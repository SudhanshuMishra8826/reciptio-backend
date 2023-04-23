"""
Wait for db to be available
"""

from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycopg2OperationalError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for db...')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OperationalError, OperationalError):
                self.stdout.write('Db unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Db available!'))
