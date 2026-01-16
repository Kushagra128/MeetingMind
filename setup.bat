@echo off
echo ========================================
echo MeetingMing - Setup Script
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

cd ..
echo.

echo [2/4] Setting up Frontend...
cd frontend
echo Installing Node dependencies...
call npm install

cd ..
echo.

echo [3/4] Creating necessary directories...
if not exist "data" mkdir data
if not exist "backend\uploads" mkdir backend\uploads
if not exist "iot-meeting-minutes\recordings" mkdir iot-meeting-minutes\recordings
echo.

echo [4/4] Checking Vosk model...
if exist "models\vosk-model-small-en-in-0.4" (
    echo Vosk model found!
) else (
    echo WARNING: Vosk model not found in models/ directory
    echo Please download a model from https://alphacephei.com/vosk/models
    echo and extract it to the models/ directory
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Backend:  cd backend ^&^& python app.py
echo   2. Frontend: cd frontend ^&^& npm run dev
echo.
echo See docs/QUICKSTART.md for more details
echo.
pause
