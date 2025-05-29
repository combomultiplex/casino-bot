# Update pip to the latest version using the venv's Python
& ".venv/Scripts/python.exe" -m pip install --upgrade pip

# Install the required packages using the venv's pip
& ".venv/Scripts/python.exe" -m pip install -r requirements.txt

# Run the Python script using the virtual environment's Python interpreter
& ".venv/Scripts/python.exe" main.py