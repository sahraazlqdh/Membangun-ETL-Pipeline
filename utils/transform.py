import pandas as pd

def clean_and_transform(df):
    try:
        df = df.copy()

        # Hapus baris invalid
        df = df[df["Title"] != "Unknown"]
        df = df[df["Rating"] != "Invalid"]
        df = df[df["Price"] != "Unavailable"]

        # Hapus duplikat dan null
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

        # Konversi kolom
        df["Price"] = df["Price"].replace(r"[\$,]", "", regex=True).astype(float) * 16000
        df["Rating"] = df["Rating"].astype(str).str.extract(r"(\d+\.\d+)").astype(float)
        df.dropna(subset=["Rating"], inplace=True)
        df["Colors"] = df["Colors"].astype(str).str.extract(r"(\d+)").astype(int)
        df["Size"] = df["Size"].astype(str)
        df["Gender"] = df["Gender"].astype(str)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

        return df
    except Exception as e:
        print(f"[Transform Error] {e}")
        return pd.DataFrame()  # Return kosong jika gagal
