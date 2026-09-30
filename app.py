from pathlib import Path
import pandas as pd
import streamlit as st
from labcore.config import load_config
from labcore.observability import Recorder
from labcore.ui import header,evidence,sources_panel,ai_panel,docs_panel
from engine import run_probe,anomaly_analysis,demo_series

ROOT=Path(__file__).resolve().parent
config,meta=load_config(ROOT)
header("Container Runtime Observatory","Look below the application: startup, memory, contention, and unusual behavior.",meta)

@st.cache_resource
def recorder(): return Recorder(ROOT,"container-runtime-observatory")

tabs=st.tabs(["VM experiment","Anomaly analysis","Evidence","AI reviewer","Public sources","Guide"])
with tabs[0]:
    kind=st.selectbox("Workload",["memory","cpu","idle"])
    a,b,c=st.columns(3)
    config["cpus"]=a.number_input("CPUs",1,4,config["cpus"])
    config["memoryMb"]=b.selectbox("Memory MiB",[256,512,1024,2048])
    config["repeats"]=c.number_input("Independent repeats",1,10,config["repeats"])
    contended=st.checkbox("Run a neighboring CPU workload")
    if st.button("Run live VM experiment",type="primary"):
        try:
            with recorder().span("runtime_probe",mode="live"):
                report=run_probe(ROOT,config,kind,contended)
                report["config_provenance"]=meta
                recorder().save(report)
                st.session_state["report"]=report
        except Exception as e: st.error(str(e))
    if st.session_state.get("report",{}).get("runs"):
        report=st.session_state["report"]
        a,b,c=st.columns(3)
        a.metric("Median startup",f'{report["summary"]["startup_median_ms"]:.0f} ms')
        b.metric("Runs",len(report["runs"]))
        c.metric("Resource samples",report["summary"]["samples"])
        for r in report["runs"]:
            st.caption(f'Repeat {r["repeat"]+1} · readiness {r["startup_ms"]:.0f} ms')
            if r["samples"]:
                frame=pd.DataFrame(r["samples"])
                st.line_chart(frame.set_index("elapsed_s")[["memoryUsageBytes"]])
            st.json(r["guest"])
with tabs[1]:
    source_mode=st.radio("Time series",["Labeled synthetic fixture","Uploaded CSV","Fetched public source"],horizontal=True)
    upload=st.file_uploader("CSV with value column",type=["csv"])
    if st.button("Analyze anomalies"):
        try:
            if source_mode=="Uploaded CSV":
                if not upload: raise ValueError("Upload a CSV first")
                frame=pd.read_csv(upload)
            elif source_mode=="Fetched public source":
                source=st.session_state.get("source_result")
                if not source or source["id"] not in {"nab-taxi","nab-cpu"}: raise ValueError("Fetch a NAB source first")
                frame=pd.read_csv(source["local_path"])
            else: frame=demo_series()
            with recorder().span("anomaly_analysis",mode=source_mode):
                report=anomaly_analysis(frame,config["anomalyContamination"])
                report["source_mode"]=source_mode
                recorder().save(report,"anomaly")
                st.session_state["anomaly"]=report
        except Exception as e: st.error(str(e))
    if "anomaly" in st.session_state:
        report=st.session_state["anomaly"]
        st.metric("Flagged evaluation observations",report["flagged_evaluation"])
        st.line_chart(pd.DataFrame(report["rows"])[["value"]])
        st.dataframe(pd.DataFrame(report["rows"]).query("flagged"),hide_index=True)
        st.caption(report["note"])
        evidence(report)
with tabs[2]: evidence(st.session_state.get("report"))
with tabs[3]: ai_panel(ROOT,st.session_state.get("report") or st.session_state.get("anomaly"))
with tabs[4]: sources_panel(ROOT)
with tabs[5]: docs_panel(ROOT)
