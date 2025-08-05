import openai
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

openai.api_key = "YOUR_OPENAI_API_KEY"

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1KgrYXHpVfTAGQZT6f15aARGCQ-qgNQZM4HWQCiqt14s").sheet1

def extract_title_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            return h1.text.strip()
        title = soup.find("title")
        if title and title.text.strip():
            return title.text.strip()
        return "Bez nadpisu"
    except:
        return "Bez nadpisu"

def generate_summary(text):
    prompt = f"Napiš stručné shrnutí v bodech (v češtině):\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

data = []
records = sheet.get_all_records()
for row in records:
    url = row.get("URL článku") or row.get("URL") or row.get("Link") or row.get("D")
    if not url:
        continue
    title = extract_title_from_url(url)
    response = requests.get(url)
    text = BeautifulSoup(response.text, "html.parser").get_text()
    summary = generate_summary(text[:2000])
    data.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": title,
        "summary": summary,
        "url": url
    })

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
