from celery import shared_task, Task
from clickhouse_connect import get_client
from core.event_log_client import EventLogClient
from users.models import UserEventLog
from core import settings
import structlog

logger = structlog.get_logger(__name__)

class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        #logger.info(f"Error occurred while executing task: {task_id}, details: {einfo}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(base=BaseTask)
def process_event_logs_task():
    client_instance = get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        query_retries=2,
        connect_timeout=30,
        send_receive_timeout=10,
    )
    client = EventLogClient(client_instance)

    while True:
        logs = UserEventLog.objects.filter(processed=False)[:100000]
        if not logs:
            break
        batch = []
        for log in logs:
            batch.append({
                'event_type': log.event_type,
                'email': log.payload['email'],
                'first_name': log.payload['first_name'],
                'last_name': log.payload['last_name'],
            })
        if batch:
            # TODO: add try/except for inserting ideally
            client.insert(batch)
            logger.info(f"Inserted {len(batch)} records into Clickhouse")
        for log in logs:
            log.processed = True
        UserEventLog.objects.bulk_update(logs, ['processed'])
        logger.info(f"Updated {len(logs)} records into PostgreSQL")