from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import logging

def create_rankings_table():
    try:
        print("[DEBUG]", "In create_rankings_table")
        hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DEV.GROUP_PROJECT_RAW.LIVE_RANKINGS (
                RK INT,
                NAME STRING,
                POINTS INT,
                AGE INT,
                SCRAPED_AT DATE
            )
        """)
        ## Ensure Idempotency.
        cursor.execute("""
            DELETE FROM DEV.GROUP_PROJECT_RAW.LIVE_RANKINGS;
        """)
        conn.commit()
        logging.info("Table LIVE_RANKINGS created or already exists.")
    except Exception as e:
        logging.error(f"Failed to create table: {e}")
    finally:
        if conn:
            conn.close()

def fetch_rankings_data(**context):
    url = Variable.get("ESPN_ATP_RANKINGS_URL")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    rankings = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='Table')
        if not table:
            logging.warning("Rankings table not found on the page.")
            return

        rows = table.find_all('tr')[1:]
        logging.info(f"Found {len(rows)} rows in the table.")
        print("[DEBUG]", rows)

        for row in rows:
            cols = [td.text.strip() for td in row.find_all('td')]
            print(cols)
            try:
                rk = int(cols[0])
                name = cols[2]
                points = int(cols[3].replace(',', ''))
                age = int(cols[4])
                rankings.append((rk, name, points, age))
                print("[DEBUG]", row)
            except ValueError:
                continue

        logging.info(f"Parsed {len(rankings)} valid rows from ESPN.")
        context['ti'].xcom_push(key='rankings', value=rankings)
    except Exception as e:
        logging.error(f"Fetching failed: {e}")

def load_rankings_to_snowflake(**context):
    rankings = context['ti'].xcom_pull(task_ids='fetch_rankings_data', key='rankings')
    if not rankings:
        logging.warning("No data to load into Snowflake.")
        return
    try:
        hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        today = datetime.today().date().isoformat()
        cursor.execute("DELETE FROM DEV.GROUP_PROJECT_RAW.LIVE_RANKINGS WHERE SCRAPED_AT = %s", (today,))
        insert_sql = """
            INSERT INTO DEV.GROUP_PROJECT_RAW.LIVE_RANKINGS (RK, NAME, POINTS, AGE, SCRAPED_AT)
            VALUES (%s, %s, %s, %s, %s)
        """
        for rk, name, points, age in rankings:
            cursor.execute(insert_sql, (rk, name, points, age, today))
        conn.commit()
        logging.info(f"Loaded {len(rankings)} records to Snowflake.")
    except Exception as e:
        logging.error(f"Load failed: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

with DAG(
    dag_id="live_rankings",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["espn", "wta", "tennis"]
) as dag:

    create_table = PythonOperator(
        task_id="create_rankings_table",
        python_callable=create_rankings_table
    )

    fetch_data = PythonOperator(
        task_id="fetch_rankings_data",
        python_callable=fetch_rankings_data,
        provide_context=True
    )

    load_data = PythonOperator(
        task_id="load_rankings_to_snowflake",
        python_callable=load_rankings_to_snowflake,
        provide_context=True
    )

    create_table >> fetch_data >> load_data
