from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.models import Variable
from datetime import timedelta
from airflow.utils.dates import days_ago

# ── Default arguments ─────────────────────────────────────────────────────────
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# ── Define the DAG ─────────────────────────────────────────────────────────────
dag = DAG(
    dag_id='load_raw_data',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['tennis', 'raw', 's3', 'snowflake'],
)

# ── Airflow Variables ──────────────────────────────────────────────────────────
S3_BUCKET = Variable.get('S3_BUCKET')
AWS_KEY   = Variable.get('AWS_ACCESS_KEY_ID')
AWS_SECRET= Variable.get('AWS_SECRET_ACCESS_KEY')
SF_CONN   = 'snowflake_connection_tennis'

# ── SQL to create tables ───────────────────────────────────────────────────────
# 1) RAW_MATCHES
sql_create_raw_matches = f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE TABLE RAW_MATCHES (
    tourney_id STRING,
    tourney_name STRING,
    surface STRING,
    draw_size NUMBER,
    tourney_level STRING,
    tourney_date NUMBER,
    match_num NUMBER,

    winner_id NUMBER,
    winner_seed STRING,
    winner_entry VARCHAR(5),
    winner_name STRING,
    winner_hand STRING,
    winner_ht NUMBER,
    winner_ioc STRING,
    winner_age FLOAT,

    loser_id NUMBER,
    loser_seed NUMBER,
    loser_entry VARCHAR(5),
    loser_name STRING,
    loser_hand STRING,
    loser_ht NUMBER,
    loser_ioc STRING,
    loser_age FLOAT,

    score STRING,
    best_of NUMBER,
    round STRING,
    minutes NUMBER,

    w_ace NUMBER,
    w_df NUMBER,
    w_svpt NUMBER,
    w_1stIn NUMBER,
    w_1stWon NUMBER,
    w_2ndWon NUMBER,
    w_SvGms NUMBER,
    w_bpSaved NUMBER,
    w_bpFaced NUMBER,

    l_ace NUMBER,
    l_df NUMBER,
    l_svpt NUMBER,
    l_1stIn NUMBER,
    l_1stWon NUMBER,
    l_2ndWon NUMBER,
    l_SvGms NUMBER,
    l_bpSaved NUMBER,
    l_bpFaced NUMBER,

    winner_rank NUMBER,
    winner_rank_points NUMBER,
    loser_rank NUMBER,
    loser_rank_points NUMBER
);
COMMIT;
'''

# 2) RAW_PLAYERS
sql_create_raw_players = f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE TABLE RAW_PLAYERS (
    PLAYER_ID INTEGER,
    NAME_FIRST VARCHAR(50),
    NAME_LAST VARCHAR(50),
    HAND VARCHAR(5),
    DOB DATE,
    IOC VARCHAR(5),
    HEIGHT FLOAT,
    WIKIDATA_ID VARCHAR(20)
);
COMMIT;
'''

# 3) RAW_RANKINGS (decades)
sql_create_raw_rankings = f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE TABLE RAW_RANKINGS (
    RANKING_DATE NUMBER,
    RANK NUMBER,
    PLAYER NUMBER,
    POINTS NUMBER
);
COMMIT;
'''

# 4) RAW_RANKINGS_CURRENT (snapshot)
sql_create_raw_rankings_current = f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE TABLE RAW_RANKINGS_CURRENT (
    RANKING_DATE NUMBER,
    RANK NUMBER,
    PLAYER NUMBER,
    POINTS NUMBER
);
COMMIT;
'''

# ── 5) Create Stage for S3 ─────────────────────────────────────────────────────
sql_create_stage = f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE STAGE RAW_TENNIS_STAGE
  URL='s3://{S3_BUCKET}/'
  CREDENTIALS=(
    AWS_KEY_ID='{AWS_KEY}'
    AWS_SECRET_KEY='{AWS_SECRET}'
  )
  DIRECTORY=(ENABLE = TRUE);
COMMIT;
'''

# ── 6) Create CSV File Format ──────────────────────────────────────────────────
sql_create_file_format = '''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
CREATE OR REPLACE FILE FORMAT RAW_CSV_FORMAT
  TYPE = CSV
  SKIP_HEADER = 1
  FIELD_DELIMITER = ','
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  TRIM_SPACE = TRUE
  REPLACE_INVALID_CHARACTERS = TRUE
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;
COMMIT;
'''

# ── 7) Helper for COPY INTO ────────────────────────────────────────────────────
def make_copy_sql(table_name: str, pattern: str) -> str:
    return f'''
USE WAREHOUSE compute_wh;
USE DATABASE tennis_project;
USE SCHEMA raw;
BEGIN;
COPY INTO {table_name}
  FROM @RAW_TENNIS_STAGE
  PATTERN = '{pattern}'
  FILE_FORMAT = (FORMAT_NAME = 'RAW_CSV_FORMAT')
  ON_ERROR = 'CONTINUE';
COMMIT;
'''

# ── 8) Define tasks ───────────────────────────────────────────────────────────
create_raw_matches = SnowflakeOperator(
    task_id='create_raw_matches_table',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_raw_matches,
    dag=dag,
)
create_raw_players = SnowflakeOperator(
    task_id='create_raw_players_table',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_raw_players,
    dag=dag,
)
create_raw_rankings = SnowflakeOperator(
    task_id='create_raw_rankings_table',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_raw_rankings,
    dag=dag,
)
create_raw_rankings_current = SnowflakeOperator(
    task_id='create_raw_rankings_current_table',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_raw_rankings_current,
    dag=dag,
)
create_stage = SnowflakeOperator(
    task_id='create_s3_stage',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_stage,
    dag=dag,
)
create_file_format = SnowflakeOperator(
    task_id='create_csv_file_format',
    snowflake_conn_id=SF_CONN,
    sql=sql_create_file_format,
    dag=dag,
)
load_matches = SnowflakeOperator(
    task_id='load_raw_matches',
    snowflake_conn_id=SF_CONN,
    sql=make_copy_sql('RAW_MATCHES', r'.*atp_matches_[0-9]{4}[.]csv'),
    dag=dag,
)
load_players = SnowflakeOperator(
    task_id='load_raw_players',
    snowflake_conn_id=SF_CONN,
    sql=make_copy_sql('RAW_PLAYERS', r'.*atp_players[.]csv'),
    dag=dag,
)
load_rankings = SnowflakeOperator(
    task_id='load_raw_rankings',
    snowflake_conn_id=SF_CONN,
    sql=make_copy_sql('RAW_RANKINGS', r'.*atp_rankings_[0-9]{2}s[.]csv'),
    dag=dag,
)
load_rankings_current = SnowflakeOperator(
    task_id='load_raw_rankings_current',
    snowflake_conn_id=SF_CONN,
    sql=make_copy_sql('RAW_RANKINGS_CURRENT', r'.*atp_rankings_current[.]csv'),
    dag=dag,
)

# ── 9) Dependencies ───────────────────────────────────────────────────────────
[create_raw_matches, create_raw_players, create_raw_rankings, create_raw_rankings_current] >> create_stage
create_stage >> create_file_format
create_file_format >> [load_matches, load_players, load_rankings, load_rankings_current]