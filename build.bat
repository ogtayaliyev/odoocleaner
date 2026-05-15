# build.bat — Script de build PyInstaller : génère l'exécutable OdooExcelCleaner.exe

@echo off
chcp 65001 > nul
echo ============================================
echo   Build OdooExcelCleaner - PyInstaller
echo ============================================

:: Vérification de l'environnement Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python introuvable dans le PATH.
    pause
    exit /b 1
)

:: Installation des dépendances
echo [1/4] Installation des dependances...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)

:: Nettoyage des anciens builds
echo [2/4] Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
if exist OdooExcelCleaner.spec del /f /q OdooExcelCleaner.spec

:: Build PyInstaller
echo [3/4] Build PyInstaller en cours (peut prendre plusieurs minutes)...
pyinstaller ^
    --onefile ^
    --name OdooExcelCleaner ^
    --icon=assets\icon.ico ^
    --add-data "main.py;." ^
    --add-data "modules;modules" ^
    --add-data "config;config" ^
    --hidden-import streamlit ^
    --hidden-import streamlit.web.cli ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import xlsxwriter ^
    --hidden-import altair ^
    --hidden-import pyarrow ^
    --hidden-import pydeck ^
    --collect-all streamlit ^
    --collect-all altair ^
    launcher.py

if %errorlevel% neq 0 (
    echo [ERREUR] Echec du build PyInstaller.
    pause
    exit /b 1
)

:: Copie du mapping.json dans dist
echo [4/4] Copie des ressources...
if not exist dist\config mkdir dist\config
copy config\mapping.json dist\config\mapping.json >nul

echo.
echo ============================================
echo   Build termine avec succes !
echo   Executable : dist\OdooExcelCleaner.exe
echo ============================================
echo.
echo Lancez ensuite Inno Setup avec setup.iss
echo pour generer l'installateur Windows.
pause
