from pathlib import Path
def Name(path: str) -> str:
    py_path = Path(path)
    return py_path.name