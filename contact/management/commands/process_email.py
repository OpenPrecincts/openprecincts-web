import json
import email
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3


def get_messages():
    sqs = boto3.resource('sqs')
    q = sqs.get_queue_by_name(QueueName=settings.CONTACT_SQS_QUEUE)

    bad = 0
    good = 0

    while True:
        messages = q.receive_messages(MaxNumberOfMessages=10)
        if not messages:
            break
        for msg in messages:
            body = json.loads(msg.body)
            if body.get('Records', [{}])[0].get('eventName', '') != 'ObjectCreated:Put':
                # TODO: log this somewhere useful
                print('bad', body)
                msg.delete()
                bad += 1
                continue

            # normal S3 email handling
            good += 1
            yield {
                "key": body["Records"][0]["s3"]["object"]["key"],
                "bucket": body["Records"][0]["s3"]["bucket"]["name"],
                "time": body["Records"][0]["eventTime"],
                "sqs_message": msg,
            }


def handle_message(message_bytes):
    em = email.message_from_bytes(message_bytes, policy=email.policy.default)

    body = em.get_body(preferencelist=('plain', 'html'))
    body_text = body.get_content()

    attachments = list(em.iter_attachments())
    print(attachments)

    return body_text, attachments


class Command(BaseCommand):
    help = "check incoming emails and process them"

    def handle(self, *args, **options):
        s3 = boto3.client("s3")
        for message in get_messages():
            print(message)
            obj = s3.get_object(Key=message['key'], Bucket=message['bucket'])
            handle_message(obj['Body'].read())

        handle_message({'key': '873ms3qntcqj8h4krrbc1d2p7fd8uucpf3lniho1',
                        'bucket': 'openprecincts-incoming-email'})
