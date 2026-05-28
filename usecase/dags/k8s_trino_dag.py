from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import timedelta, datetime
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
        dag_id='k8s_dbt_trino',
        dag_display_name='🤖 K8s DBT Trino',
        default_args=default_args,
        description='Run a task in a Kubernetes pod using the KubernetesPodOperator',
        schedule=None,
        start_date=datetime(2026,5,24),
        catchup=False,
        tags=['example', 'kubernetes'],
) as dag:

    run_in_k8s = KubernetesPodOperator(
        namespace='services',  # or your airflow namespace
        image='nilli9990/dbt-upcloud-webinar',
        labels={"app": "airflow"},
        name="run_dbt_trino_task",
        task_id="run_dbt_trino_task",
        env_vars={
            'TARGET': 'dev',
        },
        get_logs=True,
        is_delete_operator_pod=True,  # Clean up after running
    )

    run_in_k8s