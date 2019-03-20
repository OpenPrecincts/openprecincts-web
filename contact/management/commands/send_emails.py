import datetime
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from contact.models import EmailMessage, EmailMessageInstance
from contact.views import render_email


class Command(BaseCommand):
    help = "send outgoing emails"

    def handle(self, *args, **options):
        to_send = EmailMessage.objects.filter(
            approved_by__isnull=False, approved_at__isnull=False, sent_at__isnull=True
        )
        to_send = list(to_send)

        if not to_send:
            self.stdout.write(self.style.SUCCESS("No messages to send!"))
            return

        self.stdout.write(f"Preparing to send {len(to_send)} messages...")

        for email in to_send:
            prepared_emails = []
            emis = EmailMessageInstance.objects.filter(message=email)
            for emi in emis:
                to_email, subject, body = render_email(email, emi.official)
                from_email = "collect+{emi.id}@openprecincts.org"
                prepared_emails.append((subject, body, from_email, [to_email]))

            # mark as sent first, err on the side of preventing double sending
            sent_at = datetime.datetime.now()
            email.sent_at = sent_at
            email.save()
            emis.update(sent_at=sent_at)

            send_mass_mail(prepared_emails)
