import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class AnomalyStore:
    def __init__(self):
        if SUPABASE_URL and SUPABASE_KEY:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        else:
            self.client = None
            print("Warning: Supabase credentials not found in environment.")

    def insert_anomalies(self, df):
        """
        Takes a pandas DataFrame of anomalies, converts it to a list of dicts,
        and pushes to the Supabase anomalies table.
        """
        if not self.client:
            print("Cannot push anomalies: Supabase client not initialized.")
            return
            
        if df.empty:
            return

        # Prepare records for insertion
        records = []
        for index, row in df.iterrows():
            record = {
                "timestamp": index.isoformat(),
                "hits": int(row.get("hits", 0)),
                "unique_ips": int(row.get("unique_ips", 0)),
                "err_4xx_pct": float(row.get("err_4xx_pct", 0.0)),
                "err_5xx_pct": float(row.get("err_5xx_pct", 0.0)),
                "avg_size": float(row.get("avg_size", 0.0))
            }
            records.append(record)

        try:
            response = self.client.table("anomalies").insert(records).execute()
            print(f"Pushed {len(records)} anomalies to Supabase.")
            return response.data
        except Exception as e:
            print(f"Error pushing to Supabase: {e}")

# Global instance for easy importing
store = AnomalyStore()
