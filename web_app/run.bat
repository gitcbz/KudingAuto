@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Kuding Judge Helper Web App...
echo Open your browser and go to: http://localhost:5000
echo.

python app.py
