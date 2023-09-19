import os
from django.core.management import call_command
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'Backup the Django database'

    def handle(self, *args, **options):
        # Define the directory where backup files will be stored
        backup_dir = os.path.join(settings.BASE_DIR, 'database_backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate a timestamp for the backup file
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')

        # Define the backup file path
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')

        # Run the dumpdata command to create the backup
        try:
            call_command('dumpdata', output=backup_file)
            self.stdout.write(self.style.SUCCESS(f'Successfully backed up the database to {backup_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
