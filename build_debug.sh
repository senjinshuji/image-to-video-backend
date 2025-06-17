#!/bin/bash
set -e

echo "=== Render Build Debug Script ==="
echo "Python version:"
python --version || python3 --version
echo ""

echo "Pip version:"
pip --version || pip3 --version
echo ""

echo "Current directory:"
pwd
echo ""

echo "Directory contents:"
ls -la
echo ""

echo "Checking for requirements.txt:"
if [ -f requirements.txt ]; then
    echo "✓ requirements.txt found"
    echo "First 10 lines:"
    head -n 10 requirements.txt
else
    echo "✗ requirements.txt NOT FOUND!"
    exit 1
fi
echo ""

echo "Environment variables (non-sensitive):"
echo "DATABASE_URL is set: $([ -z "$DATABASE_URL" ] && echo "NO" || echo "YES")"
echo "JWT_SECRET_KEY is set: $([ -z "$JWT_SECRET_KEY" ] && echo "NO" || echo "YES")"
echo "OPENAI_API_KEY is set: $([ -z "$OPENAI_API_KEY" ] && echo "NO" || echo "YES")"
echo "KLING_ACCESS_KEY is set: $([ -z "$KLING_ACCESS_KEY" ] && echo "NO" || echo "YES")"
echo "KLING_SECRET_KEY is set: $([ -z "$KLING_SECRET_KEY" ] && echo "NO" || echo "YES")"
echo ""

echo "Upgrading pip..."
pip install --upgrade pip || pip3 install --upgrade pip
echo ""

echo "Installing requirements..."
pip install -r requirements.txt || pip3 install -r requirements.txt
echo ""

echo "Testing imports..."
python -c "import sys; print(f'Python path: {sys.path}')" || python3 -c "import sys; print(f'Python path: {sys.path}')"
echo ""

echo "Build completed successfully!"