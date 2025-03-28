from django.core.management.base import BaseCommand
from ocr.models import HandwrittenText

class Command(BaseCommand):
    help = 'Cleanup old media files'

    def handle(self, *args, **options):
        HandwrittenText.cleanup_old_files(days=1)  # Adjust days as needed
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up old media files')) 