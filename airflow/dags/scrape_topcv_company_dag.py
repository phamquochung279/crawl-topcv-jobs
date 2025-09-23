from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'scrape_topcv_company_daily',
    default_args=default_args,
    description='Chạy script scrape_topcv_company.py mỗi ngày 8h sáng GMT+7',
    schedule_interval='0 1 * * *',  # 1h UTC = 8h sáng GMT+7
    start_date=datetime(2025, 9, 22),
    catchup=False,
) as dag:
    run_script = BashOperator(
        task_id='run_scrape_topcv_company',
        bash_command='cd /opt/airflow && python scripts/scrape_topcv_company.py',
    )