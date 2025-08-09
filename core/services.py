from pathlib import Path
import pandas as pd

class DataReadError(Exception):
    pass

def safe_read_csv(file_path: str, nrows: int | None = None) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise DataReadError("File not found")
    try:
        # dtype_backend="pyarrow" mantiene números/NaN mejor
        df = pd.read_csv(path, nrows=nrows, dtype_backend="pyarrow")
        return df
    except pd.errors.EmptyDataError:
        raise DataReadError("Empty file")
    except pd.errors.ParserError:
        raise DataReadError("Invalid CSV format")
    except Exception as e:
        raise DataReadError(f"Unexpected error: {e}")