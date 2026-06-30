# src/api/main.py
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
import pandas as pd
from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(
    current_user: dict = Depends(get_current_user)
):
    """Trả về 10 raw patient records (chỉ admin được phép)."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    return JSONResponse(content={
        "requested_by": current_user["username"],
        "data": df.head(10).to_dict(orient="records")
    })


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(
    current_user: dict = Depends(get_current_user)
):
    """Trả về anonymized data (ml_engineer và admin được phép)."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    df_anon = anonymizer.anonymize_dataframe(df)
    return JSONResponse(content={
        "requested_by": current_user["username"],
        "data": df_anon.head(10).to_dict(orient="records")
    })


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Trả về aggregated metrics theo bệnh — không có PII."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    metrics = df.groupby("benh").agg(
        so_luong=("patient_id", "count"),
        ket_qua_tb=("ket_qua_xet_nghiem", "mean"),
    ).round(2).reset_index()
    return JSONResponse(content={
        "requested_by": current_user["username"],
        "metrics": metrics.to_dict(orient="records")
    })


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Xóa bệnh nhân theo ID (chỉ admin được phép)."""
    return JSONResponse(content={
        "message": f"Patient {patient_id} deleted",
        "deleted_by": current_user["username"]
    })


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
