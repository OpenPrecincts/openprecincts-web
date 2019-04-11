import pytest
import boto3
from moto import mock_s3
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Locality, State
from files.models import File
from contact.models import Official, EmailMessage, EmailMessageInstance
from contact.management.commands.process_email import parse_message, save_reply


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=settings.RAW_FILE_S3_BUCKET)
        # yield to keep context manager active
        yield s3


def test_simple_message_body_extraction():
    body = b"""Return-Path: <james@example.com>
Received: from example.com (example.com [1.2.7.3])
 by inbound-smtp.us-east-1.amazonaws.com with SMTP id ABC
 for collect@example.com;
 Wed, 13 Mar 2019 22:28:36 +0000 (UTC)
X-SES-Spam-Verdict: PASS
X-SES-Virus-Verdict: PASS
MIME-Version: 1.0
From: James <james@example.com>
Date: Wed, 13 Mar 2019 18:28:21 -0400
Subject: Incoming Test
To: collect@example.com
Content-Type: multipart/alternative; boundary="0000000000005d52140584015332"

--0000000000005d52140584015332
Content-Type: text/plain; charset="UTF-8"

This is the plain text.

--0000000000005d52140584015332
Content-Type: text/html; charset="UTF-8"

<div dir="ltr">This is the HTML.</div>

--0000000000005d52140584015332--
"""

    msg = parse_message(body)
    assert msg["from"] == "james@example.com"
    assert msg["body_text"].strip() == "This is the plain text."


def test_no_plaintext_extraction():
    body = b"""Return-Path: <james@example.com>
Received: from example.com (example.com [1.2.7.3])
 by inbound-smtp.us-east-1.amazonaws.com with SMTP id ABC
 for collect@example.com;
 Wed, 13 Mar 2019 22:28:36 +0000 (UTC)
X-SES-Spam-Verdict: PASS
X-SES-Virus-Verdict: PASS
MIME-Version: 1.0
From: James <james@example.com>
Date: Wed, 13 Mar 2019 18:28:21 -0400
Subject: Incoming Test
To: collect@example.com
Content-Type: multipart/alternative; boundary="0000000000005d52140584015332"

--0000000000005d52140584015332
Content-Type: text/html; charset="UTF-8"

<div>This is the HTML.</div>

--0000000000005d52140584015332--
"""

    msg = parse_message(body)
    assert msg["body_text"].strip() == "<div>This is the HTML.</div>"


def test_attachment_extraction():
    body = b"""MIME-Version: 1.0
From: James Turk <james@jamesturk.net>
Date: Thu, 14 Mar 2019 18:24:26 -0400
Subject: attachment test
To: collect@openprecincts.org
Content-Type: multipart/mixed; boundary="000000000000425cb3058415633d"

--000000000000425cb3058415633d
Content-Type: multipart/alternative; boundary="000000000000425caf058415633b"

--000000000000425caf058415633b
Content-Type: text/plain; charset="UTF-8"

white pixel test

--000000000000425caf058415633b
Content-Type: text/html; charset="UTF-8"

<div dir="ltr">white pixel test</div>

--000000000000425caf058415633b--
--000000000000425cb3058415633d
Content-Type: image/png; name="white-pixel.png"
Content-Disposition: attachment; filename="white-pixel.png"
Content-Transfer-Encoding: base64
Content-ID: <f_jt97auq80>
X-Attachment-Id: f_jt97auq80

iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAAlwSFlzAAAL
EwAACxMBAJqcGAAAA6ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6
eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYg
eG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4K
ICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6eG1w
PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICAgICAgICAgICB4bWxuczp0aWZmPSJo
dHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgICAgICAgICAgeG1sbnM6ZXhpZj0iaHR0
cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iPgogICAgICAgICA8eG1wOk1vZGlmeURhdGU+MjAx
OS0wMy0xNFQxODowMzozNjwveG1wOk1vZGlmeURhdGU+CiAgICAgICAgIDx4bXA6Q3JlYXRvclRv
b2w+UGl4ZWxtYXRvciAzLjguMTwveG1wOkNyZWF0b3JUb29sPgogICAgICAgICA8dGlmZjpPcmll
bnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICAgICA8dGlmZjpDb21wcmVzc2lvbj4w
PC90aWZmOkNvbXByZXNzaW9uPgogICAgICAgICA8dGlmZjpSZXNvbHV0aW9uVW5pdD4yPC90aWZm
OlJlc29sdXRpb25Vbml0PgogICAgICAgICA8dGlmZjpZUmVzb2x1dGlvbj43MjwvdGlmZjpZUmVz
b2x1dGlvbj4KICAgICAgICAgPHRpZmY6WFJlc29sdXRpb24+NzI8L3RpZmY6WFJlc29sdXRpb24+
CiAgICAgICAgIDxleGlmOlBpeGVsWERpbWVuc2lvbj4xPC9leGlmOlBpeGVsWERpbWVuc2lvbj4K
ICAgICAgICAgPGV4aWY6Q29sb3JTcGFjZT4xPC9leGlmOkNvbG9yU3BhY2U+CiAgICAgICAgIDxl
eGlmOlBpeGVsWURpbWVuc2lvbj4xPC9leGlmOlBpeGVsWURpbWVuc2lvbj4KICAgICAgPC9yZGY6
RGVzY3JpcHRpb24+CiAgIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CsbTytkAAAAMSURBVAgdY/j/
/z8ABf4C/p/KLRMAAAAASUVORK5CYII=
--000000000000425cb3058415633d--"""

    msg = parse_message(body)
    attachments = msg["attachments"]
    assert len(attachments) == 1
    assert attachments[0]["content_type"] == "image/png"
    assert attachments[0]["filename"] == "white-pixel.png"
    assert len(attachments[0]["body"]) == 1049


@pytest.fixture
def emi():
    """ fixture for an EmailMessageInstance """
    user = User.objects.create(username="testuser")
    loc = Locality.objects.get(name="Wake County", state__abbreviation="NC")
    loc.state.cycles.create(year="2020")
    anne = Official.objects.create(
        first_name="Anne", email="anne@example.com", locality=loc, created_by=user
    )
    em = EmailMessage.objects.create(
        subject_template="Subj",
        body_template="Body",
        created_by=user,
        sent_at="2019-01-01T12:00Z",
        state=State.objects.get(abbreviation="NC"),
    )
    return EmailMessageInstance.objects.create(official=anne, message=em)


@pytest.mark.django_db
def test_save_reply_simple(emi):
    message = {
        "to": f"collect+{emi.id}@example.com",
        "from": "anne@example.com",
        "date": "2019-02-15T12:00:00Z",
        "body_text": "this is the body",
        "attachments": [],
    }

    save_reply(message)

    # reply is now attached to EMI
    reply = emi.replies.get()
    assert reply.from_email == "anne@example.com"


@pytest.mark.django_db
def test_save_reply_attachments(emi, s3):
    message = {
        "to": f"collect+{emi.id}@example.com",
        "from": "anne@example.com",
        "date": "2019-02-15T12:00:00Z",
        "body_text": "this is the body",
        "attachments": [
            {
                "content_type": "text/plain",
                "body": b"this is the attachment",
                "filename": "a.txt",
            }
        ],
    }
    save_reply(message)

    # reply is now attached to EMI
    reply = emi.replies.get()
    assert reply.from_email == "anne@example.com"

    f = File.objects.get()
    assert f.source_filename == "a.txt"
    assert f.official is not None
