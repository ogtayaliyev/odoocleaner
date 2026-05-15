@echo off
setlocal
title OdooExcelCleaner PORTABLE

:: Chemin du dossier actuel
set "base_dir=%~dp0"
cd /d "%base_dir%"

echo ============================================
echo   OdooExcelCleaner - VERSION PORTABLE 
echo ============================================
echo.
echo Initialisation du moteur interne...

:: Utilisation du Python portable interne
set "PYTHON_EXE=%base_dir%python_env\python.exe"
set "APP_DIR=%base_dir%app"

if not exist "%PYTHON_EXE%" (
    echo [ERREUR] Moteur Python introuvable dans %PYTHON_EXE%
    pause
    exit /b 1
)

echo Lancement de l'interface graphique...
echo.
echo --------------------------------------------
echo NE FERMEZ PAS CETTE FENETRE pendant l'utilisation.
echo L'application va s'ouvrir dans votre navigateur.
echo --------------------------------------------

:: Lancement via le Python portable
"%PYTHON_EXE%" -m streamlit run "%APP_DIR%\main.py" --server.port=8501 --server.headless=false --browser.gatherUsageStats=false

pause
