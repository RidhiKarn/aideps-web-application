#!/bin/bash

echo "========================================"
echo "AIDEPS Frontend Quick Start"
echo "========================================"

# Clean previous installations
echo "Cleaning previous installations..."
rm -rf node_modules package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null

# Install with npm (faster for initial setup)
echo "Installing dependencies with npm..."
npm install --legacy-peer-deps

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  npm start"
echo ""
echo "The app will run on http://localhost:3000"
echo ""
echo "Login credentials:"
echo "  Email: demo@mospi.gov.in"
echo "  Password: demo123"
echo "========================================"