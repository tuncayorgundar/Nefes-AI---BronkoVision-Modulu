# modules/classic_analyzer/utils/styling.py

import pandas as pd

def highlight_anomalies(s):
    """
    Pandas Styler ile 'Status' sütunundaki 'Normal' olmayan satırları renklendirir.
    """
    is_anomaly = s['Status'] != 'Normal'
    return ['background-color: #ffcccc' if is_anomaly else '' for _ in s]

def highlight_positive_results(s):
    """
    Pandas Styler ile 'Result' sütunundaki 'Pozitif' olan satırları renklendirir.
    """
    is_positive = s['Result'] == 'Pozitif'
    return ['background-color: #ffcccc' if is_positive else '' for _ in s]