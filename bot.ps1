# Remove the .venv directory if it exists, with error handling
try {
    Remove-Item -Path ".venv" -Recurse -Force -ErrorAction Stop
} catch {
    Write-Host "Could not remove .venv: $($_.Exception.Message)"
}

python -m venv .venv

# Activate the virtual environment
& ".venv\Scripts\Activate.ps1"

# update pip to the latest version
python -m pip install --upgrade pip

# Install the required packages
pip install discord.py python-dotenv pillow PyNaCl
# Run the Python script using the virtual environment's Python interpreter
& ".venv\Scripts\python.exe" "C:\Users\Admin\Documents\GitHub\casino-bot\main.py"
