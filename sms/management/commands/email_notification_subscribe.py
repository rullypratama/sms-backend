from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from kombu import Connection, Exchange, Queue, Message
from kombu.mixins import ConsumerMixin

from sms.helpers import send_notification_email
from users.models import User


class Command(BaseCommand):
    command = None

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        exchange = Exchange(f"{settings.EMAIL_NOTIF_QUEUE_NAME}", type="direct")
        queues = [Queue(f"{settings.EMAIL_NOTIF_QUEUE_NAME}", exchange, routing_key=f"{settings.EMAIL_NOTIF_QUEUE_NAME}")]
        connection = f'amqp://{settings.QUEUE_USER}:{settings.QUEUE_PASSWORD}@{settings.QUEUE_SERVER}//'
        with Connection(connection, heartbeat=4) as conn:
            worker = EmailNotificationWorker(conn, queues)
            worker.run()


class EmailNotificationWorker(ConsumerMixin):
    def __init__(self, connection, queues):
        self.connection = connection
        self.queues = queues

    def on_message(self, body, message: Message):
        try:
            with transaction.atomic(using='default'):
                process_email_notification(body)
            message.ack()
        except Exception:
            # _log.error(f'cant save email notification {body}')
            message.reject()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         callbacks=[self.on_message])]


def process_email_notification(body):
    reporter = User.objects.filter(email=body.get('email')).first()
    health_facility_member = User.objects.filter(health_facility__code=body.get('code'))
    case_information = {
        'name': body.get('name'),
        'gender': body.get('gender'),
        'age': body.get('age'),
        'patient_contact': body.get('patient_contact'),
        'disease_type': body.get('disease_type'),
        'case_report_type': body.get('case_report_type'),
        'classification_case': body.get('classification_case'),
        'address': body.get('address'),
        'is_pregnant': body.get('is_pregnant')
    }
    for member in health_facility_member:
        send_notification_email(member, reporter, case_information)

