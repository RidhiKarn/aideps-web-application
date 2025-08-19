#!/bin/bash

echo "========================================="
echo "Installing AIDEPS Backend Dependencies"
echo "========================================="

# Function to install package
install_package() {
    echo "Installing $1..."
    pip install --break-system-packages "$1" 2>/dev/null || echo "  ⚠ Skipped: $1"
}

# Core web framework
install_package "fastapi"
install_package "uvicorn"
install_package "python-multipart"

# Database
install_package "clickhouse-driver"

# Data processing (these should already be installed)
install_package "pandas"
install_package "numpy"

# Try newer scikit-learn if old version fails
pip install --break-system-packages scikit-learn 2>/dev/null || echo "  ⚠ Skipped: scikit-learn"

# Other dependencies
install_package "scipy"
install_package "openpyxl"
install_package "pydantic"
install_package "pydantic-settings"
install_package "jinja2"
install_package "aiofiles"

# Optional visualization (may fail but not critical)
pip install --break-system-packages matplotlib 2>/dev/null || echo "  ⚠ Skipped: matplotlib"
pip install --break-system-packages seaborn 2>/dev/null || echo "  ⚠ Skipped: seaborn"

echo ""
echo "========================================="
echo "Installation complete!"
echo ""
echo "Testing imports..."
python3 -c "import fastapi; import uvicorn; print('✓ Core packages working')" 2>/dev/null || echo "✗ Some imports failed"
echo ""
echo "You can now run: python main.py"
echo "========================================="