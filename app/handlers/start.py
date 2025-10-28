"""معالجات أوامر البداية"""
import logging
from telebot import types
from config import bot
from app.database.connection import execute_query

logger = logging.getLogger(__name__)

def register_start_handlers():
    """تسجيل معالجات البداية"""
    
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """أمر البداية"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "مستخدم"
            
            # تسجيل المستخدم في قاعدة البيانات
            query = """
            INSERT INTO bot_users (user_id, username) 
            VALUES (%s, %s) 
            ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
            """
            execute_query(query, (user_id, username))
            
            # رسالة الترحيب
            welcome_text = f"""
🎬 مرحباً بك في بوت أرشيف الفيديوهات!

استخدم الأزرار أدناه للتصفح:
            """
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("🔍 بحث")
            btn2 = types.KeyboardButton("📂 التصنيفات")
            btn3 = types.KeyboardButton("⭐ المفضلة")
            btn4 = types.KeyboardButton("📜 السجل")
            markup.add(btn1, btn2, btn3, btn4)
            
            bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
            logger.info(f"مستخدم جديد: {user_id} - {username}")
            
        except Exception as e:
            logger.error(f"خطأ في أمر البداية: {e}")
            bot.send_message(message.chat.id, "حدث خطأ، حاول مرة أخرى")
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        """أمر المساعدة"""
        try:
            help_text = """
📚 قائمة الأوامر:

/start - بدء البوت
/help - عرض المساعدة
/admin - لوحة التحكم (للمشرفين)

🔍 للبحث: اكتب اسم الفيديو مباشرة
📂 التصنيفات: تصفح حسب الفئة
⭐ المفضلة: فيديوهاتك المحفوظة
📜 السجل: آخر ما شاهدت
            """
            bot.send_message(message.chat.id, help_text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"خطأ في أمر المساعدة: {e}")
    
    logger.info("✅ تم تسجيل معالجات البداية")
