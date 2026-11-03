import os
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Setup Telegram Application
ptb_app = Application.builder().token(BOT_TOKEN).build()

async def test_invoice(update: Update, context):
    await update.message.reply_text("⏳ Sedang memproses PDF Invoice...")
    # (Fungsi generate & send PDF kamu di sini)

ptb_app.add_handler(CommandHandler("test", test_invoice))

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        async def process():
            await ptb_app.initialize()
            update = Update.de_json(request.get_json(force=True), ptb_app.bot)
            await ptb_app.process_update(update)
        
        import asyncio
        asyncio.run(process())
        return "OK", 200
    return "Bot Active", 200
