from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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

        self.stdout.write(self.style.SUCCESS('Bootstrap completed'))