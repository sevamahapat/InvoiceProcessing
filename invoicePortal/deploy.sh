#!/bin/bash
# Navigate to the repository directory
cd /home/site/wwwroot

# Activate virtual environment
python -m venv antenv
source antenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py runserver

