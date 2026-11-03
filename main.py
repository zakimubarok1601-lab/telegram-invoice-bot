import os
import threading
from flask import Flask
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. FLASK SERVER UNTUK KEEP-ALIVE RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Invoice Telegram Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. LOGIK GENERATE PDF ---
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('invoice_template.html')

def build_pdf(data, output_file="invoice.pdf"):
    subtotal = sum(item['qty'] * item['price'] for item in data['items'])
    sisa = subtotal - data['dp']

    logo_file = "logo.png" if os.path.exists("logo.png") else None

    render_data = {
        **data,
        "subtotal_formatted": f"{subtotal:,.0f}".replace(",", "."),
        "dp_formatted": f"{data['dp']:,.0f}".replace(",", "."),
        "sisa_formatted": f"{sisa:,.0f}".replace(",", "."),
        "logo_path": os.path.abspath(logo_file) if logo_file else None
    }

    # Format angka pada items
    for item in render_data['items']:
        item['price_formatted'] = f"{item['price']:,.0f}".replace(",", ".")
        item['total_formatted'] = f"{item['qty'] * item['price']:,.0f}".replace(",", ".")

    html_out = template.render(render_data)
    HTML(string=html_out).write_pdf(output_file)
    return output_file

# --- 3. TELEGRAM BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Selamat Datang di Bot Invoice Henna!*\n\n"
        "Gunakan perintah /test untuk mencoba generate invoice sampel secara otomatis."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def test_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Sedang memproses PDF Invoice...")
    
    sample_data = {
        "client_name": "Kak Aisyah",
        "invoice_date": "3 November 2026",
        "items": [
            {
                "name": "Glamor Henna",
                "details": "Bride : Aisyah\nTanggal : 9 Januari 2027\nLokasi : Patra Jasa",
                "qty": 1,
                "price": 650000
            },
            {
                "name": "Transport Pulang Pergi",
                "details": "",
                "qty": 1,
                "price": 50000
            }
        ],
        "dp": 100000,
        "bank_owner": "Laila Septia Anggraini",
        "bank_account": "6080278762 (BCA)"
    }

    pdf_path = build_pdf(sample_data)
    
    with open(pdf_path, 'rb') as pdf:
        await update.message.reply_document(
            document=pdf,
            filename=f"Invoice_{sample_data['client_name']}.pdf",
            caption="✅ Invoice berhasil dibuat!"
        )

# --- 4. MAIN ENTRY POINT ---
if __name__ == '__main__':
    # Jalankan Flask Server di Thread Terpisah
    threading.Thread(target=run_flask, daemon=True).start()

    # Masukkan Token Telegram Bot dari Environment Variable
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "ISI_TOKEN_BOT_TELEGRAM_KAMU")
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_invoice))

    application.run_polling()
