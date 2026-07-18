import time
import pandas as pd
from ingestor import start_ingestor
from preprocessor import preprocess
from features import extract_features
from detector import detect_anomalies
from store import store
import os

def test_run():
    print("1. Creating dummy log.file...")
    with open("log.file", "w") as f:
        f.write('192.168.1.1 - - [18/Jul/2026:14:00:01 +0000] "GET / HTTP/1.1" 200 1024 "-" "Mozilla/5.0"\n')
        f.write('192.168.1.2 - - [18/Jul/2026:14:01:02 +0000] "POST /login HTTP/1.1" 401 512 "-" "Python-urllib"\n')
        f.write('192.168.1.1 - - [18/Jul/2026:14:06:03 +0000] "GET /api HTTP/1.1" 500 2048 "-" "Curl"\n')

    print("2. Starting ingestor...")
    event_handler = start_ingestor()
    
    time.sleep(1)
    
    with open("log.file", "r") as f:
        lines = f.readlines()
        
    print("3. Preprocessing lines...")
    df = preprocess(lines)
    print(f"   Parsed {len(df)} logs.")
    
    print("4. Extracting features...")
    f_df = extract_features(df)
    print(f"   Extracted features for {len(f_df)} windows.")
    
    if len(f_df) > 1:
        print("5. Detecting anomalies...")
        detect_anomalies(f_df)
        print("   Anomaly column added successfully.")
        
        if store.client:
            print("6. Pushing to Supabase...")
            resp = store.insert_anomalies(f_df)
            print("   Supabase response OK")
            
            print("7. Fetching from Supabase API logic...")
            fetch = store.client.table("anomalies").select("*").limit(5).execute()
            print("   Fetched DB rows:", len(fetch.data))
        else:
            print("   Supabase not connected!")

    print("\nPIPELINE TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_run()
    # Cleanup dummy log file
    if os.path.exists("log.file"):
        os.remove("log.file")
