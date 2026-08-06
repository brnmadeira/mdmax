@echo off
cd /d "C:\Users\marke\AppData\Roaming\Claude\skills\auto-convert-to-markdown"
python monitor_repo.py continuous 300
pause
