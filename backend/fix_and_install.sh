#!/bin/bash

echo "========================================="
echo "Fixing Python 3.12 Compatibility Issues"
echo "========================================="

# Fix the setuptools issue first
echo "Step 1: Upgrading pip and setuptools..."
python3 -m pip install --break-system-packages --upgrade pip
python3 -m pip install --break-system-packages --upgrade setuptools wheel

# Install build tools
echo "Step 2: Installing build dependencies..."
python3 -m pip install --break-system-packages --upgrade setuptools-scm

# Now install the required packages
echo "Step 3: Installing AIDEPS dependencies..."

# Create a requirements file with compatible versions for Python 3.12
cat > requirements_fixed.txt << EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
clickhouse-driver==0.2.6
pandas==2.1.4
numpy==1.26.3
scikit-learn==1.4.0
scipy==1.12.0
openpyxl==3.1.2
pydantic==2.5.3
pydantic-settings==2.1.0
jinja2==3.1.3
matplotlib==3.8.2
seaborn==0.13.1
aiofiles==23.2.1
httpx==0.26.0
python-dotenv==1.0.0
EOF

echo "Installing from requirements file..."
python3 -m pip install --break-system-packages -r requirements_fixed.txt

# Verify installation
echo ""
echo "Step 4: Verifying installation..."
python3 << EOF
import sys
print(f"Python version: {sys.version}")

packages_to_check = [
    "fastapi",
    "uvicorn", 
    "clickhouse_driver",
    "pandas",
    "numpy",
    "sklearn",
    "scipy",
    "pydantic",
    "jinja2"
]

failed = []
for package in packages_to_check:
    try:
        __import__(package)
        print(f"✓ {package} imported successfully")
    except ImportError as e:
        print(f"✗ {package} failed: {e}")
        failed.append(package)

if not failed:
    print("\n✓ All core packages installed successfully!")
else:
    print(f"\n⚠ Failed packages: {', '.join(failed)}")
EOF

echo ""
echo "========================================="
echo "Setup complete! You can now run:"
echo "  python3 main.py"
echo "========================================="