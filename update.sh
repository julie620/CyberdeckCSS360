#!/bin/bash
cd /home/pi/CyberdeckCSS360
git pull
rm -rf api/venv
python3 -m venv api/venv
api/venv/bin/pip install -r api/requirements.txt
npm run build
cp cyberdeck.desktop /home/pi/.config/autostart/cyberdeck.desktop
sudo cp buttons.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart myapp
sudo systemctl restart buttons
echo "Done!"