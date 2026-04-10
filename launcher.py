"""
launcher.py – entry point for the Windows EXE build.

When run as a frozen PyInstaller bundle, this script:
  1. Changes the working directory to the EXE's folder so that mistakes.db
     is created next to the executable (not inside the temp extraction dir).
  2. Opens the default browser at http://localhost:8501 after a short delay.
  3. Starts Streamlit via its internal CLI.
"""

import os
import sys
import threading
import time
import webbrowser


def _open_browser() -> None:
    time.sleep(3)
    webbrowser.open("http://localhost:8501")


def _get_base_path() -> str:
    """Return the directory that contains app.py (bundled or source)."""
    if getattr(sys, "frozen", False):
        # PyInstaller extracts files to sys._MEIPASS
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    base_path = _get_base_path()
    app_path = os.path.join(base_path, "app.py")

    # Place the DB next to the executable when frozen, else in the source dir
    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))

    # Open browser in background
    threading.Thread(target=_open_browser, daemon=True).start()

    # Launch Streamlit
    from streamlit.web import cli as stcli  # noqa: PLC0415

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    stcli.main()
