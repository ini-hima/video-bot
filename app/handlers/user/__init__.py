"""معالجات المستخدم (telebot-style)"""
import logging
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

def register_user_handlers(bot):
    """تسجيل معالجات المستخدمين لِـ telebot"""
    # مثال: يمكن إضافة أي message_handler أو callback هنا لاحقًا
    logger.info("✅ تم تسجيل معالجات المستخدمين")
