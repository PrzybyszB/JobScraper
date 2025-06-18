import subprocess
import json
import requests
import time
import re
import pandas as pd

import os

# redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def login():
    output = subprocess.check_output(['sh', './pracuj_login.sh'], text=True)
    return json.loads(output.strip())

# token = login()
# print(token['accessToken'])

def get_max_page():
    url = "https://it.pracuj.pl/praca?et=1%2C17%2C4&itth=37&pn=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3'}

    response = requests.get(url, headers=headers)
    html_content = response.text

    match = re.search(r'data-test="top-pagination-max-page-number">(\d+)</span>', html_content)

    if match:
        return int(match.group(1))
    return 1

def scraper_get():
    max_page = get_max_page()

    for page in range(1, max_page + 1):
        url = "https://it.pracuj.pl/praca?et=1%2C17%2C4&itth=37&pn={page}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3'}
        
        response = requests.get(url, headers=headers)
        html_content = response.text

        # Saving data
        file_path = os.path.join('Pracuj_scrap', f"pracuj_{page}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Download page {page}/{max_page}")
        time.sleep(1)


def scraper_cache():
    #while tutaj powinien byc
    folder_path = "Pracuj_scrap"
    pages = os.listdir(folder_path)
    all_offers = []

    # for filename in os.listdir(folder_path):
    #     if filename.endswith('.html'):
    #         file_path = os.path.join(folder_path, filename)
    #         try:
    #             os.remove(file_path)
    #             print(f"Remove: {file_path}")
    #         except Exception as e:
    #             print(f"There was an error on remove file {file_path} : {e}")

    for page in pages:
        if page.endswith(".html"):
            page_path = os.path.join(folder_path, page)
            print(f"Processing file: {page_path}")
            with open(page_path, 'r', encoding="utf-8") as file:
                html = file.read()
                pattern = r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.*?)</script>'
                match = re.search(pattern,html)
                offers = json.loads(match[1])
                for offer in offers['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['groupedOffers']:
                    offer_id = offer['offers'][0]['partitionId']

                    json_offer = {
                        "offer_technologies": offer['technologies'],
                        "offer_job_title": offer['jobTitle'],
                        "offer_company_name": offer['companyName'],
                        "offer_exp_date": offer['expirationDate'],
                        "offer_description": offer['jobDescription'],
                        "offer_link": offer['offers'][0]['offerAbsoluteUri'],
                        "offer_city": offer['offers'][0]['displayWorkplace'],
                        "offer_position_level": offer['positionLevels'],
                        "offer_contract": offer['typesOfContract'],
                        "offer_model_work": offer['workModes'],
                    }

                    all_offers.append(json_offer)
                    # redis_client.hset(f'pracuj_{offer_id}', mapping=json_offer)

    if all_offers:
        file_path = os.path.join('Pracuj_scrap', f"pracuj_offer.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_offers, f, ensure_ascii=False, indent=4)
        print(f"Processing completed. Total offers found: {len(all_offers)}")
    else:
        print("There was no offer found")

scraper_get()
scraper_cache()