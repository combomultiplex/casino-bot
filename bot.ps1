# Remove venv if it exists
if (Test-Path -Path "venv") {
    Remove-Item -Recurse -Force "venv"
}

# Create venv
python -m venv venv

# Activate venv
& ".\venv\Scripts\Activate.ps1"

# Update pip
python -m pip install --upgrade pip

# Install requirements
pip install discord.py python-dotenv pillow sqlalchemy PyNaCl

# Run bot
python -m main