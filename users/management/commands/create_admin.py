from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email', required=True)
        parser.add_argument('--password', type=str, help='Admin password', required=True)
        parser.add_argument('--first-name', type=str, help='First name', default='Admin')
        parser.add_argument('--last-name', type=str, help='Last name', default='User')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return

        user = User.objects.create_user(
            email=email,
            password=password,
            role='admin',
            is_staff=True,
            is_superuser=True,
            first_name=first_name,
            last_name=last_name
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {email}')
        )