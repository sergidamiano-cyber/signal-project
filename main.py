
import os
from dotenv import load_dotenv
load_dotenv()
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup



from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from detoxify import Detoxify

from database import SessionLocal
from database import Interaction


# =========================
# TOKEN TELEGRAM
# =========================

TOKEN = os.getenv("TELEGRAM_TOKEN")

# =========================
# MODELLO IA
# =========================

model = Detoxify('multilingual')


# =========================
# RISCRITTURA EDUCATIVA
# =========================

def rewrite_message(text):

    replacements = {

        "fai schifo": "Non sono d'accordo con quello che dici.",

        "muori": "Sono molto arrabbiato in questo momento.",

        "sei inutile": "Credo che tu possa fare meglio.",

        "idiota": "Non condivido il tuo comportamento.",

        "stupido": "Secondo me hai sbagliato.",

        "nessuno ti vuole": "Forse ci sono stati dei problemi nel gruppo.",

        "vergognati": "Forse dovresti riflettere su quello che è successo."
    }

    lower_text = text.lower()

    for bad, good in replacements.items():

        if bad in lower_text:

            return good

    return "Prova a esprimere lo stesso concetto in modo più rispettoso."


# =========================
# GESTIONE MESSAGGI
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text

    user = update.message.from_user

    print("\n====================")
    print("MESSAGGIO:")
    print(text)

    # =========================
    # ANALISI IA
    # =========================

    results = model.predict(text)

    toxicity = float(results['toxicity'])
    insult = float(results['insult'])
    threat = float(results['threat'])

    print(results)

    # =========================
    # CONTROLLO RISCHIO
    # =========================

    if (
        toxicity > 0.50
        or insult > 0.50
        or threat > 0.40
    ):

        print("⚠️ MESSAGGIO A RISCHIO")

        # Suggerimento educativo
        new_text = rewrite_message(text)

        # =========================
        # DATABASE
        # =========================

        db = SessionLocal()

        interaction = Interaction(

            username=user.username,

            original_message=text,

            rewritten_message=new_text,

            toxicity=toxicity,

            accepted=False
        )

        db.add(interaction)

        db.commit()

        db.close()

        print("✅ Salvato nel database")

        # =========================
        # PULSANTI CONTESTUALI
        # =========================

        keyboard = [

            [
                InlineKeyboardButton(
                    "✅ Usa suggerimento",
                    callback_data=f"accept|{new_text}"
                )
            ],

            [
                InlineKeyboardButton(
                    "⚠️ Mantieni originale",
                    callback_data="original"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # =========================
        # NOTIFICA CONTESTUALE
        # =========================

        await update.message.reply_text(
            f"""
⚠️ SIGNAL ha rilevato un possibile contenuto offensivo.

Suggerimento:

{new_text}
""",
            reply_markup=reply_markup
        )

    else:

        print("✅ Messaggio OK")


# =========================
# GESTIONE PULSANTI
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer(

        text="⚠️ Riflettere prima di inviare un messaggio può aiutare a prevenire conflitti.",

        show_alert=True
    )

    data = query.data

    # =========================
    # USA SUGGERIMENTO
    # =========================

    if data.startswith("accept"):

        suggested_text = data.split("|", 1)[1]

        await query.edit_message_text(
            text=f"""
✅ Hai scelto una comunicazione più rispettosa.

Messaggio suggerito:

{suggested_text}
"""
        )

    # =========================
    # MANTIENI ORIGINALE
    # =========================

    elif data == "original":

        await query.edit_message_text(
            text="""
⚠️ Hai scelto di mantenere il messaggio originale.

SIGNAL invita comunque a usare un linguaggio rispettoso.
"""
        )


# =========================
# AVVIO BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(

    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

app.add_handler(
    CallbackQueryHandler(button_handler)
)

print("\n====================")
print("SIGNAL BOT AVVIATO")
print("====================\n")

app.run_polling()