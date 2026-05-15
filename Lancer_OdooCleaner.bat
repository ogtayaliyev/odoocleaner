@echo off
setlocal
title OdooExcelCleaner - Démarrage...

:: Récupération du chemin du dossier actuel
set "base_dir=%~dp0"
cd /d "%base_dir%"

echo ============================================
echo   Lancement de OdooExcelCleaner (Streamlit)
echo ============================================
echo.

:: Vérification de la présence de Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH.
    pause
    exit /b 1
)

:: Installation discrète des dépendances si nécessaire
echo [1/2] Verification des composants...
pip install -r requirements.txt --quiet

:: Lancement de Streamlit
echo [2/2] demarrage de l'interface graphique...
echo.
echo L'application va s'ouvrir dans votre navigateur.
echo Gardez cette fenêtre ouverte tant que vous utilisez l'outil.
echo.

python -m streamlit run main.py --server.headless=false --server.port=8501 --browser.gatherUsageStats=false

pause
