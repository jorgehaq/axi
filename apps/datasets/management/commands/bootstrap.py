from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from apps.auth.models import OAuthApplication

class Command(BaseCommand):
    help = 'Bootstrap initial users and data'

    def handle(self, *args, **options):
        # Create default test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'password': make_password('testpass'),
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created testuser')
            )
        else:
            self.stdout.write(
                self.style.WARNING('testuser already exists')
            )

        # Create test OAuth application
        oauth_app, app_created = OAuthApplication.objects.get_or_create(
            client_id='test_client',
            defaults={
                'name': 'Test Application',
                'client_secret': 'test_secret'
            }
        )

        if app_created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test OAuth application')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Test OAuth application already exists')
            )

        # Create Gmail OAuth application for testing
        gmail_app, gmail_created = OAuthApplication.objects.get_or_create(
            client_id='axi-gmail-client',
            defaults={
                'name': 'Gmail Test Application',
                'client_secret': 'generated-secret'
            }
        )

        if gmail_created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Gmail OAuth application')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Gmail OAuth application already exists')
            )

        self.stdout.write(self.style.SUCCESS('Bootstrap completed'))