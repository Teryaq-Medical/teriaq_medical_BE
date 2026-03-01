# fix_lab_specialists.py
import os
import sys

# 1️⃣ Add project root to sys.path
sys.path.append(r"E:\django\Teriaq\env\src")  # <-- path to the folder containing manage.py

# 2️⃣ Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ASER.settings")  # <-- replace with your actual settings module

# 3️⃣ Setup Django
import django
django.setup()

# 4️⃣ Import models
from labs.models import Lab, LabSpecialists

# 5️⃣ Cleanup dangling Many-to-Many rows
valid_ids = set(LabSpecialists.objects.values_list('id', flat=True))

for lab in Lab.objects.all():
    current_ids = set(lab.specialists.values_list('id', flat=True))
    invalid_ids = current_ids - valid_ids
    if invalid_ids:
        print(f"Removing invalid IDs {invalid_ids} from Lab {lab.id}")
        lab.specialists.remove(*invalid_ids)

print("Cleanup completed successfully!")