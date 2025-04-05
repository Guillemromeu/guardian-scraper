# Si no tens instal·lades aquestes llibreries, executa: 
# !pip install requests beautifulsoup4 pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

BASE_URL = "https://www.theguardian.com"
SECTION_URL = "https://www.theguardian.com/uk/technology"

# 1) OBTENIR LA PÀGINA PRINCIPAL
resp = requests.get(SECTION_URL, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

# --------------------------------------------
#  FUNCIONS D'ANÀLISI DE SECCIONS
# --------------------------------------------

def get_articles_from_section(section, label_section=""):
    """
    Dada una <section>, localitza els <a> que tenen un link rellevant
    i un títol (via aria-label o text).
    Retorna una llista de diccionaris amb la info bàsica.
    """
    articles = []

    a_tags = section.find_all("a", href=True)

    for a in a_tags:
        link = a["href"]

        if not link.startswith("/"):
            continue

        full_url = BASE_URL + link

        title = a.get("aria-label", "").strip()
        if not title:
            title = a.get_text(strip=True)

        if not title:
            continue

        articles.append({
            "section_type": label_section,
            "headline": title,
            "url": full_url
        })

    return articles

# --------------------------------------------
# 2) LOCALITZAR LES SECCIONS QUE T’INTERESSEN
# --------------------------------------------

all_sections = soup.find_all("section")
articles_info = []

for sec in all_sections:
    data_link_name = sec.get("data-link-name", "")
    data_component = sec.get("data-component", "")

    if any(keyword in data_link_name.lower() for keyword in ["technology", "spotlight", "smartphone", "review"]):
        label = data_link_name or data_component
        articles = get_articles_from_section(sec, label_section=label)
        articles_info.extend(articles)

# --------------------------------------------
# 3) ACCEDIR ALS ARTICLES PER EXTREURE AUTOR, DATA, ETC.
# --------------------------------------------

extended_articles_data = []

for item in articles_info:
    article_url = item["url"]
    section_type = item["section_type"]
    headline = item["headline"]

    try:
        print(f"Processant article: {article_url}")
        article_resp = requests.get(article_url, headers=headers)
        article_soup = BeautifulSoup(article_resp.text, 'html.parser')

        # AUTOR
        author_tag = article_soup.find("a", rel="author")
        author = author_tag.get_text(strip=True) if author_tag else None

        # DATA
        time_tag = article_soup.find("time")
        pub_date = time_tag.get("datetime") if time_tag else "Not available"

        # SUBTÍTOL
        meta_subtitle = article_soup.find("meta", attrs={"name": "description"})
        subtitle = meta_subtitle.get("content") if meta_subtitle else None

        extended_articles_data.append({
            "section_type": section_type,
            "headline": headline,
            "subtitle": subtitle,
            "url": article_url,
            "author": author,
            "publication_date": pub_date
        })

        time.sleep(1)  # Evitar saturar el servidor

    except Exception as e:
        print(f"Error processant {article_url}: {e}")

# 4) CREAR UN DATAFRAME I MOSTRAR ELS RESULTATS
df = pd.DataFrame(extended_articles_data)
print(f"Articles trobats: {len(df)}")
df.head(10)

# Assegura que la carpeta 'data' existeix
output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(output_dir, exist_ok=True)

# Desa els resultats a un arxiu CSV dins la carpeta 'data'
output_path = os.path.join(output_dir, 'guardian_articles.csv')
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Resultats desats a: {output_path}")

