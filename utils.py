import pandas as pd
from db import FileMeta, session

def get_stats(df):
    stats = {
        'shape': df.shape,
        'null_counts': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict()
    }
    return stats

def save_file_meta(filename, original_name, username, df):
    meta = FileMeta(
        filename=filename,
        original_name=original_name,
        uploaded_by=username,
        rows=df.shape[0],
        cols=df.shape[1]
    )
    session.add(meta)
    session.commit()
