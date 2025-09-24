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
    'scrape_topcv_jobs_daily',
    default_args=default_args,
    description='Chạy pipeline mỗi ngày 8h sáng GMT+7',
    schedule_interval=None,
    # schedule_interval='0 1 * * *',  # 1h UTC = 8h sáng GMT+7
    start_date=datetime(2025, 9, 22),
    catchup=False,
) as dag:
    scrape_topcv_jobs = BashOperator(
        task_id='scrape_topcv_jobs',
        bash_command='cd /opt/airflow && python scripts/scrape_topcv_jobs.py',
    )

    upload_to_sheets = BashOperator(
        task_id='upload_to_sheets',
        bash_command='cd /opt/airflow && python scripts/upload_to_sheets.py',
    )

    scrape_topcv_jobs >> upload_to_sheets