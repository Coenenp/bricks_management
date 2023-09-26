import os
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from bricks.models import Item

class Command(BaseCommand):
    help = 'Download and store images from LargeImageReference URLs'

    def handle(self, *args, **options):
        
        items_with_large_image_reference = Item.objects.filter(LargeImageReference__isnull=False)
        items_without_large_image_reference = Item.objects.filter(LargeImageReference__isnull=True)
        items_with_large_internal_url = Item.objects.filter(LargeInternalURL__isnull=True)

        self.stdout.write(self.style.SUCCESS(f'Total items with ImageReference: {items_with_large_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items without ImageReference: {items_without_large_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items with InternalURL null: {items_with_large_internal_url.count()}'))

        items = Item.objects.filter(LargeImageReference__isnull=False)#, LargeInternalURL__isnull=True)
        downloaded_large_images_dir = os.path.join(settings.MEDIA_ROOT, 'downloaded_large_images')
        
        # Check if the download directory exists, and create it if not
        if not os.path.exists(downloaded_large_images_dir):
            os.makedirs(downloaded_large_images_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {downloaded_large_images_dir}'))

        self.stdout.write(self.style.SUCCESS('Downloading will start...'))
        
        # Add a message to check if there are items to process
        self.stdout.write(self.style.SUCCESS(f'Total items to process: {items.count()}'))
        
        for item in items:
            large_image_reference = item.LargeImageReference
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                response = requests.get(large_image_reference, headers=headers)
                
                if response.status_code == 200:
                    filename = os.path.basename(large_image_reference)
                    local_path = os.path.join(downloaded_large_images_dir, filename)

                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(8192):
                            f.write(chunk)

                    item.LargeInternalURL = f'downloaded_large_images/{filename}'
                    item.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download {large_image_reference}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))