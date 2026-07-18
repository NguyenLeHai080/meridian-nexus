import os
import tempfile
from pathlib import Path

database_file = Path(tempfile.gettempdir()) / "northstar-api-tests.sqlite"
database_file.unlink(missing_ok=True)
os.environ["APP_KEY"] = "test-key-that-is-at-least-thirty-two-characters-long"
os.environ["DATABASE_URL"] = f"sqlite:///{database_file.as_posix()}"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"
os.environ["TRUSTED_HOSTS"] = "testserver,localhost"
