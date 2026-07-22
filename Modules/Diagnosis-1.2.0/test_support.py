from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.mkdtemp(prefix="diagnosis-suite-")
TEST_DB_PATH = str(Path(_TEST_DB_DIR) / "diagnosis.db")
os.environ.setdefault("DIAGNOSIS_DB_PATH", TEST_DB_PATH)
atexit.register(shutil.rmtree, _TEST_DB_DIR, True)

