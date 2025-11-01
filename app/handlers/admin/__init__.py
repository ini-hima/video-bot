"""معالجات الإدارة - re-export للوحدة الفعلية المكتوبة لِـ telebot"""
from .admin import register_admin_handlers, handle_admin_callback

__all__ = ["register_admin_handlers", "handle_admin_callback"]
