import re
import io
import json
import email
from django.core.management.base import BaseCommand
from django.conf import settings
from contact.models import EmailMessageInstance, EmailReply
from files.utils import upload_file
import boto3


def get_messages():
    sqs = boto3.resource("sqs")
    q = sqs.get_queue_by_name(QueueName=settings.CONTACT_SQS_QUEUE)

    bad = 0
    good = 0

    while True:
        messages = q.receive_messages(MaxNumberOfMessages=10)
        if not messages:
            break
        for msg in messages:
            body = json.loads(msg.body)
            if body.get("Records", [{}])[0].get("eventName", "") != "ObjectCreated:Put":
                # TODO: log this somewhere useful
                print("bad message", body)
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


def parse_message(message_bytes):
    em = email.message_from_bytes(message_bytes, policy=email.policy.default)

    body = em.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content()

    attachments = []
    for attachment in em.iter_attachments():
        attachments.append(
            {
                "content_type": attachment.get_content_type(),
                "body": attachment.get_content(),
                "filename": re.findall('name="(.*)"', attachment["Content-Type"])[0],
            }
        )

    return {
        "from": re.findall("<(.*)>", em["From"])[0],
        "to": em["To"],
        "date": em["Date"],
        "body_text": body_text,
        "attachments": attachments,
    }


def save_reply(msg):
    # use the +msgid part of the To: address to figure out what this is a reply to
    msg_id = re.findall(r"\+(\d+)@", msg["to"])
    emi = None
    if msg_id:
        try:
            emi = EmailMessageInstance.objects.get(pk=msg_id[0])
        except EmailMessageInstance.DoesNotExist:
            pass

    if not emi:
        raise ValueError("could not find parent message for " + msg["to"])

    EmailReply.objects.create(
        reply_to=emi,
        from_email=msg["from"],
        timestamp=msg["date"],
        body_text=msg["body_text"],
    )

    # save the attachments
    for attachment in msg["attachments"]:
        upload_file(
            stage="S",
            locality=emi.official.locality,
            official=emi.official,
            mime_type=attachment["content_type"],
            size=len(attachment["body"]),
            filename=attachment["filename"],
            created_by=emi.message.created_by,
            file_obj=io.BytesIO(attachment["body"]),
        )


class Command(BaseCommand):
    help = "check incoming emails and process them"

    def handle(self, *args, **options):
        s3 = boto3.client("s3")
        for message in get_messages():
            obj = s3.get_object(Key=message["key"], Bucket=message["bucket"])
            msg = parse_message(obj["Body"].read())
            try:
                save_reply(msg)
                message.delete()
            except ValueError as e:
                print(e)
