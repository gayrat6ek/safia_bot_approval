#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""


import logging

import requests
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,KeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


import re




BASE_URL = 'http://185.74.5.198:8000'

# Enable logging
logger = logging.getLogger(__name__)

PHONENUMBER, FULLNAME,PASSWORD= range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [[KeyboardButton(text='Share number', request_contact=True)]]

    await update.message.reply_text(
        "Hello i  am bot ",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,input_field_placeholder="Please share you number?",resize_keyboard=True
        ),
    )

    return PHONENUMBER


async def phonenumber(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    context.user_data['phone_number'] = update.message.contact.phone_number
    await update.message.reply_text(
        "Iltimos toliq ismingizni kiriting",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FULLNAME


async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    full_name = update.message.text
    context.user_data['full_name']=full_name
    await update.message.reply_text(
        'iltimos menga passwordingizni yuboring'"va u kamida 6 belgidan iborat bolishiga etibor bering",
    )
    return PASSWORD
import json


async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    password = update.message.text
    context.user_data['password']=password
    r = requests.post(url=f"{BASE_URL}/register",data=json.dumps({'username':str(context.user_data['phone_number']),'password':(context.user_data['password']),'full_name':str(context.user_data['full_name']),'telegram_id':int(update.message.from_user.id)}))
    if r.status_code == 200:
        await update.message.reply_text(
        "Sizning malumotlaringiz adminga yuborildi. va sizga tez orada sizga javob beramiz."
    )
    else:
        await update.message.reply_text('Siz oldin ro\'yhatdan otgansiz iltimsiz iltimos javob kelishini kuting')
    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user

    user = requests.post(url=f"{BASE_URL}/tel/me",data=json.dumps({'id':int(update.message.from_user.id)}))
    try:
        if user.json()['role'] in ['musa','shakhzod','begzod','fin','accountant','purchasing']:
            await update.message.reply_text('you are super user. your role is {}'.format(user.json()['role']))
        else:
            await update.message.reply_text(
            "you are still has not been chacked", reply_markup=ReplyKeyboardRemove()
        )  
    except:
         await update.message.reply_text(
            "you hasnot registered yet", reply_markup=ReplyKeyboardRemove()
        )  
    return ConversationHandler.END


async def handle_callback_query(update:Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    selected_option = query.data
    reply_markup = InlineKeyboardMarkup([])
    
    text_of_order = query.message.text
    user_id = query.from_user.id
    order_id = list(map(int, re.findall('\d+', text_of_order)))[0]
    order_update = requests.post(url=f"{BASE_URL}/update/order/status/from/telegram",data=json.dumps({'order_id':order_id,'telid':user_id,'status':selected_option}))
    if order_update.status_code == 200: 
        message = query.message
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        await query.message.reply_text('you voted this order')
    else:
        await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        await query.message.reply_text('you cannot vote for this message')


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

def main() -> None:
    callback_query_handler = CallbackQueryHandler(handle_callback_query)
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6298581686:AAGVha0x_j3u-KPik0NDW6eSd_LBZ-0yQRI").build()
    application.add_handler(callback_query_handler)

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),CommandHandler('check',check)],
        states={
            PHONENUMBER: [MessageHandler(filters.CONTACT, phonenumber)],
            FULLNAME: [MessageHandler(filters.TEXT, fullname)],
            PASSWORD: [MessageHandler(filters.TEXT, password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],


    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()