import onedrivesdk
import os

import sharepy

import logging

from django.core.management.base import BaseCommand

from unicef_geospatial.core.models import Boundary, BoundaryType, Category, Country, Location

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'fetch sharepoint data'

    def add_arguments(self, parser):
        parser.add_argument('--host',
                            default='https://unicef-my.sharepoint.com',
                            help='Sharepoint host address')
        parser.add_argument('--username',
                            default=None,
                            help='username')
        parser.add_argument('--password',
                            default=None,
                            help='password')

    def handle(self, *args, **options):
        username = options.get('username') or  os.environ.get('SHAREPOINT_USERNAME', None)
        password = options.get('password') or  os.environ.get('SHAREPOINT_PASSWORD', None)

        import onedrivesdk
        from onedrivesdk.helpers import GetAuthCodeServer

        redirect_uri = 'http://localhost:8080/'
        client_secret = 'your_app_secret'
        scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

        client = onedrivesdk.get_default_client(
            client_id='your_client_id', scopes=scopes)

        auth_url = client.auth_provider.get_auth_url(redirect_uri)

        # this will block until we have the code
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)

        client.auth_provider.authenticate(code, redirect_uri, client_secret)
