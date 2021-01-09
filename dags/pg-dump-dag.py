from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from datetime import datetime


cmd = """
# dump database
pg_dump -h {{ params.pg_host }} -p {{ params.pg_port }} -U {{ params.pg_user }} -n airflow -Fc {{ params.pg_database }} > airflow.db
zip airflow.zip airflow.db
# upload file to S3
export AWS_ACCESS_KEY_ID={{ params.secret_access_key }}
export AWS_SECRET_ACCESS_KEY={{ params.secret_key }}
export AWS_DEFAULT_REGION={{ params.region }}
aws s3 cp airflow.zip s3://{{ params.s3_bucket_name }}/{{ params.s3_key }}
"""


with DAG(
    "pg_dump_dag",
    start_date=datetime(2021, 1, 1),
    max_active_runs=1,
    schedule_interval=None,
) as dag:

    t1 = BashOperator(
        task_id='print_connection_params',
        bash_command="echo $AIRFLOW_CONN_AIRFLOW_DB",
        dag=dag,
    )

    t2 = BashOperator(
        task_id='set_postgres_pass',
        bash_command="echo *:*:*:*:" +
        Variable.get("PG_PASS") + " > ~/.pgpass && chmod 600 ~/.pgpass",
        dag=dag,
    )

    t3 = BashOperator(
        task_id='pg_dump',
        bash_command=cmd,
        params={
            "pg_host": Variable.get("PG_HOST"),
            "pg_port": Variable.get("PG_PORT"),
            "pg_user": Variable.get("PG_USER"),
            "pg_database": Variable.get("PG_DATABASE"),
            "secret_access_key": Variable.get("AWS_ACCESS_KEY_ID"),
            "secret_key": Variable.get("AWS_SECRET_ACCESS_KEY"),
            "region": Variable.get("AWS_DEFAULT_REGION"),
            "s3_bucket_name": Variable.get("S3_BACKET"),
            "s3_key": Variable.get("S3_KEY")
        },
        dag=dag,
    )

    t2 >> t3
