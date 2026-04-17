import pandas as pd
from fastapi import HTTPException

def extract_rssi_from_file(file):
    try:
        df = pd.read_csv(file.file)

        if df.empty:
            raise ValueError("Empty file")

        if "RSSI_Value_dBm" in df.columns:
            return df["RSSI_Value_dBm"].values
        else:
            return df.iloc[:, 1].values

    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format: {file.filename}"
        )