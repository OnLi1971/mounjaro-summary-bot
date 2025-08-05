# Mounjaro Novinky - AI Shrnutí článků

Tento skript každý den:
- Načte nový článek z Google Sheet (sloupec D)
- Získá obsah článku z webu
- Pošle ho do OpenAI API pro shrnutí do bodů v češtině
- Zapíše výtah do sloupce F

## Nastavení
1. Vytvoř `credentials.json` s Google Service účtem
2. Vytvoř `.env` s klíčem `OPENAI_API_KEY`
3. Nastav denní spouštění (viz GitHub Actions níže)
