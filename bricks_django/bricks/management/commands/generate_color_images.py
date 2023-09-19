import os
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image
from bricks.models import Color

class Command(BaseCommand):
    help = 'Generate colored PNG files from Hex color codes'

    def handle(self, *args, **options):
        colors = Color.objects.all()

        output_directory = os.path.join(settings.MEDIA_ROOT, 'color_images')

        # Check if the download directory exists, and create it if not
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {output_directory}'))

        for color in colors:
            hex_code = color.HEX
            color_id = color.ColorID
            file_name = f"color.{color_id}.png"

            # Create a new image with the specified size and color
            image = Image.new("RGB", (110, 90), hex_code)

            # Save the image to the output directory
            file_path = os.path.join(output_directory, file_name)
            image.save(file_path)

            self.stdout.write(self.style.SUCCESS(f"Saved {file_name}"))

        self.stdout.write(self.style.SUCCESS(f"{len(colors)} PNG files generated in '{output_directory}'"))