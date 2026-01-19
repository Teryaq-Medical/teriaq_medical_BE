# Install dependencies
pip install -r requirements.txt

# Create the folder if it doesn't exist
mkdir -p staticfiles

# Collect static files
python3.9 manage.py collectstatic --no-input --clear