import json
from pathlib import Path
import statistics
import shutil
import tempfile
import time
import numpy as np
import pandas as pd
import psutil
from pydantic import BaseModel,Field,model_validator
from sklearn.ensemble import IsolationForest
from labcore.runtime import AppleContainer


class Experiment(BaseModel):
    cpus:int=Field(default=1,ge=1,le=4)
    memoryMb:int=Field(default=256,ge=256,le=2048)
    repeats:int=Field(default=3,ge=1,le=10)
    durationSeconds:int=Field(default=3,ge=2,le=20)
    allocationMb:int=Field(default=64,ge=8,le=128)
    sampleIntervalSeconds:float=Field(default=.5,ge=.2,le=2)
    anomalyContamination:float=Field(default=.05,gt=0,le=.25)
    @model_validator(mode="after")
    def memory(self):
        if self.allocationMb>=self.memoryMb/2: raise ValueError("Allocation must leave at least half the VM memory for the OS")
        return self


def normalize_stats(payload):
    if isinstance(payload,list):
        if not payload: raise ValueError("Empty statistics response")
        payload=payload[0]
    if "memoryUsageBytes" not in payload:
        raise ValueError("Unrecognized runtime statistics schema: missing memoryUsageBytes")
    return {k:int(payload[k]) for k in ["memoryUsageBytes","cpuUsageUsec","networkRxBytes","networkTxBytes","blockReadBytes","blockWriteBytes"] if k in payload}


def run_probe(root:Path,config,kind="memory",contended=False):
    c=Experiment.model_validate(config)
    if kind not in {"memory","cpu","idle"}: raise ValueError("Unknown workload")
    runtime=AppleContainer()
    runs=[]
    for repeat in range(c.repeats):
        name=runtime.name("probe")
        neighbor=runtime.name("neighbor")
        staging=tempfile.TemporaryDirectory(prefix="lab-probe-")
        shutil.copy2(root/"workloads/probe.py",Path(staging.name)/"probe.py")
        try:
            if contended:
                r=runtime.call(["run","-d","--name",neighbor,"--cpus",str(c.cpus),"--memory",f"{c.memoryMb}m","--network","none",
                                "--volume",f"{staging.name}:/work:ro","python:3.12-slim","python","/work/probe.py","cpu","45","8"])
                if r.returncode: raise RuntimeError(r.stderr)
            start=time.perf_counter()
            r=runtime.call(["run","-d","--name",name,"--cpus",str(c.cpus),"--memory",f"{c.memoryMb}m","--network","none",
                            "--volume",f"{staging.name}:/work:ro","python:3.12-slim","python","/work/probe.py",kind,str(c.durationSeconds),str(c.allocationMb)])
            if r.returncode: raise RuntimeError(r.stderr)
            ready=None
            for _ in range(60):
                log=runtime.call(["logs",name],timeout=3)
                if "READY" in log.stdout:
                    ready=time.perf_counter(); break
                time.sleep(.1)
            if ready is None: raise RuntimeError("Probe did not announce readiness")
            samples=[]
            while time.perf_counter()-ready<c.durationSeconds:
                stats=runtime.call(["stats","--format","json","--no-stream",name],timeout=5)
                if stats.returncode==0:
                    try:
                        row=normalize_stats(json.loads(stats.stdout))
                        row.update({"elapsed_s":time.perf_counter()-ready,"host_used_bytes":psutil.virtual_memory().used})
                        samples.append(row)
                    except (ValueError,KeyError,json.JSONDecodeError):
                        # A process may finish between readiness and stats; preserve the gap.
                        pass
                time.sleep(c.sampleIntervalSeconds)
            logs=runtime.call(["logs",name],timeout=5).stdout
            guest={}
            for line in logs.splitlines():
                if line.startswith("{"):
                    guest.update(json.loads(line))
            runs.append({"repeat":repeat,"startup_ms":(ready-start)*1000,"samples":samples,"guest":guest,
                         "stats_observed":bool(samples),"contended":contended})
        finally:
            runtime.cleanup(name)
            if contended: runtime.cleanup(neighbor)
            staging.cleanup()
    starts=[r["startup_ms"] for r in runs]
    return {"mode":"live Apple Container measurements","kind":kind,"config":c.model_dump(),"runs":runs,
            "summary":{"startup_median_ms":statistics.median(starts),"startup_max_ms":max(starts),
                       "samples":sum(len(r["samples"]) for r in runs),"contended":contended},
            "measurement_notes":["Startup includes CLI and workload readiness, with a cached image expected.",
                                 "host_used_bytes measures the entire Mac, not this VM's attributable memory.",
                                 "guest_peak_rss_bytes is a high-water mark and will not fall after free.",
                                 "A short run may produce no runtime stats; absence is reported, never replaced by zero."]}


def anomaly_analysis(frame,contamination=.05):
    if "value" not in frame: raise ValueError("Expected a numeric value column")
    numeric=pd.to_numeric(frame["value"],errors="coerce")
    if len(numeric)<30 or not np.isfinite(numeric).all(): raise ValueError("Provide at least 30 finite numeric values")
    if len(numeric)>100000: raise ValueError("Maximum 100,000 observations")
    train_size=max(20,int(len(numeric)*.6))
    model=IsolationForest(n_estimators=100,contamination=contamination,random_state=42,n_jobs=1)
    model.fit(numeric.iloc[:train_size].to_numpy().reshape(-1,1))
    result=frame.copy()
    result["score"]=-model.score_samples(numeric.to_numpy().reshape(-1,1))
    result["flagged"]=model.predict(numeric.to_numpy().reshape(-1,1))==-1
    result["split"]=["reference" if i<train_size else "evaluation" for i in range(len(result))]
    report={"mode":"Isolation Forest exploratory analysis","training_rows":train_size,"evaluation_rows":len(result)-train_size,
            "flagged_evaluation":int(result.iloc[train_size:]["flagged"].sum()),"rows":result.to_dict(orient="records"),
            "note":"Anomaly scores identify unusual values relative to the reference window; they are not incident labels."}
    if "expected_anomaly" in result:
        test=result.iloc[train_size:]
        truth=test["expected_anomaly"].astype(bool)
        predicted=test["flagged"]
        tp=int((truth & predicted).sum())
        report["precision"]=tp/int(predicted.sum()) if predicted.sum() else 0
        report["recall"]=tp/int(truth.sum()) if truth.sum() else 0
    return report


def demo_series():
    rng=np.random.default_rng(42)
    values=rng.normal(10,1,100)
    values[80:88]=np.arange(80,88)
    return pd.DataFrame({"timestamp":range(100),"value":values,"expected_anomaly":[80<=i<88 for i in range(100)]})
