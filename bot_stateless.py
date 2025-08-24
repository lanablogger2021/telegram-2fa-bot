import os
import time
import re
import pyotp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

def clean_secret(text: str):
    text = re.sub(r"[^A-Z2-7]", "", text.upper())
    return text if text else None

def generate_totp(secret: str):
    totp = pyotp.TOTP(secret)
    code = totp.now()
    remaining = 30 - (int(time.time()) % 30)
    return code, remaining

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Kirim secret TOTP (contoh: `TBTM MIVF YE2B ...`) dan saya akan balas dengan 6-digit kode.\n\n"
        "⚠️ Secret tidak disimpan, hanya dipakai sekali lalu dibuang.",
        parse_mode="Markdown"
    )

async def handle_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    secret = clean_secret(text)
    if not secret:
        await update.message.reply_text("❗ Secret tidak valid. Harus base32 (A-Z, 2-7).")
        return
    code, remain = generate_totp(secret)
    await update.message.reply_text(f"🔐 Code: *{code}*\n⏳ Berlaku {remain}s", parse_mode="Markdown")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("❌ Set TELEGRAM_BOT_TOKEN environment variable dulu!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret))

    print("🤖 Bot started (stateless).")
    app.run_polling()

if __name__ == "__main__":
    main()
