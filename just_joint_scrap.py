import json
import time
import re
import os
from seleniumbase import SB
from bs4 import BeautifulSoup

# def scraper_get():
#     with SB(uc=True) as sb:

#         url = f"https://justjoin.it/job-offers/all-locations/python?experience-level=junior&orderBy=DESC&sortBy=published&from=0"
#         sb.driver.uc_open_with_reconnect(url,6)

#         time.sleep(5)

#         html_content = sb.get_page_source()
    
#         # Saving data
#         file_path = os.path.join('Just_joint_scrap', f"Just_joint_scrap.html")
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(html_content)
        
#         # soup = BeautifulSoup(html_content,'html.parser')

#         print(f"Download JustJoint")

# scraper_get()


import requests

url = "https://justjoin.it/api/offers"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://justjoin.it/",
}

response = requests.get(url, headers=headers)
print("URL:", url)
print("Nagłówki:", headers)
print("Status:", response.status_code)
print("Treść:", response.text)
if response.status_code == 200:
    offers = response.json()
    print(f"Znaleziono {len(offers)} ofert.")
    print("Przykład:", offers[0]["title"])
else:
    print("Błąd:", response.status_code)