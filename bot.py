import random
import string
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ChatInviteLink
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# --- CONFIG ---
BOT_TOKEN = "8012689768:AAH0xZrT-56mSWey1gM-gq4cD3syOYMz5so"
ADMIN_USERNAME = "@Jiims95"
CHANNEL_ID = -1002131023645
PAYPAL_LINK = "https://www.paypal.com/paypalme/jiims95"
REVOLUT_LINK = "https://revolut.me/jiims95"

# --- UTILS ---
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

user_codes = {}  # user_id: code
user_lang = {}   # user_id: 'fr' or 'en'

# --- TEXTES ---
WELCOME_TEXT = {
    'fr': """
👋 Bienvenue sur Jims Fx – L’élite du trading intelligent.

📈 Rejoins notre canal privé et accède à :

🔥 Des signaux *exclusifs & ultra qualitatifs*, sélectionnés avec rigueur  
🎯 Des setups avec un *Risk:Reward minimum de 3:1* (souvent bien plus !)  
🧠 Des *conseils de trading* pour renforcer ta discipline et ta stratégie  
📊 Des *graphiques explicatifs* à chaque position pour comprendre et progresser

✅ Que tu sois débutant ou confirmé, tu trouveras ici une réelle valeur ajoutée.

👉 Pour t’abonner et rejoindre le canal privé, utilise la commande : /subscribe
    """,
    'en': """
👋 Welcome to Jims Fx – The elite of smart trading.

📈 Join our private channel and access:

🔥 *Exclusive & ultra high-quality* signals, carefully selected  
🎯 Setups with *Risk:Reward of at least 3:1* (often much more!)  
🧠 *Trading tips* to improve your discipline and strategy  
📊 *Detailed charts* for each trade to learn and grow

✅ Whether you’re a beginner or experienced, you’ll find real value here.

👉 To subscribe and join the private channel, use the command: /subscribe
    """
}

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_lang.get(user_id, 'en')
    keyboard = [
        [
            InlineKeyboardButton("Français", callback_data="lang:fr"),
            InlineKeyboardButton("English", callback_data="lang:en")
        ]
    ]
    await update.message.reply_text(
        "Choisissez votre langue / Choose your language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_lang.get(user_id, 'en')
    code = generate_code()
    user_codes[user_id] = code

    paypal_url = f"{PAYPAL_LINK}?note={code}"
    revolut_url = f"{REVOLUT_LINK}?note={code}"

    text = {
        'fr': f"Voici votre code de référence unique : *{code}*
Veuillez le mettre en description du paiement.

Une fois le paiement effectué, cliquez sur "J'ai payé".",
        'en': f"Here is your unique reference code: *{code}*
Please include it in the payment note.

Once payment is done, click "I have paid"."
    }

    buttons = [
        [InlineKeyboardButton("Payer via PayPal / PayPal", url=paypal_url)],
        [InlineKeyboardButton("Payer via Revolut / Revolut", url=revolut_url)],
        [InlineKeyboardButton("J'ai payé / I have paid", callback_data=f"paid:{user_id}")]
    ]

    await update.message.reply_text(
        text[lang],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- CALLBACKS ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    user_id = user.id

    if data.startswith("lang:"):
        lang = data.split(":")[1]
        user_lang[user_id] = lang
        await query.edit_message_text(WELCOME_TEXT[lang], parse_mode="Markdown")

    elif data.startswith("paid:"):
        code = user_codes.get(user_id, "?")

        keyboard = [[
            InlineKeyboardButton("Confirmer paiement", callback_data=f"confirm:{user_id}")
        ]]
        await context.bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=f"🚀 *Nouvelle demande d'abonnement*

Utilisateur: @{user.username}
ID: {user_id}
Code: `{code}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text("Votre demande a été envoyée à l'administrateur. You will receive your access link shortly.")

    elif data.startswith("confirm:"):
        user_id = int(data.split(":")[1])
        try:
            invite_link: ChatInviteLink = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                creates_join_request=False
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔗 Voici votre lien d'accès au canal privé / Here is your access link to the private channel: {invite_link.invite_link}"
            )
            await query.edit_message_text("Lien envoyé à l'utilisateur / Link sent to user.")
        except Exception as e:
            await query.edit_message_text(f"Erreur / Error: {e}")

# --- MAIN ---
if __name__ == '__main__':
    print("✅ Démarrage du bot Jims Fx (version personnalisée)")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling()
