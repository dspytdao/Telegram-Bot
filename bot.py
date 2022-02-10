import datetime
import logging
import os
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

#from app.utils import FirstTry
#datastorage = FirstTry()

from py3cw.request import Py3CW

p3cw = Py3CW(
    key=os.environ.get("KEY"), 
    secret=os.environ.get("SECRET"),
    request_options={
        'request_timeout': 10,
        'nr_of_retries': 5,
        'retry_status_codes': [502],
        'retry_backoff_factor': 0.1
    }
)

long_array = ['https://c.tenor.com/SY_Rb9FZFb4AAAAS/cat-jam-stonks.gif', "https://i.giphy.com/media/YnkMcHgNIMW4Yfmjxr/giphy.webp", ]

short_array = ["https://c.tenor.com/lhey0DPlkiQAAAAM/rage-red-stocks.gif" ]

# Command Handlers
def start(update, context):
    # how do we pass class instance here
    context.bot.sendAnimation(chat_id=update.message.chat_id,
        animation = 'https://c.tenor.com/8IIQDBECgssAAAAM/hello-sexy-hi.gif',
        caption='Long Signal!',
        )
    #datastorage.add_counter()

    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hi! Enter the id for the marketplace to get the latest signal')
    #update.message.reply_text(f'Hi! number:{datastorage.counter}')


def help(update, context):
    """Send a message when the command /help is issued."""
    
    update.message.reply_text('Help! Help! Help! Help!')


def echo(update, context):
    #https://core.telegram.org/bots/api#sendanimation
    #https://stackoverflow.com/questions/35294948/telegram-python-chatbot-replying-with-an-animated-gif
    """Echo the user message."""
    #print(update.message.text)
    error, data = p3cw.request(
        entity='marketplace', 
        action='signals',
        action_id = update.message.text
    )
    if len(error):
        update.message.reply_text(f' Enter Correct ID')
    #print(data)
    if data[0]['signal_type'] == 'long':
        context.bot.sendAnimation(
            chat_id=update.message.chat_id,
            animation = long_array[random.randrange(2)-1],
            caption='Long Signal!',
        )
    else:
        context.bot.sendAnimation(
            chat_id=update.message.chat_id,
            animation = short_array[0],
            caption='Short Signal!',
        )
    pair = data[0]['pair']
    exchange = data[0]['exchange']
    id = data[0]['id']
    time = datetime.datetime.fromtimestamp(
        int(data[0]['timestamp'])
    ).strftime('%Y-%m-%d %H:%M:%S')
    min = data[0]['min']
    max = data[0]['max']
    update.message.reply_text(f' Pair: {pair}, Exchange: {exchange}, Id: {id}, Time: {time}, Min: {min}, Max: {max}')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.environ.get("API_KEY")
    APP_NAME='https://nft-link-telegram-bot.herokuapp.com/'
  
    updater = Updater(TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_NAME + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()