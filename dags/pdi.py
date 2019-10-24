import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.hooks.base_hook import BaseHook


def task_fail_slack_alert(context):

    failed_alert = SlackAPIPostOperator(
            task_id='slack_failed',
            channel=slack_channel,
            token=slack_token,
            text="""
                :red_circle: Task Failed. 
                *Task*: {task}  
                *Dag*: {dag} 
                *Execution Time*: {exec_date}  
                *Log Url*: {log_url} 
                """.format(
                task=context.get('task_instance').task_id,
                dag=context.get('task_instance').dag_id,
                ti=context.get('task_instance'),
                exec_date=context.get('execution_date'),
                log_url=context.get('task_instance').log_url,
            )
        )
    return failed_alert.execute(context=context)

default_args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
    'retries': 0,
    'on_failure_callback': task_fail_slack_alert
}
dag = DAG(
    dag_id='pdi',
    default_args=default_args,
    schedule_interval="* * * * *",
)

task_with_failed_slack_alerts = BashOperator(
    task_id='fail_task',
    bash_command='exit 1',
    on_failure_callback=task_fail_slack_alert,
    provide_context=True,
    dag=dag)