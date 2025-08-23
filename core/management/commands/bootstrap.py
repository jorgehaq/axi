from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create bootstrap users for API testing and administration'

    def handle(self, *args, **options):
        users_created = 0
        
        # Create test user for API testing
        try:
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@analytics-api.com',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass')
                user.save()
                users_created += 1
                self.stdout.write(
                    self.style.SUCCESS('✅ Test user "testuser" created successfully')
                )
            else:
                self.stdout.write('ℹ️ Test user "testuser" already exists')
                
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING('⚠️ Could not create testuser')
            )

        # Create admin user for management
        try:
            admin, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@analytics-api.com',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            if created:
                admin.set_password('AdminSecure2024!')
                admin.save()
                users_created += 1
                self.stdout.write(
                    self.style.SUCCESS('✅ Admin user "admin" created successfully')
                )
            else:
                self.stdout.write('ℹ️ Admin user "admin" already exists')
                
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING('⚠️ Could not create admin user')
            )

        # Summary report
        if users_created > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Bootstrap completed! {users_created} new users created.')
            )
            self.stdout.write('\n📋 Available users:')
            self.stdout.write('   testuser / testpass (for API testing)')
            self.stdout.write('   admin / AdminSecure2024! (for administration)')
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ All users already exist. Bootstrap completed.')
            )