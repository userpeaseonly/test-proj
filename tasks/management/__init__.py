from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users and tasks for testing'

    def handle(self, *args, **options):
        # Create sample users
        users_data = [
            {'email': 'user1@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'user2@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'user3@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
        ]

        users = []
        for user_data in users_data:
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(
                    email=user_data['email'],
                    password='testpass123',
                    role='user',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                users.append(user)
                self.stdout.write(f'Created user: {user.email}')
            else:
                users.append(User.objects.get(email=user_data['email']))

        # Create sample tasks
        task_templates = [
            'Complete project documentation',
            'Review code changes',
            'Update test cases',
            'Fix reported bugs',
            'Implement new feature',
            'Optimize database queries',
            'Update user interface',
            'Write API documentation',
            'Conduct code review',
            'Deploy to staging'
        ]

        for user in users:
            num_tasks = random.randint(3, 8)
            for i in range(num_tasks):
                task_title = random.choice(task_templates)
                completed = random.choice([True, False])
                
                task = Task.objects.create(
                    title=f"{task_title} - {user.first_name}",
                    description=f"Sample task description for {task_title.lower()}",
                    completed=completed,
                    user=user
                )
                self.stdout.write(f'Created task: {task.title} ({"Completed" if completed else "Pending"})')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data')
        )