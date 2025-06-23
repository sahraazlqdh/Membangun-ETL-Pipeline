import time
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import RequestException, ConnectTimeout

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetch_html_content(url, retries=3, delay=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.content
        except (RequestException, ConnectTimeout) as err:
            print(f"[FETCH ERROR] Percobaan ke-{attempt} gagal: {err}")
            if attempt < retries:
                print(f"[RETRY] Menunggu {delay} detik sebelum mencoba lagi...")
                time.sleep(delay)
            else:
                print(f"[FAILED] Gagal mengambil konten dari {url} setelah {retries} kali percobaan.")
                return None

def parse_product_details(card):
    try:
        title_tag = card.select_one('h3.product-title')
        title = title_tag.text.strip() if title_tag and title_tag.text.strip() else "Unknown"

        price_box = card.find('div', class_='price-container')
        price = price_box.text.strip() if price_box else "Unavailable"

        details = card.find_all('p')

        def get_detail_text(label, regex, fallback):
            for p in details:
                if label in p.text:
                    match = re.search(regex, p.text)
                    if match:
                        return match.group(1).strip()
            return fallback

        rating = get_detail_text("Rating", r"Rating:\s*⭐\s*(\d+(?:\.\d+)?)", "Invalid")
        colors = get_detail_text("Colors", r"(\d+)\s*Colors", "0")
        size = get_detail_text("Size", r"Size:\s*(\w+)", "Unknown")
        gender = get_detail_text("Gender", r"Gender:\s*(\w+)", "Unknown")
        timestamp = datetime.now().isoformat()

        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "Timestamp": timestamp
        }
    except Exception as err:
        print(f"[PARSE ERROR] {err}")
        return None

def get_fashion_data(page_limit=50, pause=1.5):
    records = []
    for page in range(1, page_limit + 1):
        url = "https://fashion-studio.dicoding.dev/" if page == 1 else f"https://fashion-studio.dicoding.dev/page{page}"
        print(f"[SCRAPING] Mengakses {url}")
        html = fetch_html_content(url)

        if not html:
            print("[STOP] Konten tidak tersedia. Menghentikan scraping.")
            break

        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('.collection-card')

        if not cards:
            print(f"[INFO] Tidak ada kartu produk di halaman {page}.")
            continue

        for card in cards:
            item = parse_product_details(card)
            if item:
                records.append(item)

        time.sleep(pause)

    return records
