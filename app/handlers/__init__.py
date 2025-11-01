"""
تسجيل جميع معالجات البوت (telebot-style)
"""
from typing import Any

from .start import register_start_handlers
from .search import register_search_handlers
from .video_handler import register_video_handlers
from .admin import register_admin_handlers
from .user import register_user_handlers

def register_handlers(bot: Any) -> None:
    """تسجيل جميع معالجات البوت بتمرير كائن telebot.TeleBot"""
    # معالجات البداية والأوامر الأساسية
    register_start_handlers(bot)

    # معالجات البحث
    register_search_handlers(bot)

    # معالجات الفيديو
    register_video_handlers(bot)

    # معالجات الإدارة
    register_admin_handlers(bot)

    # معالجات المستخدم
    register_user_handlers(bot)

    print("✅ تم تسجيل جميع معالجات البوت")
