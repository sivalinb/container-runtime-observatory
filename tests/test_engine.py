import numpy as np
import pandas as pd
import pytest
from engine import anomaly_analysis,demo_series,normalize_stats,Experiment

def test_stats_preserve_real_units():
    r=normalize_stats([{'memoryUsageBytes':1024,'cpuUsageUsec':2000000,'networkRxBytes':0}])
    assert r['memoryUsageBytes']==1024
    assert r['cpuUsageUsec']==2000000

def test_unknown_stats_never_become_zero():
    with pytest.raises(ValueError): normalize_stats({'unrecognized':42})

def test_empty_stats_rejected():
    with pytest.raises(ValueError): normalize_stats([])

def test_anomalies_evaluated_on_held_out_window():
    r=anomaly_analysis(demo_series())
    assert r['training_rows']==60
    assert r['evaluation_rows']==40
    assert r['recall']>=.75

def test_detector_reproducible():
    assert anomaly_analysis(demo_series())==anomaly_analysis(demo_series())

@pytest.mark.parametrize('values',[[1]*10,[float('nan')]*40,[float('inf')]*40])
def test_bad_series_rejected(values):
    with pytest.raises(ValueError): anomaly_analysis(pd.DataFrame({'value':values}))

def test_memory_headroom_enforced():
    with pytest.raises(ValueError): Experiment(allocationMb=128,memoryMb=256)
