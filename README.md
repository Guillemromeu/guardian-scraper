# **Pràctica 1: Tech Trends from The Guardian**

## **1. Integrants del grup**

- Víctor Olivera Begue
- Guillem Romeu Graells

---

## **2. Arxius del repositori**

Aquest repositori conté els fitxers i carpetes següents:

```
guardian_scraper_project/
├── data/
│   └── guardian_articles.csv     # Fitxer CSV generat amb els articles extrets
├── src/
│   └── guardian_scraper.py       # Script Python per fer l'scraping
├── LICENSE                       # Llicència ODbL per al dataset
├── README.md                     # Aquest document
└── requirements.txt              # Fitxer amb les dependències del projecte
```

---

## **3. Ús del codi**

Per executar l'script i generar el dataset:

1. Assegura't que tens instal·lat **Python 3.8 o superior**.
2. Instal·la les llibreries necessàries:
```bash
pip install -r requirements.txt
```
3. Executa el script principal:
```bash
python src/guardian_scraper.py
```

Aquest script:

- Accedeix a la secció de tecnologia de The Guardian.
- Filtra i selecciona articles rellevants.
- Extreu títol, data de publicació, autor/a, resum i URL.
- Desa les dades a `data/guardian_articles.csv`.

No admet paràmetres externs per línia de comandament. L'execució és automàtica.

---

## **4. DOI del dataset**

📄 Dataset publicat a Zenodo: DOI 10.5281/zenodo.15170520

---

## **5. Descripció del projecte**

Aquest projecte correspon a la Pràctica 1 de l’assignatura *Tipologia i cicle de vida de les dades* del Màster en Ciència de Dades (UOC). El seu objectiu és construir un conjunt de dades a partir de notícies de la secció *Technology* del diari The Guardian.

---

## **6. Requisits**

### Llibreries necessàries

- `requests`
- `beautifulsoup4`
- `pandas`

Instal·lació:

```bash
pip install -r requirements.txt
```

---

## **7. Verificació de l'estil del codi**

Pots verificar que el codi segueix l’estil PEP8 amb `pylint`:

```bash
pylint src/guardian_scraper.py
```

---

## **8. Llicència**

**Open Database License (ODbL) v1.0**  
http://opendatacommons.org/licenses/odbl/1.0/

Consulta el fitxer `LICENSE` per al text complet.
