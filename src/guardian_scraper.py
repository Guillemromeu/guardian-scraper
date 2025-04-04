import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

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

        author_tag = article_soup.find("a", rel="author")
        author = author_tag.get_text(strip=True) if author_tag else None

        time_tag = article_soup.find("time")
        pub_date = time_tag.get("datetime") if time_tag else None

        body_div = article_soup.find("div", class_="content__article-body")
        if body_div:
            p_tags = body_div.find_all("p")
            summary = p_tags[0].get_text(strip=True) if p_tags else None
        else:
            summary = None

        extended_articles_data.append({
            "section_type": section_type,
            "headline": headline,
            "url": article_url,
            "author": author,
            "publication_date": pub_date,
            "summary": summary
        })

        time.sleep(1)

    except Exception as e:
        print(f"Error processant {article_url}: {e}")

df = pd.DataFrame(extended_articles_data)
print(f"Articles trobats: {len(df)}")
print(df.head(10))

import os

# Assegura que la carpeta 'data' existeix
output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(output_dir, exist_ok=True)

# Desa els resultats a un arxiu CSV dins la carpeta 'data'
output_path = os.path.join(output_dir, 'guardian_articles.csv')
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Resultats desats a: {output_path}")