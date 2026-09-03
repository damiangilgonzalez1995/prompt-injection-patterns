import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Blueprint tests always run offline against the injectable mock.
os.environ["PIP_MODE"] = "mock"
