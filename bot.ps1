# Remove existing virtual environment if it exists
if (Test-Path "$PSScriptRoot\.venv") {
    Remove-Item -Recurse -Force "$PSScriptRoot\.venv"
}

# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

# Ensure pip is up to date
python -m pip install --upgrade pip

# Install required packages from requirements.txt if it exists, else install manually
if (Test-Path "$PSScriptRoot\requirements.txt") {
    python -m pip install -r "$PSScriptRoot\requirements.txt"
} else {
    python -m pip install discord.py python-dotenv pillow PyNaCl sqlalchemy psycopg2
}

# Run the bot
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\main.py"