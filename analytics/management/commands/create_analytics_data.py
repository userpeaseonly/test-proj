from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to create sample data for analytics monitoring.
    This creates users and tasks that can be monitored through the analytics dashboard
    using PostgreSQL aggregation queries on the existing models.
    """
    help = 'Create sample data for analytics dashboard monitoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=50,
            help='Number of tasks to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Task.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create users
        self.stdout.write(f'Creating {options["users"]} users...')
        users = self.create_users(options['users'])
        
        # Create tasks
        self.stdout.write(f'Creating {options["tasks"]} tasks...')
        self.create_tasks(users, options['tasks'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {options["users"]} users and {options["tasks"]} tasks for analytics monitoring'
            )
        )

    def create_users(self, count):
        """Create test users for analytics monitoring"""
        users = []
        
        # Sample user data
        first_names = [
            'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry',
            'Iris', 'Jack', 'Kate', 'Liam', 'Mia', 'Noah', 'Olivia', 'Peter',
            'Quinn', 'Ruby', 'Sam', 'Tina'
        ]
        
        last_names = [
            'Anderson', 'Brown', 'Clark', 'Davis', 'Evans', 'Foster', 'Green',
            'Harris', 'Jones', 'King', 'Lewis', 'Miller', 'Nelson', 'Parker',
            'Roberts', 'Smith', 'Taylor', 'Wilson', 'Young', 'Zhang'
        ]
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            
            # Avoid duplicates
            if User.objects.filter(email=email).exists():
                email = f"user{i}_{random.randint(1000, 9999)}@example.com"
            
            user = User.objects.create_user(
                email=email,
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                role='user'
            )
            users.append(user)
            
        return users

    def create_tasks(self, users, count):
        """Create test tasks for analytics monitoring"""
        task_titles = [
            'Complete project proposal',
            'Review code changes',
            'Update documentation',
            'Fix critical bug',
            'Implement new feature',
            'Write unit tests',
            'Update user interface',
            'Optimize database queries',
            'Prepare presentation',
            'Conduct user research',
            'Design system architecture',
            'Create API endpoints',
            'Refactor legacy code',
            'Setup CI/CD pipeline',
            'Analyze performance metrics',
            'Create backup strategy',
            'Update dependencies',
            'Write technical specifications',
            'Conduct code review',
            'Deploy to production',
            'Monitor system health',
            'Create user stories',
            'Design database schema',
            'Implement authentication',
            'Create landing page',
            'Setup monitoring',
            'Write integration tests',
            'Create user manual',
            'Optimize images',
            'Setup email notifications'
        ]
        
        task_descriptions = [
            'This is an important task that needs to be completed soon.',
            'High priority item requiring immediate attention.',
            'Regular maintenance task for system stability.',
            'User-requested feature enhancement.',
            'Technical debt that should be addressed.',
            'Quality assurance and testing task.',
            'Documentation update for better clarity.',
            'Performance optimization requirement.',
            'Strategic planning and analysis.',
            'Research and development task.'
        ]
        
        tasks = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        for i in range(count):
            # Random creation date within the last 30 days
            random_days = random.randint(0, 30)
            created_at = start_date + timedelta(days=random_days)
            
            # Add some time variation within the day
            created_at += timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Random completion status (70% completion rate on average)
            completed = random.random() < 0.7
            
            # If completed, set a random completion time after creation
            if completed:
                max_completion_days = min(
                    (end_date - created_at).days,
                    7  # Complete within 1-7 days
                )
                if max_completion_days > 0:
                    completion_days = random.randint(0, max_completion_days)
                    completion_time = created_at + timedelta(
                        days=completion_days,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    updated_at = completion_time
                else:
                    # If same day, just add some hours
                    updated_at = created_at + timedelta(
                        hours=random.randint(1, 23),
                        minutes=random.randint(0, 59)
                    )
            else:
                # Random update time for incomplete tasks
                max_update_days = (end_date - created_at).days
                if max_update_days > 0:
                    update_days = random.randint(0, max_update_days)
                    updated_at = created_at + timedelta(
                        days=update_days,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                else:
                    updated_at = created_at
            
            task = Task.objects.create(
                title=random.choice(task_titles),
                description=random.choice(task_descriptions),
                user=random.choice(users),
                completed=completed,
                created_at=created_at,
                updated_at=updated_at
            )
            tasks.append(task)
            
        return tasks
