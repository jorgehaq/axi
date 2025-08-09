import json
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Token, DataFile
from django.core.files.uploadedfile import UploadedFile

def health(request):
    return JsonResponse({"status": "ok"})

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





from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from .models import DataFile
from .services import safe_read_csv, DataReadError

def _json_error(message: str, status: int = 400):
    from django.http import JsonResponse
    return JsonResponse({"error": message}, status=status)

@require_GET
def data_preview(request, id: int):
    datafile = get_object_or_404(DataFile, pk=id)
    try:
        df = safe_read_csv(datafile.file.path, nrows=5)
    except DataReadError as e:
        return _json_error(str(e), status=400)

    # Conviértelo a JSON simple (lista de dicts)
    preview = df.head(5).to_dict(orient="records")
    return JsonResponse({"id": datafile.id, "rows": preview})

@require_GET
def data_summary(request, id: int):
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