import pandas as pd
from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def save_to_csv(df, filename="fashion_data.csv"):
    try:
        df.to_csv(filename, index=False)
        print(f"[CSV] Data disimpan di {filename}")
    except Exception as e:
        print(f"[CSV Error] Gagal menyimpan data ke CSV: {e}")

def save_to_postgresql(df, db_name="fashion_db", user="postgres", password="pass", host="localhost", port="5432"):
    try:
        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
        df.to_sql("fashion_products", engine, index=False, if_exists="replace")
        print("[PostgreSQL] Data disimpan di tabel fashion_products")
    except Exception as e:
        print(f"[PostgreSQL Error] {e}")

def save_to_google_spreadsheet(df, spreadsheet_id, range_name="Sheet1!A1", credential_file="client_secret.json"):
    try:
        credentials = Credentials.from_service_account_file(credential_file)
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        data = [df.columns.tolist()] + df.astype(str).values.tolist()

        sheet.values().clear(spreadsheetId=spreadsheet_id, range=range_name).execute()
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": data}
        ).execute()
        print("[Google Sheets] Data berhasil ditulis ke spreadsheet.")
    except Exception as e:
        print(f"[Google Sheets Error] {e}")

def load_data(
    df,
    spreadsheet_id=None,
    range_name="Sheet1!A1",
    credential_file="client_secret.json",
    use_postgres=True
):
    save_to_csv(df)

    if use_postgres:
        save_to_postgresql(df)

    if spreadsheet_id:
        save_to_google_spreadsheet(
            df,
            spreadsheet_id=spreadsheet_id,
            range_name=range_name,
            credential_file=credential_file
        )
