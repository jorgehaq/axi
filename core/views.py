import json
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Token, DataFile
from drf_spectacular.utils import extend_schema, OpenApiParameter
# from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# from google.cloud import storage
from django.conf import settings
from datetime import timedelta
# import logging
from .permissions import IsOwnerOfDataFile
from .services import (
    safe_read_csv, DataReadError,
    select_columns, apply_filters, apply_sort, paginate,
    compute_correlation, compute_trend,
)
from .serializers import TrendParamsSerializer, RowsParamsSerializer, FileUploadSerializer

def _json_error(message: str, status: int = 400):
    from django.http import JsonResponse
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
    # ?f=col,op,val (repetible)
    raw = request.query_params.getlist("f")
    out = []
    for item in raw:
        parts = [p.strip() for p in item.split(",")]
        if len(parts) >= 3:
            col, op, value = parts[0], parts[1], ",".join(parts[2:])
            out.append((col, op, value))
    return out


def _parse_filters2(request):
    """
    Espera filtros repetibles:
      ?f=col,op,value
    Ejemplos:
      ?f=country,eq,CO
      ?f=amount,gte,100
      ?f=name,contains,foo
      ?f=status,in,active|pending
    """
    raw = request.GET.getlist("f")
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
    return Response({"status": "ok"})

"""
def health(request):
    return JsonResponse({"status": "ok"})
"""

@extend_schema(
    request=FileUploadSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "id": {"type": "integer"}
            }
        },
        400: {
            "type": "object", 
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            "Upload exitoso",
            value={"message": "File uploaded successfully", "id": 1},
            response_only=True,
        )
    ],
    summary="Subir archivo CSV",
    description="Sube un archivo CSV para análisis. El archivo debe tener extensión .csv"
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_view(request):
    # Validar con serializer
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": {"code": "bad_request", "message": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear el archivo
    datafile = DataFile.objects.create(
        file=serializer.validated_data["file"], 
        uploaded_by=request.user
    )
    
    return Response({
        "message": "File uploaded successfully", 
        "id": datafile.id
    })


"""
def _require_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Token "):
        return None
    key = auth.split(" ", 1)[1].strip()
    try:
        return Token.objects.select_related("user").get(key=key).user
    except Token.DoesNotExist:
        return None


@csrf_exempt
def upload_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    user = _require_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if "file" not in request.FILES:
        return HttpResponseBadRequest("CSV file is required (multipart/form-data, field name 'file')")

    upload: UploadedFile = request.FILES["file"]
    # KISS: no validamos CSV aún, solo guardamos
    datafile = DataFile.objects.create(file=upload, uploaded_by=user)
    return JsonResponse({"message": "File uploaded successfully", "id": datafile.id})
"""




@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_preview(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    try:
        df = safe_read_csv(datafile.file.path, nrows=5)
    except DataReadError as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)
    return Response({"id": datafile.id, "rows": df.head(5).to_dict(orient="records")})

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_summary(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return Response({"id": datafile.id, "summary": {}})

    desc = numeric_df.describe()
    subset = desc.loc[["count", "mean", "std"]].to_dict()
    summary = {col: {k: (float(v) if v is not None else None) for k, v in stats.items()}
               for col, stats in subset.items()}
    return Response({"id": datafile.id, "summary": summary})


@require_GET
def data_summary2(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return _json_error(str(e), status=400)

    # Solo columnas numéricas
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return JsonResponse({"id": datafile.id, "summary": {} })

    desc = numeric_df.describe()  # count, mean, std, min, 25%, 50%, 75%, max
    # KISS: entregamos solo count, mean, std como pidió el roadmap
    subset = desc.loc[["count", "mean", "std"]].to_dict()
    # Asegura tipos serializables
    summary = {col: {k: (float(v) if v is not None else None) for k, v in stats.items()}
               for col, stats in subset.items()}
    return JsonResponse({"id": datafile.id, "summary": summary})





@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_rows(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)

    params = RowsParamsSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)

    columns = params.validated_data.get("columns")
    columns = [c.strip() for c in columns.split(",")] if columns else None
    filters = _parse_filters(request)
    df = apply_filters(df, filters)
    df = select_columns(df, columns)
    df = apply_sort(df, params.validated_data.get("sort"))
    payload = paginate(df.to_dict(orient="records"),
                       params.validated_data["page"],
                       params.validated_data["page_size"])
    return Response(payload)


@require_GET
def data_rows2(request, id: int):
    """
    Lista filas con filtros, selección de columnas, orden y paginación.
    Params:
      - columns=a,b,c
      - f=col,op,val  (repetible)
      - sort=colA,-colB
      - page=1&page_size=50
    """
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return _json_error(str(e), status=400)

    # Selección de columnas
    columns = request.GET.get("columns")
    columns = [c.strip() for c in columns.split(",")] if columns else None

    # Filtros
    filters = _parse_filters(request)
    df = apply_filters(df, filters)
    df = select_columns(df, columns)

    # Orden
    sort_expr = request.GET.get("sort")
    df = apply_sort(df, sort_expr)

    # Serializa y pagina
    records = df.to_dict(orient="records")
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 50))
    payload = paginate(records, page, page_size)
    return JsonResponse(payload)







@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_correlation(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)

    cols = request.query_params.get("cols")
    cols = [c.strip() for c in cols.split(",")] if cols else None
    try:
        corr = compute_correlation(df, cols)
    except ValueError as ve:
        return Response({"error": {"code":"bad_request","message": str(ve)}}, status=400)
    return Response({"id": datafile.id, "correlation": corr})



@require_GET
def data_correlation_otro(request, id: int):
    """
    Correlación Pearson simple.
    Params:
      - cols=a,b,c (opcional; si no, usa numéricas)
    """
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return _json_error(str(e), status=400)

    cols = request.GET.get("cols")
    cols = [c.strip() for c in cols.split(",")] if cols else None
    try:
        corr = compute_correlation(df, cols)
    except ValueError as ve:
        return _json_error(str(ve), status=400)
    return JsonResponse({"id": datafile.id, "correlation": corr})







@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def data_trend(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    params = TrendParamsSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    date_col = params.validated_data["date"]
    value_col = params.validated_data.get("value")
    freq = params.validated_data["freq"]
    agg = params.validated_data["agg"]

    if agg != "count" and not value_col:
        return Response({"error":{"code":"bad_request","message":"Missing 'value' parameter for agg != count"}}, status=400)

    try:
        out = compute_trend(
            safe_read_csv(datafile.file.path),
            date_col=date_col, value_col=value_col or date_col, freq=freq, agg=agg
        )
    except (ValueError, DataReadError) as e:
        return Response({"error": {"code":"bad_request","message": str(e)}}, status=400)

    return Response({"id": datafile.id, "trend": out})


@require_GET
def data_trend2(request, id: int):
    """
    Trends básicos por fecha.
    Params:
      - date=<col_fecha> (requerido)
      - value=<col_numerica> (requerido si agg != count)
      - freq=D|W|M (def D)
      - agg=sum|mean|count (def sum)
    """
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        df = safe_read_csv(datafile.file.path)
    except DataReadError as e:
        return _json_error(str(e), status=400)

    date_col = request.GET.get("date")
    value_col = request.GET.get("value")
    freq = request.GET.get("freq", "D").upper()
    agg = request.GET.get("agg", "sum").lower()

    if not date_col:
        return _json_error("Missing 'date' parameter", status=400)
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
def get_download_url_2(request, id: int):
    """Generate download URL (local or GCS based on configuration)"""
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    
    # Check if GCS is enabled
    use_gcs = getattr(settings, 'USE_GCS', False)
    
    if not use_gcs:
        # LOCAL DEVELOPMENT: Return direct media URL
        logger.info(f"🔧 Using local storage for file {datafile.file.name}")
        
        return Response({
            "download_url": request.build_absolute_uri(datafile.file.url),
            "expires_in": 900,  # 15 min (mock)
            "filename": datafile.file.name,
            "file_size": datafile.file.size,
            "type": "direct",
            "storage": "local"
        })
    
    # GCS PRODUCTION: Generate signed URL
    try:
        from google.cloud import storage
        
        logger.info(f"🌤️ Using GCS storage for file {datafile.file.name}")
        
        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        blob = bucket.blob(datafile.file.name)
        
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET"
        )
        
        return Response({
            "download_url": signed_url,
            "expires_in": 900,  # 15 min
            "filename": datafile.file.name,
            "file_size": datafile.file.size,
            "type": "signed",
            "storage": "gcs"
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to generate GCS signed URL: {e}")
        return Response(
            {"error": {"code": "server_error", "message": f"Could not generate download URL: {str(e)}"}},
            status=500
        )

@api_view(["GET"])   
@permission_classes([IsAuthenticated, IsOwnerOfDataFile])
def get_download_url(request, id: int):
    """Generate download URL - LOCAL ONLY"""
    datafile = get_object_or_404(DataFile, pk=id)
    # request.check_object_permissions(request, datafile)
    
    # Solo retornar URL local
    return Response({
        "download_url": request.build_absolute_uri(datafile.file.url),
        "expires_in": 900,
        "filename": datafile.file.name,
        "type": "direct",
        "storage": "local"
    })