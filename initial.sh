#!/bin/bash
# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')

# Check if Python version is 3.11
if [[ "$python_version" == "3.11"* ]]; then
    echo "Python 3.11 found. Continuing..."
    # Create a virtual environment
    python3.11 -m venv env
    # Activate the virtual environment
    source env/bin/activate
    # Install requirements
    pip install -r requirements.txt
    # Give execute permission to make-db.sh
    chmod +x make-db.sh
    # Run make-db.sh
    ./make-db.sh
    # Deactivate the virtual environment
    deactivate
else
    echo "Python 3.11 not found. Stopping..."
    exit 1
fi