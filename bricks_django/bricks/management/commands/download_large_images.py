import os
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from bricks.models import Item

class Command(BaseCommand):
    help = 'Download and store images from WebrickImageReference URLs'

    def handle(self, *args, **options):
        
        items_with_webrick_image_reference = Item.objects.filter(WebrickImageReference__isnull=False)
        items_without_webrick_image_reference = Item.objects.filter(WebrickImageReference__isnull=True)
        items_with_webrick_internal_url = Item.objects.filter(WebrickInternalURL__isnull=True)

        self.stdout.write(self.style.SUCCESS(f'Total items with WebrickImageReference: {items_with_webrick_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items without WebrickImageReference: {items_without_webrick_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total items with WebrickInternalURL null: {items_with_webrick_internal_url.count()}'))

        items = Item.objects.filter(WebrickImageReference__isnull=False)
        downloaded_webrick_images_dir = os.path.join(settings.MEDIA_ROOT, 'downloaded_webrick_images')

        # Check if the download directory exists, and create it if not
        if not os.path.exists(downloaded_webrick_images_dir):
            os.makedirs(downloaded_webrick_images_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {downloaded_webrick_images_dir}'))

        self.stdout.write(self.style.SUCCESS('Downloading will start...'))

        # Add a message to check if there are items to process
        self.stdout.write(self.style.SUCCESS(f'Total items to process: {items.count()}'))        

        for item in items:
            if webrick_image_reference := item.WebrickImageReference:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    }
                    response = requests.get(webrick_image_reference, headers=headers)


                    if response.status_code == 200:
                        extension = os.path.splitext(webrick_image_reference)[1]
                        filename = f'{item.ItemID}-{item.Name}{extension}'
                        local_path = os.path.join(downloaded_webrick_images_dir, filename)

                        # Use os.path.normpath to ensure the path is formatted correctly for the current OS
                        local_path = os.path.normpath(local_path)

                        with open(local_path, 'wb') as f:
                            for chunk in response.iter_content(8192):
                                f.write(chunk)

                        item.WebrickInternalURL = f'downloaded_webrick_images/{filename}'
                        item.save()

                        self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to download {webrick_image_reference}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            else:
                self.stdout.write(self.style.ERROR(f'WebrickImageReference is None for item with pk={item.pk}'))