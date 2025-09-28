#manager_tasks/pagination.py
from rest_framework.pagination import CursorPagination


#28-09-2025 hw17 pagination
class CustomCursorPagination(CursorPagination):
    page_size = 6
    ordering = '-created_at'
    cursor_query_param = 'cursor'  # Параметр для курсора в URL


