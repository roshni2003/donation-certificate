import requests
import pandas as pd
import time

# Your deployed Apps Script Web App URLs
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxublTrVVO3Of8sUJ-4M6UjXlncpS1yDe78UnpvNxDuo8o9o69xuD2XUs6Bgea1XxkI/exec"
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxublTrVVO3Of8sUJ-4M6UjXlncpS1yDe78UnpvNxDuo8o9o69xuD2XUs6Bgea1XxkI/exec"

def fetch_sheet_data():
    """Fetch all data from Google Sheet"""
    try:
        res = requests.get(SHEET_API_URL)
        res.raise_for_status()
        df = pd.DataFrame(res.json())
        print(f"Fetched {len(df)} donor rows from sheet")
        return df
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return pd.DataFrame()

def fetch_unprocessed_donors():
    """Fetch only unprocessed or new donor rows (based on unique key)."""
    df = fetch_sheet_data()
    if df.empty:
        return df

    # Generate unique key for each row
    df['ProcessedKey'] = df.apply(lambda r: f"{r['Serial_No']}_{r['Date']}_{r['Name']}", axis=1)

    # Include only rows where Processed is blank OR ProcessedKey not marked yet
    if 'Processed' in df.columns:
        unprocessed_df = df[
            (df['Processed'].isna()) |
            (df['Processed'] == '') |
            (df['Processed'] == 'NO') |
            (~df['ProcessedKey'].isin(df['ProcessedKey'].where(df['Processed'] == 'YES')))
        ]
    else:
        print("No 'Processed' column found. Processing all donors (first run).")
        unprocessed_df = df

    print(f"Unprocessed donors: {len(unprocessed_df)}")
    return unprocessed_df


def main():
    # Fetch only unprocessed donors
    df = fetch_unprocessed_donors()
    
    if df.empty:
        print("No unprocessed donors found.")
        return
    
    print(f"Processing {len(df)} unprocessed donor rows")
    
    successful = 0
    failed = 0
    
    for i, row in df.iterrows():
        try:
            # Prepare payload
            payload = {
                "Serial_No": str(row["Serial_No"]).strip(),
                "Date": str(row["Date"]).strip(),
                "Name": str(row["Name"]).strip(),
                "Address": str(row["Address"]).strip(),
                "Amount": str(row["Amount"]).strip(),
                "Amount_in_words": "INR Two Thousand Five Hundred Rupees",
                "PAN": str(row["PAN"]).strip(),
            }
            
            print(f"\n[{i+1}] Processing: {payload['Serial_No']} - {payload['Name']}")
            
            # Send request to generate PDF
            r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=60)
            
            if r.status_code == 200:
                response_data = r.json()
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS: PDF created - {response_data.get('pdfUrl', 'URL not available')}")
                    successful += 1

        # Mark as processed in sheet
                    mark_payload = {
                        "function": "markAsProcessed",
                        "serialNo": payload['Serial_No'],
                        "date": payload['Date'],
                        "name": payload['Name']
                    }
                    requests.post(APPS_SCRIPT_URL, json=mark_payload)

                else:
                    print(f"❌ ERROR: {response_data.get('message', 'Unknown error')}")
                    failed += 1

            else:
                print(f"❌ HTTP ERROR: {r.status_code}")
                if r.status_code == 429:
                    print("   ⚠️  Rate limited. Waiting 10 seconds...")
                    time.sleep(10)
                    # Retry once
                    r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=60)
                    if r.status_code == 200:
                        response_data = r.json()
                        if response_data.get('status') == 'success':
                            print(f"✅ RETRY SUCCESS: PDF created")
                            successful += 1
                        else:
                            print(f"❌ RETRY ERROR: {response_data.get('message', 'Unknown error')}")
                            failed += 1
                    else:
                        print(f"❌ RETRY FAILED: {r.status_code}")
                        failed += 1
                else:
                    failed += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(2)  # Increased delay to avoid rate limiting
            
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            failed += 1
    
    print(f"\n📊 SUMMARY: {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()