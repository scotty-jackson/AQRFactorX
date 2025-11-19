#!/bin/bash
# Setup script for AQR data management tools

echo "Setting up AQR data management environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To use the scripts:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run scripts: python preview_dataset.py"
echo ""
