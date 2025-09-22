import json
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from datetime import timedelta
import pandas as pd
import io

from .models import Token, DataFile
from .permissions import IsOwnerOfDataFile
from .services import (
    safe_read_csv, DataReadError,
    select_columns, apply_filters, apply_sort, paginate,
    compute_correlation, compute_trend
)
from .serializers import TrendParamsSerializer, RowsParamsSerializer, FileUploadSerializer


def _json_error(message: str, status: int = 400):
    return JsonResponse({"error": message}, status=status)


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        data = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return HttpResponseBadRequest("username and password are required")
    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    token = Token.create_for(user)
    return JsonResponse({"token": token.key})


def _parse_filters(request):
    raw = request.query_params.getlist("f")
    out = []
    for item in raw:
        parts = [p.strip() for p in item.split(",")]
        if len(parts) >= 3:
            col, op, value = parts[0], parts[1], ",".join(parts[2:])
            out.append((col, op, value))
    return out


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    try:
        from django.core.files.storage import default_storage
        default_storage.listdir('.')
        storage_status = "ok"
    except Exception as e:
        storage_status = f"error: {str(e)}"
    return Response({
        "status": "ok" if db_status == "ok" and storage_status == "ok" else "degraded",
        "database": db_status,
        "storage": storage_status
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_view(request):
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": {"code": "bad_request", "message": serializer.errors}}, status=400)
    datafile = DataFile.objects.create(file=serializer.validated_data["file"], uploaded_by=request.user)
    return Response({"message": "File uploaded successfully", "id": datafile.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_preview(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        with datafile.file.open('r') as f:
            df = pd.read_csv(f, nrows=5, dtype_backend="pyarrow")
    except pd.errors.EmptyDataError:
        return Response({"error": {"code":"bad_request","message": "Empty file"}}, status=400)
    except pd.errors.ParserError:
        return Response({"error": {"code":"bad_request","message": "Invalid CSV format"}}, status=400)
    rows = df.head(5).to_dict(orient="records")
    return Response({"id": datafile.id, "rows": rows})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_summary(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        with datafile.file.open('r') as f:
            df = pd.read_csv(f, dtype_backend="pyarrow")
    except Exception as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return Response({"id": datafile.id, "summary": {}})
    desc = numeric_df.describe()
    subset = desc.loc[["count", "mean", "std"]].to_dict()
    summary = {col: {k: (float(v) if v is not None else None) for k, v in stats.items()} for col, stats in subset.items()}
    return Response({"id": datafile.id, "summary": summary})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_rows(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        with datafile.file.open('r') as f:
            df = pd.read_csv(f, dtype_backend="pyarrow")
    except Exception as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)
    params = RowsParamsSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    columns = params.validated_data.get("columns")
    columns = [c.strip() for c in columns.split(",")] if columns else None
    filters = _parse_filters(request)
    df = apply_filters(df, filters)
    df = select_columns(df, columns)
    df = apply_sort(df, params.validated_data.get("sort"))
    payload = paginate(df.to_dict(orient="records"), params.validated_data["page"], params.validated_data["page_size"])
    return Response(payload)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_correlation(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        with datafile.file.open('r') as f:
            df = pd.read_csv(f, dtype_backend="pyarrow")
    except Exception as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)
    cols = request.query_params.get("cols")
    cols = [c.strip() for c in cols.split(",")] if cols else None
    try:
        corr = compute_correlation(df, cols)
    except ValueError as ve:
        return Response({"error": {"code":"bad_request","message": str(ve)}}, status=400)
    return Response({"id": datafile.id, "correlation": corr})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_trend(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        with datafile.file.open('r') as f:
            df = pd.read_csv(f, dtype_backend="pyarrow")
    except Exception as e:
        return _json_error(str(e), status=400)
    params = TrendParamsSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    date_col = params.validated_data['date']
    value_col = params.validated_data.get('value')
    freq = params.validated_data['freq']
    agg = params.validated_data['agg']
    if agg != "count" and not value_col:
        return _json_error("Missing 'value' parameter for agg != count", status=400)
    if freq not in {"D", "W", "M"}:
        return _json_error("Invalid freq (use D, W, or M)", status=400)
    if agg not in {"sum", "mean", "count"}:
        return _json_error("Invalid agg (use sum, mean, or count)", status=400)
    try:
        out = compute_trend(df, date_col=date_col, value_col=(value_col or date_col), freq=freq, agg=agg)
    except ValueError as ve:
        return _json_error(str(ve), status=400)
    return JsonResponse({"id": datafile.id, "trend": out})


@api_view(["GET"])   
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def get_download_url(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    return Response({
        "download_url": request.build_absolute_uri(datafile.file.url),
        "expires_in": 900,
        "filename": datafile.file.name,
        "type": "direct",
        "storage": "local"
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bulk_upload_view(request):
    files = request.FILES.getlist('files')
    if not files:
        return Response({"error": {"code": "bad_request", "message": "No files provided"}}, status=400)
    results = []
    for file in files:
        if not file.name.endswith('.csv'):
            results.append({"filename": file.name, "status": "error", "message": "Only CSV files allowed"})
            continue
        try:
            datafile = DataFile.objects.create(file=file, uploaded_by=request.user)
            results.append({"filename": file.name, "status": "success", "id": datafile.id})
        except Exception as e:
            results.append({"filename": file.name, "status": "error", "message": str(e)})
    return Response({"results": results})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def bulk_delete_view(request):
    ids = request.data.get('ids', [])
    if not ids or not isinstance(ids, list):
        return Response({"error": {"code": "bad_request", "message": "Missing or invalid 'ids' array"}}, status=400)
    user_files = DataFile.objects.filter(id__in=ids, uploaded_by=request.user)
    deleted_count = user_files.count()
    user_files.delete()
    return Response({"message": f"Deleted {deleted_count} datasets", "deleted_ids": list(ids[:deleted_count])})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cohort_analysis_view(request, id):
    try:
        dataset = DataFile.objects.get(id=id, uploaded_by=request.user)
        dataset.file.seek(0)
        file_content = dataset.file.read()
        df = pd.read_csv(io.BytesIO(file_content))
        required_cols = ['user_id', 'registration_date', 'activity_date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return Response({
                "error": f"Missing required columns: {missing_cols}",
                "required": required_cols,
                "available": list(df.columns)
            }, status=400)
        result = {
            "cohorts": {},
            "retention": {}
        }
        return Response({
            "dataset_id": id,
            "analysis_type": "cohort_retention",
            "results": result
        })
    except DataFile.DoesNotExist:
        return Response({"error": "Dataset not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })
