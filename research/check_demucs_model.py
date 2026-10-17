"""Minimal prerequisite check for an isolated Demucs worker."""
from pathlib import Path
import importlib.util
import json

MODEL = "htdemucs"
CHECKPOINT = "955717e8-8726e21a.th"

def status():
    checkpoint = Path.home()/".cache"/"torch"/"hub"/"checkpoints"/CHECKPOINT
    return {
        "demucs_installed": importlib.util.find_spec("demucs") is not None,
        "model": MODEL,
        "checkpoint_cached": checkpoint.is_file(),
    }

if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
