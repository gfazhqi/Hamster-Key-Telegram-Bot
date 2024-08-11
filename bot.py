import subprocess
import os
import logging
import asyncio
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import server

# Paste Token Here if you don't want to put it in an env. variable for some reason
TOKEN_INSECURE = ""

if os.name == 'posix':
    TOKEN = subprocess.run(["printenv", "HAMSTER_BOT_TOKEN"], text=True, capture_output=True).stdout.strip()
elif os.name == 'nt':
    TOKEN = subprocess.run(["echo", "%HAMSTER_BOT_TOKEN%"], text=True, capture_output=True, shell=True).stdout.strip()
    TOKEN = "" if TOKEN == "%HAMSTER_BOT_TOKEN%" else TOKEN

AUTHORIZED_USERS = []
EXCLUSIVE = False
REQUIRED_CHANNEL = "@your_channel_name"  # Ganti dengan nama channel Anda

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Ubah ke DEBUG untuk lebih banyak logging
)

logger = logging.getLogger(__name__)

async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=update.effective_chat.id)
        logger.debug(f"User status: {chat_member.status}")
        return chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Error checking user membership: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please join our channel first: {REQUIRED_CHANNEL}")
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="The Commands are:\n*/bike*\n*/clone*\n*/cube*\n*/train*\n*/all*\nThese will generate 4 keys for their respective games\.", 
        parse_mode='MARKDOWNV2'
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="You can also set how many keys are generated\. For example, */cube 8* will generate *EIGHT* keys for the cube game\.", 
        parse_mode='MARKDOWNV2'
    )

async def generate_keys(update: Update, context: ContextTypes.DEFAULT_TYPE, chosen_game: int):
    if not await is_user_joined(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please join our channel first: {REQUIRED_CHANNEL}")
        return

    if EXCLUSIVE and update.effective_chat.id not in AUTHORIZED_USERS:
        return

    logger.info(f"Generating for client: {update.effective_chat.id}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Generating\.\.\.", parse_mode='MARKDOWNV2')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This will only take a moment\.\.\.", parse_mode='MARKDOWNV2')

    try:
        no_of_keys = int(context.args[0]) if context.args else 4
    except ValueError:
        no_of_keys = 4

    keys = await server.run(chosen_game=chosen_game, no_of_keys=no_of_keys)
    generated_keys = [f"`{key}`" for key in keys]
    formatted_keys = '\n'.join(generated_keys)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted_keys}", parse_mode='MARKDOWNV2')
    logger.info("Message sent to the client.")

async def bike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_keys(update, context, chosen_game=1)

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_keys(update, context, chosen_game=2)

async def cube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_keys(update, context, chosen_game=3)

async def train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_keys(update, context, chosen_game=4)

async def all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please join our channel first: {REQUIRED_CHANNEL}")
        return

    if EXCLUSIVE and update.effective_chat.id not in AUTHORIZED_USERS:
        return

    logger.info(f"Generating for client: {update.effective_chat.id}")
    logger.info("Generating keys for All Games.")
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Currently generating for all games\.\.\.", parse_mode='MARKDOWNV2')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Come Back in about 5\-10 minutes\.", parse_mode='MARKDOWNV2')

    try:
        no_of_keys = int(context.args[0]) if context.args else 4
    except ValueError:
        no_of_keys = 4

    for i in range(4):
        await generate_keys(update, context, chosen_game=i+1)

if __name__ == '__main__':
    logger.debug(f"TOKEN: {TOKEN or TOKEN_INSECURE}")
    
    # Reset event loop
    try:
        asyncio.get_event_loop().close()
    except:
        pass
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    application = ApplicationBuilder().token(TOKEN or TOKEN_INSECURE).build()
    logger.info("Server is running. Awaiting users...")

    application.add_handler(CommandHandler('start', start, block=False))
    application.add_handler(CommandHandler('bike', bike, block=False))
    application.add_handler(CommandHandler('clone', clone, block=False))
    application.add_handler(CommandHandler('cube', cube, block=False))
    application.add_handler(CommandHandler('train', train, block=False))
    application.add_handler(CommandHandler('all', all, block=False))

    application.run_polling()
