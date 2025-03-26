import os
import openpyxl
from django.core.management.base import BaseCommand
from inventory.models import Product  # Adjust based on your actual app name

class Command(BaseCommand):
    help = "Import products from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR("File not found!"))
            return

        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active  # Get the first sheet

            products_created = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):  # Start from row 2
                quantity, name, price = row

                # Skip empty rows
                if not name:
                    continue

                product, created = Product.objects.get_or_create(
                    name=name.strip(),
                    defaults={
                        "category_id": 7,  # Assign category ID 1
                        "quantity": int(quantity),
                        "price": float(price),
                    }
                )

                if created:
                    products_created += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {products_created} products with category ID 4."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
