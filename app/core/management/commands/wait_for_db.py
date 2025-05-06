"""
Django command to wait for database to be available
"""
from time import sleep
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        """EntryPoint for command"""
        self.stdout.write('Waiting for database .....')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable waiting 1 seccond...')
        self.stdout.write(self.style.SUCCESS('Database available!'))
