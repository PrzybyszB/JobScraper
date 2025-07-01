from airflow.models import Variable
from dotenv import load_dotenv

env_vars = load_dotenv(".env")
for key, value in env_vars.items():
    Variable.set(key, value)
    print(f"Airflow Variable is set correctly : {key}")