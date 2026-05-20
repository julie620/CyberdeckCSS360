#!/bin/bash
set -e

echo "Installing myapp..."

# System dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm

# Python backend
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# React frontend (Vite build, run from root)
npm install
npm run build
# Vite outputs to dist/ by default

# .env reminder
echo ""
echo "⚠️  Make sure api/.env has your Spotify credentials"
echo "    nano api/.env"

# Systemd service
sed -i "s|HOME_DIR|$HOME|g" myapp.service
sudo cp myapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable myapp

echo ""
echo "✅ Done! Run 'sudo systemctl start myapp' to launch"
