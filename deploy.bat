@echo off
REM MeetingMing Deployment Script for Windows
REM This script helps deploy MeetingMing using Docker

echo ==========================================
echo MeetingMing Deployment Script
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [OK] Created .env file
    echo [WARNING] Please review and update .env file with your configuration
    echo.
)

REM Create necessary directories
echo Creating necessary directories...
if not exist data mkdir data
if not exist backend\uploads mkdir backend\uploads
if not exist iot-meeting-minutes\recordings mkdir iot-meeting-minutes\recordings
if not exist logs mkdir logs
echo [OK] Directories created
echo.

REM Ask user what to do
echo What would you like to do?
echo 1) Build and start containers
echo 2) Stop containers
echo 3) View logs
echo 4) Rebuild containers (clean build)
echo 5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto logs
if "%choice%"=="4" goto rebuild
if "%choice%"=="5" goto end
goto invalid

:start
echo.
echo Building and starting containers...
docker-compose up -d --build
echo.
echo [OK] Deployment complete!
echo.
echo Access MeetingMing at: http://localhost
echo Backend API at: http://localhost:5000
echo.
echo View logs with: docker-compose logs -f
echo Stop with: docker-compose down
pause
goto end

:stop
echo.
echo Stopping containers...
docker-compose down
echo [OK] Containers stopped
pause
goto end

:logs
echo.
echo Viewing logs (Ctrl+C to exit)...
docker-compose logs -f
goto end

:rebuild
echo.
echo Rebuilding containers (this may take a while)...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo [OK] Rebuild complete!
pause
goto end

:invalid
echo [ERROR] Invalid choice
pause
goto end

:end
echo.
echo Goodbye!
