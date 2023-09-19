import os
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from bricks.models import Item

class Command(BaseCommand):
    help = 'Download and store images from ImageReference URLs'

    def handle(self, *args, **options):
        
        items_with_image_reference = Item.objects.filter(ImageReference__isnull=False)
        items_without_image_reference = Item.objects.filter(ImageReference__isnull=True)
        items_with_internal_url = Item.objects.filter(InternalURL__isnull=True)

        self.stdout.write(self.style.SUCCESS(f'Total items with ImageReference: {items_with_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items without ImageReference: {items_without_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items with InternalURL null: {items_with_internal_url.count()}'))

        items = Item.objects.filter(ImageReference__isnull=False)#, InternalURL__isnull=True)
        downloaded_images_dir = os.path.join(settings.MEDIA_ROOT, 'downloaded_images')
        
        # Check if the download directory exists, and create it if not
        if not os.path.exists(downloaded_images_dir):
            os.makedirs(downloaded_images_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {downloaded_images_dir}'))

        self.stdout.write(self.style.SUCCESS('Downloading will start...'))
        
        # Add a message to check if there are items to process
        self.stdout.write(self.style.SUCCESS(f'Total items to process: {items.count()}'))
        
        for item in items:
            image_reference = item.ImageReference
            image_name = os.path.basename(image_reference)
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                response = requests.get(image_reference, headers=headers)
                
                if response.status_code == 200:
                    filename = os.path.basename(image_reference)
                    local_path = os.path.join(downloaded_images_dir, filename)

                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(8192):
                            f.write(chunk)

                    item.InternalURL = f'downloaded_images/{filename}'
                    item.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download {image_reference}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))