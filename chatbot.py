from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    ContextTypes, filters
import configparser
import os
import logging
import redis
global redis1

MovieReview = range(4)

def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    #update environment
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    # redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']
    # ['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    redis1 = redis.Redis(host=(os.environ['HOST']), password=
    (os.environ['PASSWORD']), port=(os.environ['REDISPORT']))
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start", callback=start)],
    #     states={
    #         MovieReview: [CommandHandler("write", callback=write), CommandHandler("check", callback=help_command)],
    #     },
    #     fallbacks=[CommandHandler("cancel", callback=cancel)],
    # )
    dispatcher.add_handler(echo_handler)
    # dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("write", write))
    dispatcher.add_handler(CommandHandler("checkAll", checkAll))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("cancel", cancel))


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Good day,' + str(context.args[0]) + '!')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        # logging.info(context.args[1])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
        redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["/write", "/check"]]

    update.message.reply_text(
        "Hi! My name is Gp18 Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Do you want to write movie reviews or read movie reviews?\n"
        "send /write to write movie reviews \nor /check to read movie reviews",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="write or check"
        ),
    )

    return write

def write(update: Update, context: CallbackContext) -> None:
    """Stores the selected gender and asks for a photo."""
    # update.message.reply_text('Helping you helping you.')
    try:
        global redis1
        title = context.args[0]
        # review = context.args[1]
        num = len(context.args)
        review = ""
        i = 0
        for i in range(1,num):
            review = review + context.args[i] + " "

        logging.info(context.args[0])
        logging.info(review)
        # logging.info(re)
        redis1.__setitem__(title, review)
        update.message.reply_text('Title: ' + title + '\nContent: \n' +
        redis1.get(title).decode('UTF-8'))
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /write <keyword>')

def checkAll(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        title = redis1.keys()
        # logging.info(title.decode('UTF-8'))
        msg = ""
        for i in range(len(title)):
            msg = msg + title[i].decode('UTF-8') + "\n"
        update.message.reply_text('Title: \n' + msg + '\n' + 'Type /check title_name to check the review')
    except (IndexError, ValueError):
        update.message.reply_text('error')

def check(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        title = context.args[0]
        review = redis1.get(title).decode('UTF-8')
        # logging.info(title.decode('UTF-8'))
        update.message.reply_text('Title: ' + title + '\nReview: \n' + review)
    except (IndexError, ValueError):
        update.message.reply_text('error')





def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':
    main()