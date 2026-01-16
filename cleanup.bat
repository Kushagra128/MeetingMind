@echo off
echo ========================================
echo Meeting Transcriber - Cleanup Script
echo ========================================
echo.

echo This script will clean up temporary and cache files.
echo.
echo What would you like to clean?
echo   1. Python cache files only (__pycache__, *.pyc)
echo   2. All cache files (Python + Node)
echo   3. User data (recordings, uploads, database)
echo   4. Everything (cache + user data)
echo   5. Cancel
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto clean_python
if "%choice%"=="2" goto clean_all_cache
if "%choice%"=="3" goto clean_user_data
if "%choice%"=="4" goto clean_everything
if "%choice%"=="5" goto cancel

echo Invalid choice. Exiting.
goto end

:clean_python
echo.
echo Cleaning Python cache files...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo Python cache cleaned!
goto end

:clean_all_cache
echo.
echo Cleaning all cache files...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo Python cache cleaned!
echo.
echo Note: To clean Node modules, run: cd frontend && rmdir /s /q node_modules && npm install
goto end

:clean_user_data
echo.
echo WARNING: This will delete all recordings, uploads, and the database!
set /p confirm="Are you sure? (yes/no): "
if not "%confirm%"=="yes" goto cancel

echo.
echo Cleaning user data...
if exist "backend\uploads\user_*" rmdir /s /q "backend\uploads\user_*"
if exist "iot-meeting-minutes\recordings\user_*" rmdir /s /q "iot-meeting-minutes\recordings\user_*"
if exist "iot-meeting-minutes\recordings\pdfs" rmdir /s /q "iot-meeting-minutes\recordings\pdfs"
if exist "data\meeting_transcriber.db" del /q "data\meeting_transcriber.db"
echo User data cleaned!
goto end

:clean_everything
echo.
echo WARNING: This will delete cache files AND all user data!
set /p confirm="Are you sure? (yes/no): "
if not "%confirm%"=="yes" goto cancel

echo.
echo Cleaning everything...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
if exist "backend\uploads\user_*" rmdir /s /q "backend\uploads\user_*"
if exist "iot-meeting-minutes\recordings\user_*" rmdir /s /q "iot-meeting-minutes\recordings\user_*"
if exist "iot-meeting-minutes\recordings\pdfs" rmdir /s /q "iot-meeting-minutes\recordings\pdfs"
if exist "data\meeting_transcriber.db" del /q "data\meeting_transcriber.db"
echo Everything cleaned!
goto end

:cancel
echo.
echo Cleanup cancelled.
goto end

:end
echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
pause
