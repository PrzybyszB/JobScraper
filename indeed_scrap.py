import json
import time
import re
import os
from seleniumbase import SB
from bs4 import BeautifulSoup

# https://pl.indeed.com/jobs?q=Python+Junior&start=0/viewjob?jk=f15a7bba125c3772&from=vjs&tk=1in74njr1j0hj803&viewtype=embedded&xkcb=SoCa67M30nBRpHzm9h0YbzkdCdPP&continueUrl=%2Fjobs%3Fq%3DPython%2BJunior%26start%3D0

def scraper_get(start_page, end_page=10):
    with SB(uc=True) as sb:
        for page in range(start_page, end_page +1):
            url = f"https://pl.indeed.com/jobs?q=Python+Junior&start={page*10}"
            sb.driver.uc_open_with_reconnect(url,6)

            time.sleep(5)

            html_content = sb.get_page_source()
        
            # Saving data
            file_path = os.path.join('Indeed_scrap', f"indeed_scrap_{page}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # soup = BeautifulSoup(html_content,'html.parser')

            print(f"Download Indeed {page}/{end_page}")
            
def scraper_cache():
    try:
        folder_path = 'Indeed_scrap'
        pages = os.listdir(folder_path)
        all_offers = []

        for page in pages:
            if page.endswith('.html'):
                page_path = os.path.join(folder_path, page)
                print(f"Processing file: {page}")
                with open(page_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Find tag script with id='mosaic-data'
                script_tag = soup.find('script', {'id':'mosaic-data'})

                if script_tag:
                    script_text = script_tag.get_text()

                    # Regex to extract data
                    pattern = r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=s*({.*"providerId":"mosaic-provider-jobcards","uiVariant":null});'
                    match = re.search(pattern, script_text, re.DOTALL)
                    if match:
                        offers = json.loads(match[1])

                        for offer in offers['metaData']['mosaicProviderJobCardsModel']['results']:
                            offer_title = offer.get('title', 'No Data')
                            string_offer = str(offer_title)
                            keywords = [r'\bjunior\b', r'\bmlodszy\b', r'\bmłodszy\b']

                            # Check if any keyword matches the offer title
                            if any(re.search(keyword, string_offer, re.IGNORECASE) for keyword in keywords):
                                offer_id = offer.get('jobkey', 'No Data')

                                # Expiration date logic (30 days)
                                exp_date = offer.get('createDate', 0) + 2592000000  # Zabezpieczenie na datach
                                snippet = offer.get('snippet', None)
                                offer_desc = 'No Data'
                                if snippet:
                                    pattern = r'<li>(.*?)</li>'
                                    match = re.search(pattern, snippet, re.DOTALL)
                                    if match:
                                        offer_desc = match[1]

                                offer_link = f"https://pl.indeed.com/viewjob?jk={offer_id}"

                                json_offer = {
                                    "offer_technologies": offer.get('jobSeekerMatchSummaryModel', {}).get('sortedMisMatchingEntityDisplayText', 'No Data'),
                                    "offer_job_title": offer_title,
                                    "offer_company_name": offer.get('moreLinks', {}).get('companyName', 'No Data'),
                                    "offer_exp_date": exp_date,
                                    "offer_description": offer_desc,
                                    "offer_link": offer_link,
                                    "offer_city": offer.get('moreLinks', {}).get('locationName', 'No Data'),
                                }

                                # Add condition to replace None values with 'No Data'
                                for key, value in json_offer.items():
                                    if value is None:
                                        json_offer[key] = 'No data'

                                all_offers.append(json_offer)

                    # After processing all offers for the page, save to file
                    file_path = os.path.join('Indeed_scrap', f"indeed_offer.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(all_offers, f, ensure_ascii=False, indent=4)

        if all_offers:
            print(f"Processing completed. Total offers found: {len(all_offers)}")
        else:
            print("No offers matching the keywords were found.")

    except Exception as e:
        print(f"Error occurred: {e}")



# scraper_get(0,10)
scraper_cache()
