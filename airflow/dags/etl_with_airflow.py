import json
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator 
from airflow.models import Variable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract(file):
    logger.info(f"Extracting data from {file}")
    with open(file, 'r', encoding='utf-8') as f:
        offers = json.load(f)
    logger.info(f"Extracted {len(offers)} offers")
    return offers

def transform(**context):
    offers = context['ti'].xcom_pull(task_ids='extract')
    print("Offers type:", type(offers))
    logger.info(f"Offers type: {type(offers)}")
    print("Offers value:", offers)
    cleaned_df = []
    for offer in offers:
        cleaned_df.append({
            "job_title": offer['offer_job_title'],
            "company": offer['offer_company_name'],
            "city": offer['offer_city'],
            "description": offer['offer_description'],
            "technologies": ', '.join(offer['offer_technologies']),
            "position_level": ', '.join(offer['offer_position_level']),
            "contract": ', '.join(offer['offer_contract']),
            "model_work": ', '.join(offer['offer_model_work']),
            "exp_date": offer['offer_exp_date'][:10], 
            "url": offer['offer_link'],
        })

    logger.info(f"Transformed {len(cleaned_df)} offers")
    return cleaned_df

def load(**context):
    cleaned_df = context['ti'].xcom_pull(task_ids='transform')
    logger.info(f"Loading {len(cleaned_df)} offers to database")
    df = pd.DataFrame(cleaned_df)

    user = 'job_scrap_user'
    password = 'job_scrap_password'
    host = 'job_scrap_db'
    port = 5432
    db = 'job_scrap_db'

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

    with engine.connect() as conn:
        conn.execute("DROP TABLE IF EXISTS offers;")
        logger.info("Dropped table offers if existed")
        
    df.to_sql("offers", engine)
    logger.info("Data was successfully saved to DB and as csv")
    print("Data was successffully saved to DB and as csv")

default_args = {
    'owner': 'airflow',
    'retires': 5,
    'retry_delay': timedelta(minutes=5),
    'sla': timedelta(minutes=20)
}

with DAG(
    default_args=default_args,
    dag_id='etl_with_airflow_V06',
    start_date=datetime(2025, 6, 22),
) as dag:

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
        op_kwargs={'file': '/opt/airflow/dags/Pracuj_scrap/pracuj_offer.json'},
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
        provide_context=True,
    )

    load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    provide_context=True,
    )

    extract_task >> transform_task >> load_task
