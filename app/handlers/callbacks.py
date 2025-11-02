"""معالج شامل لجميع أزرار البوت مع دعم التصفح وأزرار الإدارة (telebot-style)"""
import logging
import math
from datetime import datetime
from telebot import types
from app.core.config import settings
from app.database.connection import execute_query

logger = logging.getLogger(__name__)

# حالة المستخدمين للعمليات التفاعلية
user_states = {}

def safe_edit(bot, chat_id, message_id, text, markup=None, allow_html=False):
    """تحرير رسالة بأمان بدون تعقيد Markdown. استخدم HTML فقط عند ضمان سلامة النص."""
    try:
        if allow_html:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='HTML')
        else:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    except Exception as e:
        logger.error(f"❌ edit_message_text failed: {e}")
        # كحل بديل: أرسل رسالة جديدة بدل التعديل
        try:
            if allow_html:
                bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text, reply_markup=markup)
        except Exception as e2:
            logger.error(f"❌ send_message fallback failed: {e2}")

def safe_send(bot, chat_id, text, markup=None, allow_html=False):
    try:
        if allow_html:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Exception as e:
        logger.error(f"❌ send_message failed: {e}")

def handle_callback_query(bot, call):
    """معالج شامل للأزرار مع دعم التصفح وأزرار الإدارة"""
    try:
        user_id = call.from_user.id
        data = call.data

        # استخدم إعدادات المشروع للحصول على قائمة المشرفين لتفادي الاستيراد الحلقي
        ADMIN_IDS = getattr(settings, "admin_list", [])

        if data == "main_menu":
            # استدعاء وظيفة البداية عبر تسجيلها سابقاً؛ إن أردت يمكنك استدعاء start handler مباشرة
            try:
                from app.handlers.start import start_command  # قد لا تكون متاحة بهذه الصيغة دائماً
                bot.delete_message(call.message.chat.id, call.message.message_id)
                start_command(call.message)
            except Exception:
                # بدلاً من ذلك أعد إرسال رسالة ثابتة أو استدعِ register_start_handlers عند بدء التطبيق
                pass

        elif data == "search":
            handle_search_menu(bot, call)

        elif data == "categories":
            handle_categories_menu(bot, call)

        elif data.startswith("categories_page_"):
            page = int(data.replace("categories_page_", ""))
            handle_categories_menu(bot, call, page)

        elif data == "favorites":
            handle_favorites_menu(bot, call, user_id)

        elif data == "history":
            handle_history_menu(bot, call, user_id)

        elif data == "popular":
            handle_popular_videos(bot, call)

        elif data == "recent":
            handle_recent_videos(bot, call)

        elif data == "stats":
            handle_stats_menu(bot, call)

        elif data == "help":
            handle_help_menu(bot, call)

        elif data.startswith("video_"):
            from app.handlers.video_handler import handle_video_details
            video_id = int(data.replace("video_", ""))
            handle_video_details(bot, call, user_id, video_id)

        elif data.startswith("category_"):
            if "_page_" in data:
                parts = data.replace("category_", "").split("_page_")
                category_id = int(parts[0])
                page = int(parts[1])
                handle_category_videos(bot, call, category_id, page)
            else:
                category_id = int(data.replace("category_", ""))
                handle_category_videos(bot, call, category_id)

        elif data.startswith("download_"):
            from app.handlers.video_handler import handle_video_download
            video_id = int(data.replace("download_", ""))
            handle_video_download(bot, call, video_id)

        elif data.startswith("favorite_"):
            from app.handlers.video_handler import handle_toggle_favorite
            video_id = int(data.replace("favorite_", ""))
            handle_toggle_favorite(bot, call, user_id, video_id)

        # معالجة أزرار الإدارة
        elif data.startswith("admin_"):
            if user_id not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "❌ غير مصرح لك بهذه العملية")
                return

            from app.handlers.admin import handle_admin_callback
            handle_admin_callback(bot, call)
            return  # عدم استدعاء answer_callback_query مرة أخرى

        else:
            bot.answer_callback_query(call.id, "🔄 هذه الميزة قيد التطوير")

        # تأكيد الضغط (بدون رسالة في حال تم التعامل داخل دوال الفيديو)
        if not data.startswith(("video_", "download_", "favorite_", "admin_")):
            bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"❌ خطأ في معالج الأزرار: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ حدث خطأ")
        except:
            pass

def register_all_callbacks(bot):
    """تسجيل معالجات الأزرار"""
    bot.callback_query_handler(func=lambda call: True)(lambda call: handle_callback_query(bot, call))
    logger.info("✅ تم تسجيل معالجات الأزرار")
