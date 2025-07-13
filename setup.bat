@echo off
echo Vietnamese Interpreter POC Setup
echo ================================

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Creating sample directories...
mkdir data\input 2>nul
mkdir data\output 2>nul
mkdir models 2>nul
mkdir logs 2>nul

echo.
echo Setup completed!
echo.
echo To run the interpreter:
echo 1. Place audio files in data\input\
echo 2. Run: python src\main.py data\input\your_file.wav
echo.
echo Example audio files for testing can be found online or recorded locally.
pause
