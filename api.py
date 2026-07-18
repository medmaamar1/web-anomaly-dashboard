from fastapi import FastAPI, HTTPException
from store import store
import pandas as pd

app = FastAPI(title="Real-Time Web Detection API", version="1.0.0")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "web-anomaly-detection-api"}

@app.get("/health")
def health_check():
    supabase_status = "connected" if store.client else "disconnected"
    return {"status": "healthy", "supabase": supabase_status}

@app.get("/anomalies/recent")
def get_recent_anomalies(limit: int = 50):
    """
    Fetch the most recent anomalies detected by the ML pipeline.
    """
    if not store.client:
        raise HTTPException(status_code=503, detail="Supabase connection not configured.")
        
    try:
        response = store.client.table("anomalies").select("*").order("timestamp", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
