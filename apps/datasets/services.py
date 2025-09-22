from typing import Any, Dict, List, Tuple
import pandas as pd


class DataReadError(Exception):
    pass


def safe_read_csv(file_path: str, nrows: int | None = None) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, nrows=nrows, dtype_backend="pyarrow")
    except pd.errors.EmptyDataError:
        raise DataReadError("Empty file")
    except pd.errors.ParserError:
        raise DataReadError("Invalid CSV format")
    except Exception as e:
        raise DataReadError(f"Error reading file: {e}")


def validate_columns(df: pd.DataFrame, cols: List[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def select_columns(df: pd.DataFrame, columns: List[str] | None) -> pd.DataFrame:
    if not columns:
        return df
    validate_columns(df, columns)
    return df[columns]


def _op_filter(series: pd.Series, op: str, value: str) -> pd.Series:
    if op == 'eq':
        return series == value
    if op == 'neq':
        return series != value
    if op == 'gt':
        return series.astype(float) > float(value)
    if op == 'gte':
        return series.astype(float) >= float(value)
    if op == 'lt':
        return series.astype(float) < float(value)
    if op == 'lte':
        return series.astype(float) <= float(value)
    if op == 'contains':
        return series.astype(str).str.contains(value, na=False)
    if op == 'in':
        values = set(value.split('|'))
        return series.astype(str).isin(values)
    raise ValueError(f"Invalid op: {op}")


def apply_filters(df: pd.DataFrame, filters: List[Tuple[str, str, str]]) -> pd.DataFrame:
    for col, op, val in filters:
        if col not in df.columns:
            continue
        mask = _op_filter(df[col], op, val)
        df = df[mask]
    return df


def apply_sort(df: pd.DataFrame, sort_expr: str | None) -> pd.DataFrame:
    if not sort_expr:
        return df
    fields = []
    ascending = []
    for part in sort_expr.split(','):
        part = part.strip()
        if part.startswith('-'):
            fields.append(part[1:])
            ascending.append(False)
        else:
            fields.append(part)
            ascending.append(True)
    return df.sort_values(by=fields, ascending=ascending)


def paginate(records: List[Dict[str, Any]], page: int, page_size: int) -> Dict[str, Any]:
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": records[start:end],
    }


def compute_correlation(df: pd.DataFrame, cols: List[str] | None = None) -> Dict[str, Dict[str, float]]:
    if cols:
        validate_columns(df, cols)
        df = df[cols]
    numeric_df = df.select_dtypes(include=["number"])  # solo numéricas
    if numeric_df.empty:
        return {}
    corr = numeric_df.corr(numeric_only=True)
    return {c: corr[c].to_dict() for c in corr.columns}


def compute_trend(df: pd.DataFrame, date_col: str, value_col: str, freq: str, agg: str) -> Dict[str, Any]:
    if date_col not in df.columns:
        raise ValueError("Missing date column")
    if agg != "count" and value_col not in df.columns:
        raise ValueError("Missing value column for non-count agg")

    s = pd.to_datetime(df[date_col], errors='coerce')
    df = df.assign(_date=s)
    if agg == 'count':
        out = df.set_index('_date').resample(freq)[date_col].count()
    elif agg == 'sum':
        out = df.set_index('_date').resample(freq)[value_col].sum()
    elif agg == 'mean':
        out = df.set_index('_date').resample(freq)[value_col].mean()
    else:
        raise ValueError("Invalid agg")
    return {str(k.date()): (float(v) if v is not None else None) for k, v in out.items()}

