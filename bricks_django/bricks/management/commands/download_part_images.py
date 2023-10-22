import os
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from bricks.models import Part

class Command(BaseCommand):
    help = 'Download and store images for Parts'

    def handle(self, *args, **options):
        
        parts_with_image_reference = Part.objects.filter(ImageReference__isnull=False)
        parts_without_image_reference = Part.objects.filter(ImageReference__isnull=True)
        parts_with_internal_url = Part.objects.filter(InternalURL__isnull=True)

        self.stdout.write(self.style.SUCCESS(f'Total parts with ImageReference: {parts_with_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total parts without ImageReference: {parts_without_image_reference.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total parts with InternalURL null: {parts_with_internal_url.count()}'))

        parts = Part.objects.filter(ImageReference__isnull=False)#, InternalURL__isnull=True)
        downloaded_images_dir = os.path.join(settings.MEDIA_ROOT, 'downloaded_part_images')

        # Check if the download directory exists, and create it if not
        if not os.path.exists(downloaded_images_dir):
            os.makedirs(downloaded_images_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {downloaded_images_dir}'))

        self.stdout.write(self.style.SUCCESS('Downloading will start...'))

        # Add a message to check if there are parts to process
        self.stdout.write(self.style.SUCCESS(f'Total parts to process: {parts.count()}'))

        for part in parts:
            image_reference = part.ImageReference

            if image_reference:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    }
                    response = requests.get(image_reference, headers=headers)

                    if response.status_code == 200:
                        extension = os.path.splitext(image_reference)[1]
                        filename = f'{part.PartID}-{part.ItemID.Name}-{part.ColorID.Name}{extension}'
                        local_path = os.path.join(downloaded_images_dir, filename)

                        # Use os.path.normpath to ensure the path is formatted correctly for the current OS
                        local_path = os.path.normpath(local_path)

                        # Add a print statement to track when the file-saving process starts
                        print(f'Saving file: {filename}')

                        with open(local_path, 'wb') as f:
                            for chunk in response.iter_content(8192):
                                f.write(chunk)

                        part.InternalURL = f'downloaded_part_images/{filename}'
                        part.save()

                        self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to download {image_reference}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            else:
                self.stdout.write(self.style.ERROR(f'ImageReference is None for part with pk={part.pk}'))
