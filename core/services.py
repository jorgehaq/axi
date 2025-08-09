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
    



from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import math
import pandas as pd
import numpy as np


# -------------------
# Validación & helpers
# -------------------

ALLOWED_FILTER_OPS = {"eq", "ne", "gt", "gte", "lt", "lte", "contains", "in"}

def validate_columns(df: pd.DataFrame, cols: List[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Unknown column(s): {', '.join(missing)}")

def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def apply_filters(df: pd.DataFrame, filters: List[Tuple[str, str, str]]) -> pd.DataFrame:
    """
    filters: lista de tuplas (col, op, value); op∈ALLOWED_FILTER_OPS
      - eq/ne: igualdad/desigualdad
      - gt/gte/lt/lte: comparadores numéricos
      - contains: substring (case-insensitive)
      - in: lista separada por |
    """
    out = df.copy()
    for col, op, val in filters:
        if col not in out.columns:
            # columna inexistente => ignora filtro (KISS: alternativa es lanzar error)
            continue
        if op not in ALLOWED_FILTER_OPS:
            continue

        s = out[col]
        if op in {"gt", "gte", "lt", "lte"}:
            s_num = coerce_numeric(s)
            v = pd.to_numeric(val, errors="coerce")
            if pd.isna(v):
                continue
            if op == "gt":
                out = out[s_num > v]
            elif op == "gte":
                out = out[s_num >= v]
            elif op == "lt":
                out = out[s_num < v]
            else:
                out = out[s_num <= v]
        elif op == "eq":
            out = out[s.astype(str) == str(val)]
        elif op == "ne":
            out = out[s.astype(str) != str(val)]
        elif op == "contains":
            out = out[s.astype(str).str.contains(str(val), case=False, na=False)]
        elif op == "in":
            opts = [x.strip() for x in str(val).split("|") if x.strip()]
            out = out[s.astype(str).isin(opts)]
    return out

def select_columns(df: pd.DataFrame, columns: List[str] | None) -> pd.DataFrame:
    if not columns:
        return df
    validate_columns(df, columns)
    return df[columns]

def apply_sort(df: pd.DataFrame, sort_expr: str | None) -> pd.DataFrame:
    """
    sort_expr: "colA,-colB" (desc con prefijo '-')
    """
    if not sort_expr:
        return df
    keys = [k.strip() for k in sort_expr.split(",") if k.strip()]
    cols, ascending = [], []
    for k in keys:
        if k.startswith("-"):
            cols.append(k[1:])
            ascending.append(False)
        else:
            cols.append(k)
            ascending.append(True)
    # ignora columnas que no existan
    cols_exist = [c for c in cols if c in df.columns]
    if not cols_exist:
        return df
    asc = [ascending[i] for i, c in enumerate(cols) if c in cols_exist]
    return df.sort_values(by=cols_exist, ascending=asc, kind="mergesort")

def paginate(records: List[Dict[str, Any]], page: int, page_size: int) -> Dict[str, Any]:
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 50), 100))
    total = len(records)
    pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
        "items": records[start:end],
    }

# -------------------
# Analytics
# -------------------

def compute_correlation(df: pd.DataFrame, cols: List[str] | None = None) -> Dict[str, Dict[str, float]]:
    data = df
    if cols:
        validate_columns(df, cols)
        data = df[cols]
    corr = data.select_dtypes(include=["number"]).corr(numeric_only=True)
    if corr.empty:
        return {}
    # Convierte a dict de floats
    out: Dict[str, Dict[str, float]] = {}
    for c in corr.columns:
        out[c] = {r: (float(corr.loc[r, c]) if not pd.isna(corr.loc[r, c]) else None) for r in corr.index}
    return out

def compute_trend(
    df: pd.DataFrame, date_col: str, value_col: str, freq: str = "D", agg: str = "sum"
) -> List[Dict[str, Any]]:
    """
    freq: 'D' (día), 'W' (semana), 'M' (mes)
    agg: 'sum' | 'mean' | 'count'
    """
    validate_columns(df, [date_col, value_col])
    # Parseo de fecha
    dt = pd.to_datetime(df[date_col], errors="coerce", utc=False)
    ok_mask = ~dt.isna()
    df2 = df.loc[ok_mask].copy()
    if df2.empty:
        return []
    df2["_dt"] = dt[ok_mask]
    # Selección de agregador
    agg_fn = {"sum": "sum", "mean": "mean", "count": "count"}.get(agg, "sum")
    # Numérico si se requiere
    if agg in {"sum", "mean"}:
        df2[value_col] = coerce_numeric(df2[value_col])
    # Resample
    s = df2.set_index("_dt").resample(freq)[value_col].agg(agg_fn)
    s = s.dropna()
    return [{"date": i.isoformat(), value_col: float(v) if v is not None else None} for i, v in s.items()]
