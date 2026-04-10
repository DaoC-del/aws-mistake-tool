"""
launcher.py – entry point for the Windows EXE build.

When run as a frozen PyInstaller bundle, this script:
  1. Changes the working directory to the EXE's folder so that mistakes.db
     is created next to the executable (not inside the temp extraction dir).
  2. Forces Streamlit into production mode via environment variables so the
     server can bind to a fixed port without errors (see note below).
  3. Opens the default browser at http://localhost:8501 after a short delay.
  4. Starts Streamlit via its internal CLI.

Note – why the env-var approach is needed
------------------------------------------
PyInstaller frozen apps trigger Streamlit's ``global.developmentMode = True``
because Streamlit cannot find its own script on ``sys.argv[0]`` inside the
bundle.  When ``global.developmentMode`` is ``True``, Streamlit's config
validator raises::

    RuntimeError: server.port does not work when global.developmentMode is true.

Setting ``STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false`` (and the other server
variables) via *environment variables* before Streamlit boots bypasses this
validator entirely and ensures the app starts reliably in production mode.
"""

import os
import sys
import threading
import time
import webbrowser

# ---------------------------------------------------------------------------
# Force production mode BEFORE importing Streamlit.
# Streamlit reads these env-vars during its first import / config bootstrap,
# so they must be set here, before ``stcli.main()`` is called.
# ---------------------------------------------------------------------------
os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")


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

    # Launch Streamlit.  Server config is already provided via env-vars above;
    # passing --server.port here would re-trigger the developmentMode check.
    from streamlit.web import cli as stcli  # noqa: PLC0415

    sys.argv = ["streamlit", "run", app_path]
    stcli.main()
