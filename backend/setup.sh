#!/bin/bash

echo "========================================="
echo "Setting up AIDEPS Backend"
echo "========================================="

# Install required Python packages
echo "Installing Python dependencies in global environment..."

# Core dependencies with specific versions that work
pip install --break-system-packages fastapi==0.104.1
pip install --break-system-packages uvicorn[standard]==0.24.0
pip install --break-system-packages python-multipart==0.0.6
pip install --break-system-packages clickhouse-driver==0.2.6
pip install --break-system-packages pandas==2.1.3
pip install --break-system-packages numpy==1.24.3
pip install --break-system-packages scikit-learn==1.3.2
pip install --break-system-packages scipy==1.11.4
pip install --break-system-packages openpyxl==3.1.2
pip install --break-system-packages pydantic==2.5.0
pip install --break-system-packages pydantic-settings==2.1.0
pip install --break-system-packages jinja2==3.1.2
pip install --break-system-packages matplotlib==3.8.2
pip install --break-system-packages seaborn==0.13.0
pip install --break-system-packages aiofiles==23.2.1

echo ""
echo "✓ Dependencies installed!"
echo ""
echo "Now you can start the backend server:"
echo "  python main.py"
echo ""
echo "The server will run on: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "========================================="