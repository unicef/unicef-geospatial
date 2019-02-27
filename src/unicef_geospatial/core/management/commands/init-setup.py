import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand

from constance import config

from unicef_geospatial.utils import locking


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument(
            '--deploy',
            action='store_true',
            dest='deploy',
            default=False,
            help='run deployment related actions')
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help='select all options but `demo`')
        parser.add_argument(
            '--interactive',
            action='store_true',
            dest='interactive',
            default=False,
            help='select all production deployment options')

        parser.add_argument(
            '--collectstatic',
            action='store_true',
            dest='collectstatic',
            default=False,
            help='')

        parser.add_argument(
            '--users',
            action='store_true',
            dest='users',
            default=False,
            help='')

        parser.add_argument(
            '--migrate',
            action='store_true',
            dest='migrate',
            default=False,
            help='select all production deployment options')

        parser.add_argument(
            '--tasks',
            action='store_true',
            dest='tasks',
            default=False,
            help='schedule tasks')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        migrate = options['migrate']
        _all = options['all']
        deploy = options['deploy']
        if deploy:
            _all = True
        ModelUser = get_user_model()
        lock = locking.lock('init-setup', timeout=60 * 5)
        if not lock.acquire(blocking=False):
            self.stderr.write("Another process is running setup. Nothing to do.")
            return ""
        try:
            if options['collectstatic'] or _all:
                self.stdout.write(f"Run collectstatic")
                call_command('collectstatic', verbosity=verbosity - 1, interactive=False)

            if migrate or _all:
                self.stdout.write(f"Run migrations")
                call_command('migrate', verbosity=verbosity - 1)

            self.stdout.write(f"Create group `{config.DEFAULT_GROUP}`")
            default_group, __ = Group.objects.get_or_create(name=config.DEFAULT_GROUP)

            if options['users'] or _all:
                if settings.DEBUG:
                    pwd = '123'
                    admin = os.environ.get('USER', 'admin')
                else:
                    pwd = os.environ.get('ADMIN_PASSWORD', ModelUser.objects.make_random_password())
                    admin = os.environ.get('ADMIN_USERNAME', 'admin')

                self._admin_user, created = ModelUser.objects.get_or_create(username=admin,
                                                                            defaults={"is_superuser": True,
                                                                                      "is_staff": True,
                                                                                      "password": make_password(pwd)})

                if created:  # pragma: no cover
                    self.stdout.write(f"Created superuser `{admin}` with password `{pwd}`")
                else:  # pragma: no cover
                    self.stdout.write(f"Superuser `{admin}` already exists`.")

        finally:
            lock.release()
