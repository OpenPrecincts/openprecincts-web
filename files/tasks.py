from celery import shared_task
from .transformations.basic import ZipFiles

@shared_task
def zip_files(created_by, files):
    ZipFiles(created_by, files).run()
