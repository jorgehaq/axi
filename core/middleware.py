import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class StructuredLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Generar correlation ID único para esta request
        request.correlation_id = str(uuid.uuid4())[:8]
        request.start_time = time.time()
        
        # Log de inicio
        logger.info(f"Request started - correlation_id: {request.correlation_id}, method: {request.method}, path: {request.path}, user: {str(request.user) if hasattr(request, 'user') else 'anonymous'}")
    
    def process_response(self, request, response):
        # Log de respuesta
        duration = time.time() - getattr(request, 'start_time', time.time())

        logger.info(f"Request completed - correlation_id: {getattr(request, 'correlation_id', 'unknown')}, status_code: {response.status_code}, duration_ms: {round(duration * 1000, 2)}")

        return response
