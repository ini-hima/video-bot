import os
import logging
from flask import Flask, request
from config import bot, DATABASE_URL
from app.database.connection import init_database
import threading
import schedule
import time
import requests

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# ✅ استيراد المعالجات بطريقة آمنة
def register_all_handlers():
    """تسجيل جميع المعالجات"""
    handlers_registered = 0
    
    # معالجات البداية
    try:
        from app.handlers.start import register_start_handlers
        register_start_handlers()
        handlers_registered += 1
    except Exception as e:
        logger.error(f"❌ خطأ في معالجات البداية: {e}")
    
    # معالجات الإدارة
    try:
        from app.handlers.admin import register_admin_handlers
        register_admin_handlers()
        handlers_registered += 1
    except Exception as e:
        logger.error(f"❌ خطأ في معالجات الإدارة: {e}")
    
    # معالجات النصوص
    try:
        from app.handlers.text import register_text_handlers
        register_text_handlers()
        handlers_registered += 1
    except Exception as e:
        logger.error(f"❌ خطأ في معالجات النصوص: {e}")
    
    # معالجات الأزرار
    try:
        from app.handlers.callbacks import register_callback_handlers
        register_callback_handlers()
        handlers_registered += 1
    except Exception as e:
        logger.error(f"❌ خطأ في معالجات الأزرار: {e}")
    
    # معالجات الفيديوهات
    try:
        from app.handlers.video_handler import register_video_handlers
        register_video_handlers()
        handlers_registered += 1
    except Exception as e:
        logger.error(f"❌ خطأ في معالجات الفيديوهات: {e}")
    
    logger.info(f"✅ تم تسجيل {handlers_registered}/5 معالج")
    return handlers_registered

@app.route('/', methods=['GET'])
def index():
    """صفحة رئيسية للتحقق"""
    return "البوت يعمل!", 200

@app.route(f'/{os.getenv("BOT_TOKEN")}', methods=['POST'])
def webhook():
    """استقبال التحديثات من Telegram"""
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    except Exception as e:
        logger.error(f"خطأ في معالجة webhook: {e}")
        return '', 500

def cleanup_old_data():
    """تنظيف البيانات القديمة"""
    try:
        from app.database.connection import execute_query
        query = "DELETE FROM user_history WHERE watched_at < NOW() - INTERVAL '30 days'"
        execute_query(query)
        logger.info("✅ تم تنظيف البيانات القديمة")
    except Exception as e:
        logger.error(f"خطأ في التنظيف: {e}")

def schedule_cleanup():
    """جدولة التنظيف"""
    schedule.every().day.at("03:00").do(cleanup_old_data)
    while True:
        schedule.run_pending()
        time.sleep(3600)

def keep_alive():
    """إبقاء الخدمة نشطة"""
    url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:10000')
    while True:
        try:
            requests.head(url)
            time.sleep(300)
        except:
            pass

if __name__ == '__main__':
    logger.info("🚀 بدء تشغيل بوت أرشيف الفيديوهات")
    
    # الاتصال بقاعدة البيانات
    try:
        init_database()
        logger.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
    
    # تسجيل المعالجات
    logger.info("📝 بدء تسجيل جميع المعالجات...")
    handlers_count = register_all_handlers()
    
    if handlers_count == 0:
        logger.error("❌ لم يتم تسجيل أي معالج - تحقق من الأخطاء")
    else:
        logger.info(f"✅ تم تسجيل {handlers_count} معالج بنجاح")
    
    # تشغيل جدولة التنظيف
    cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("✅ تم تفعيل جدولة التنظيف")
    
    # تشغيل keep-alive
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("✅ تم تفعيل نظام الإبقاء نشطاً")
    
    # إعداد Webhook
    webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL')}/{os.getenv('BOT_TOKEN')}"
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        logger.info(f"✅ تم إعداد Webhook: {webhook_url}")
    except Exception as e:
        logger.error(f"❌ فشل إعداد Webhook: {e}")
    
    # تشغيل Flask
    logger.info("🎉 البوت جاهز للعمل!")
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
