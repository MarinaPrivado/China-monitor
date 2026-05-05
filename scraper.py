import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def fetch_with_requests(url, timeout=30):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  [requests] Falha em {url}: {e}")
        return None


def fetch_with_playwright(url, timeout=30000):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"  [playwright] Falha em {url}: {e}")
        return None


def scrape_site(site_config):
    name = site_config["name"]
    url = site_config["url"]
    print(f"\n[SCRAPER] Scrapeando: {name}")
    print(f"  URL: {url}")

    html = fetch_with_requests(url)
    if not html:
        html = fetch_with_playwright(url)
    if not html:
        print(f"  [ERRO] Não foi possível acessar {url}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    today = datetime.now().strftime("%Y-%m-%d")
    site_dir = os.path.join(RAW_DIR, today)
    os.makedirs(site_dir, exist_ok=True)
    safe_name = name.replace(" ", "_").replace("/", "_").lower()
    raw_path = os.path.join(site_dir, f"{safe_name}.html")
    text_path = os.path.join(site_dir, f"{safe_name}.txt")

    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(html)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"  [OK] Salvo em {raw_path}")
    return {"name": name, "url": url, "html": html, "text": text, "raw_path": raw_path}


def scrape_all(config):
    results = []
    for i, site in enumerate(config["sites"]):
        if i > 0:
            time.sleep(5)
        result = scrape_site(site)
        if result:
            results.append(result)
    return results
