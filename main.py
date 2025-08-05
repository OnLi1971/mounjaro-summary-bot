import openai
import gspread
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Nastavení API klíče
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ověření přístupu ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1KgrYXHpVfTAGQZT6f15aARGCQ-qgNQZM4HWQCiqt14s").sheet1

# Přejdeme řádky a zpracujeme nový článek
rows = sheet.get_all_records()
for idx, row in enumerate(rows, start=2):
    url = row.get("D") or row.get("URL") or row.get("Url")  # podpora různých názvů sloupců
    if not url:
        continue

    # Pokud už je ve sloupci F shrnutí, přeskočíme
    summary = sheet.cell(idx, 6).value
    if summary:
        continue

    # Načtení obsahu článku z URL
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text() for p in paragraphs)
    except Exception as e:
        sheet.update_cell(idx, 6, f"Chyba načítání: {e}")
        continue

    # Shrnutí pomocí OpenAI
    try:
        prompt = f"Vytvoř mi stručný výtah v bodech v češtině z následujícího článku:

{content[:6000]}"
        result = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jsi AI asistent specializovaný na shrnutí článků do češtiny."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        summary_text = result["choices"][0]["message"]["content"]
        sheet.update_cell(idx, 6, summary_text)
    except Exception as e:
        sheet.update_cell(idx, 6, f"Chyba AI: {e}")
