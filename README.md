# ETL Pipeline Sederhana — Fashion Data

Proyek ini adalah implementasi **ETL (Extract, Transform, Load) Pipeline** sederhana menggunakan Python. Pipeline ini bertugas mengekstrak data fashion dari web, mentransformasikannya, lalu memuat hasilnya ke CSV, PostgreSQL, dan Google Sheets.

---

## 📌 Fitur

- ✅ Web scraping dari `https://fashion-studio.dicoding.dev/`
- ✅ Transformasi data: konversi harga, validasi rating, formatting timestamp
- ✅ Penyimpanan hasil ke:
  - CSV (`fashion_data.csv`)
  - PostgreSQL (tabel `fashion_products`)
  - Google Spreadsheet (opsional)
- ✅ Unit testing lengkap (pytest)
- ✅ Coverage testing ≥ 99%

---

## ▶️ Cara Menjalankan

### 1. Aktifkan Virtual Environment

```
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install Dependensi
```
pip install -r requirements.txt
```
### 3. Jalankan Script ETL (opsional)
Jika memiliki file main.py sebagai entry point:
```
python main.py
```
### 🧪 Menjalankan Unit Test
```
coverage run -m pytest tests
coverage report -m
```
