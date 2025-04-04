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

    # Ex. busquem tots els <a> amb href i classe 'dcr-*' (segons els exemples)
    # o simplement tots els <a> amb href i aria-label:
    a_tags = section.find_all("a", href=True)

    for a in a_tags:
        link = a["href"]

        # Filtra enllaços interns o sense sentit
        if not link.startswith("/"):
            # The Guardian acostuma a tenir enllaços interns tipus "/technology/2025..."
            continue

        # Reconstrueix l'URL complet si cal
        full_url = BASE_URL + link

        # Títol: o bé aria-label o bé el text intern de l'etiqueta
        title = a.get("aria-label", "").strip()
        if not title:
            # Si aria-label és buit, prova amb el text
            title = a.get_text(strip=True)

        # Salta si no hi ha títol
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

# Exemples (adapta-ho al que trobis a la pàgina):
# - 'spotlight' pot aparèixer a data-link-name, data-component, etc.
# - 'smartphone reviews' pot ser a data-link-name="smartphone reviews"

# Pots buscar TOTES les <section> i després filtrar-ne algunes
all_sections = soup.find_all("section")
articles_info = []

for sec in all_sections:
    # Mira si la section té un data-link-name o data-component que t'interessa
    # Exemples: "technology", "spotlight", "smartphone reviews", "review", etc.

    data_link_name = sec.get("data-link-name", "")
    data_component = sec.get("data-component", "")

    # Comprovem si conté alguna paraula clau
    # (adapta-ho a les paraules que hagis vist: 'spotlight', 'feature', 'smartphone reviews', etc.)
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
        pub_date = time_tag.get("datetime") if time_tag else None

        # PRIMER PARÀGRAF COM A RESUM
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