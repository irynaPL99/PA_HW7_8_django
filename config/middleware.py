# config/middleware.py
"""28-09-2025 hw17 logging (проблема логировнаия http запросов)
Перехватывает каждый HTTP-запрос.
Записывает информацию о запросе (метод, путь, статус ответа) в логгер django.request,
который настроен на использование обработчика http_file.
Передает дополнительные поля (method, path, status) через extra,
 чтобы они соответствовали форматтеру http.
"""
import logging
logger = logging.getLogger('django.request')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        logger.info(
            f"Request: {request.method} {request.path} {response.status_code}",
            extra={
                'method': request.method,
                'path': request.path,
                'status': response.status_code
            }
        )
        return response