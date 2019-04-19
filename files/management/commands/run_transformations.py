from django.core.management.base import BaseCommand
from files.models import Transformation
from files.transformations import run_transformation


class Command(BaseCommand):
    help = "run transformations"

    def handle(self, *args, **options):
        to_run = Transformation.objects.filter(finished_at__isnull=True)

        self.stdout.write(f"Preparing to run {len(to_run)} transformations...")

        for t in to_run:
            self.stdout.write(f"running #{t.id}: {t.get_transformation_display()}")
            run_transformation(t)
