#!/bin/bash
cd /home/pi/CyberdeckCSS360
git pull
source api/venv/bin/activate
pip install -r api/requirements.txt
deactivate
npm run build
cp cyberdeck.desktop /home/pi/.config/autostart/cyberdeck.desktop
sudo systemctl restart myapp
echo "Done!"