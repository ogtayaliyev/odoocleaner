# launcher.py — Point d'entrée PyInstaller : lance Streamlit en sous-processus et ouvre le navigateur automatiquement

import sys
import os
import subprocess
import threading
import time
import webbrowser


def get_base_path() -> str:
    """Retourne le chemin de base compatible mode développement et mode PyInstaller (.exe)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def open_browser(url: str, delay: float = 3.0) -> None:
    """Ouvre le navigateur après un délai pour laisser Streamlit démarrer."""
    time.sleep(delay)
    webbrowser.open(url)


def main() -> None:
    base_path = get_base_path()
    main_script = os.path.join(base_path, "main.py")
    port = 8501
    url = f"http://localhost:{port}"

    # Chemin vers Python embarqué ou système
    python_exec = sys.executable

    # Construction de la commande Streamlit
    cmd = [
        python_exec,
        "-m",
        "streamlit",
        "run",
        main_script,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]

    # Si on est dans un exe PyInstaller, streamlit run ne marche pas directement
    # On utilise le module streamlit directement
    if getattr(sys, "frozen", False):
        cmd = [
            python_exec,
            "-c",
            (
                "import streamlit.web.cli as stcli; import sys; "
                f"sys.argv = ['streamlit', 'run', r'{main_script}', "
                f"'--server.port', '{port}', "
                "'--server.headless', 'true', "
                "'--server.enableCORS', 'false', "
                "'--browser.gatherUsageStats', 'false']; "
                "stcli.main()"
            ),
        ]

    # Lancer le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, args=(url, 3.0), daemon=True)
    browser_thread.start()

    # Lancer Streamlit (bloquant)
    env = os.environ.copy()
    env["PYTHONPATH"] = base_path
    
    # Ajouts pour débogage et stabilité
    import sys
    with open(os.path.join(os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else base_path, "streamlit_log.txt"), "w") as log_file:
        log_file.write(f"Starting command: {cmd}\n")
        process = subprocess.Popen(cmd, env=env, cwd=base_path, stdout=log_file, stderr=log_file)
        process.wait()


if __name__ == "__main__":
    # Protection critique contre le spawn infini
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Empêcher la récursion si le script est appelé par Streamlit ou Multiprocessing
    import sys
    # Ignorer si c'est un processus enfant de multiprocessing ou si streamlit est déjà dans les arguments
    if '--multiprocessing-fork' in sys.argv or 'run' in sys.argv:
        pass
    else:
        main()
