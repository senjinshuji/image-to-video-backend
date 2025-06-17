#!/bin/bash
set -e

echo "=== Render Build Script ==="
echo "Python version:"
python --version
echo ""

echo "Upgrading pip..."
pip install --upgrade pip
echo ""

echo "Installing requirements..."
pip install -r requirements.txt
echo ""

echo "Build completed successfully!"