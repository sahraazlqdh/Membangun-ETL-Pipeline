import pandas as pd
from utils.extract import get_fashion_data
from utils.transform import clean_and_transform
from utils.load import load_data

def run_pipeline():
    try:
        print("[INFO] Memulai proses ETL...")

        raw_items = get_fashion_data(page_limit=50)
        if not raw_items:
            print("[WARNING] Tidak ada data yang berhasil diambil. ETL dihentikan.")
            return

        df_raw = pd.DataFrame(raw_items)
        print(f"[INFO] Jumlah data mentah: {len(df_raw)}")

        print("\n[INFO] Preview data sebelum transformasi:")
        print(df_raw.head())

        cleaned_df = clean_and_transform(df_raw)
        print(f"[INFO] Data setelah transformasi: {len(cleaned_df)} entri")

        print("\n[INFO] Preview data setelah transformasi:")
        print(cleaned_df.head())

        load_data(cleaned_df)
        print("[SUCCESS] Proses ETL selesai.")

    except Exception as err:
        print(f"[ERROR] Kesalahan pada proses utama: {err}")

if __name__ == '__main__':
    run_pipeline()
