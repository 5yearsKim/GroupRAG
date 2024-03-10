

def set_python_path() -> None:
    import sys
    from pathlib import Path

    # Add the parent directory of 'scripts' to sys.path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
