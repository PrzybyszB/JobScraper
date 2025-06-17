import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import os

def extract(file):
    with open(file, 'r', encoding='utf-8') as f:
        offers = json.load(f)
    return offers

def transform(offers):
    
    cleaned_df = []
    
    for offer in offers:
        cleaned_df.append({
        "job_title": offer['offer_job_title'],
        "company" : offer['offer_company_name'],
        "city" : offer['offer_city'],
        "description" : offer['offer_description'],
        "technologies" : json.loads(offer['offer_technologies']),
        "position_level" : json.loads(offer['offer_position_level']),
        "contract" : json.loads(offer['offer_contract']),
        "model_work" : json.loads(offer['offer_model_work']),
        "exp_date": datetime.strptime(offer['offer_exp_date'][:10], "%Y-%m-%d").date(),
        "url" : offer['offer_link'],

    })
    
    return pd.DataFrame(cleaned_df)

def load(cleaned_df):
    
    user = 'job_scrap_user'
    password = 'job_scrap_password'
    host = 'localhost'
    port = 5432
    db = 'job_scrap_db'

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
    cleaned_df.to_csv("cleaned_pracuj_offers.csv")
    cleaned_df.to_sql("offers", engine)
    print("Data was successffully saved to DB and as csv")


file = "./Pracuj_scrap/pracuj_offer.json"

offers = extract(file)
cleaned_df = transform(offers)
load(cleaned_df)
