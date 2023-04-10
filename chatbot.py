from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    ContextTypes, filters
import configparser
import os
import logging

import redis
global redis1

import json
import pymongo
myclient = pymongo.MongoClient('mongodb://huang:coGpqKLbSMEsjI839oMXYzWll2MkyTH3OzF76OQF26N3bc1FjGRV0nRl4yHVovUkBhwAzLhAnMF2hrPoTXVPAA==@huang.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@huang@')
mydb = myclient['ChatBotDB']
moviecol = mydb['Movie']
mountaincol = mydb['Mountain']



def main():
    global redis1


    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    
    redis1 = redis.Redis(host=(os.environ['HOST']), password=
    (os.environ['PASSWORD']), port=(os.environ['REDISPORT']))
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("write", write))
    dispatcher.add_handler(CommandHandler("checkAllMovie", checkAllMovie))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("photo",photo))
    dispatcher.add_handler(CommandHandler("checkHikingRoute", checkHikingRoute))


    dispatcher.add_handler(CommandHandler("cancel", cancel))


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    dispatcher.add_handler(CommandHandler("addmountain", addMountain))
    # dispatcher.add_handler(CommandHandler("movie", Movie))
    # dispatcher.add_handler(CommandHandler("mountain", Mountain))
    # dispatcher.add_handler(CommandHandler("clean", cleanDB))


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
def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Good day, ' + str(context.args[0]) + '!')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        # global redis1
        logging.info('Keyword: ' + context.args[0])
        # logging.info(context.args[1])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        # in Redis database, automatically set 'msg' as a key, increase its value by 1
        redis1.incr(msg) 
        update.message.reply_text('You have said ' + msg + ' for ' +
        redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        # Reply to the user with a message suggesting the correct command format.
        update.message.reply_text('Usage: /add <keyword>')


# start a conversation by entering '/start'
def start(update: Update, context) -> int:
    reply_keyboard = [["/checkAllMovie", "/checkHikingRoute", "/cancel"]]

    update.message.reply_text(
        "Hi! My name is Gp18 Bot. I will hold a conversation with you.\n\n"
        
        "Do you want to write a movie review, read a movie review, see the hiking information?\n"
        "1. send /checkAllMovie to read see all movie's name'\n"
        "2. send /write + <movie title>. + <movie review> to write a movie review\n"
        "3. send /checkHikingRoute to see all mountain's name\n"
        "4. send /photo + <mountain name> to see a hiking route and a photo\n"
        "5. Send /cancel to stop talking to me\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="checkAllMovie, write, checkHikingRoute, photo or cancel"
        ),
    )
    return write


# write a review in the format of '/write <movie_title>. <movie_review>'
def write(update: Update, context: CallbackContext) -> None:
    try:
        input_text = ' '.join(context.args) # transfer a list to string
        # detect the first full stop, split the string as a separator.
        movie_title, movie_review = input_text.split('.', maxsplit=1)

        # push movie name to movie_name list in redis
        # if(redis1.get(movie_title) != None):
        #     redis1.lrem('movie_name', 0, movie_title)
        # redis1.lpush('movie_name', movie_title)
        record = {'movie_title': movie_title,'movie_review': movie_review}
        moviecol.insert_one(record)
        movie_record_fromdb = moviecol.find_one({'movie_title': movie_title})
        review = movie_record_fromdb['movie_review']


        #log
        # logging.info('context: ' + movie_title)
        # logging.info('review: ' + movie_review)
        logging.info(movie_record_fromdb)


        # store to Redis database with 'movie_title' as the key.
        # redis1.set(movie_title, movie_review)

        #reply user movie title and movie review
        update.message.reply_text('Movie Title: \n' + movie_title + '\nMovie Review: ' +
                                  review)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /write <movie_title>. <movie_review>')


def checkAllMovie(update: Update, context) -> None:
    try:

        #get movie title from movie_name list
        # movie_titles_list = redis1.lrange('movie_name',0,-1)
        movie_list = moviecol.find()
        logging.info(movie_list)
        movie_titles_list = []
        for result in movie_list:
            movie_titles_list.append(result)
        logging.info(movie_titles_list)

        msg = ''

        # get movie title from movie_titles_list
        for movie_record in movie_titles_list:
            movie_title = movie_record['movie_title']
            msg  = msg + movie_title + " \n"

        #reply user all movie title
        update.message.reply_text('Movie Title \n' + '\n' + msg + '\n' +
                                  'Type /check title_name to check the review')
        
    except (IndexError, ValueError):
        update.message.reply_text('error')

#check a movie review
def check(update: Update, context: CallbackContext) -> None:
    try:
        # global redis1
        title = context.args[0]
        # review = redis1.get(title).decode('UTF-8')
        record = moviecol.find_one({'movie_title': title})
        review = record['movie_review']
        # logging.info(title.decode('UTF-8'))
        update.message.reply_text('Title: ' + title + '\nReview: \n' + review)
    except (IndexError, ValueError):
        update.message.reply_text('error')

# see a hiking route and a photo,
def photo(update: Update, context: CallbackContext) -> None:

    try:
        # get the mountain name from the input
        mountain_name = ' '.join(context.args)
        # logging.info(mountain_name)
        mountain_route = 'mountain_route'

        # get description from Redis according to mountain name
        # mountain_info = redis1.hgetall(mountain_route)
        # logging.info(mountain_info)

        # get the URL and description according to mountain_name
        # img_url = redis1.hget(mountain_name, 'img_url')
        # description = redis1.hget(mountain_name, 'description')
        mountain_info = mountaincol.find_one({'mountain_name': mountain_name})
        img_url = mountain_info['img_url']
        description = mountain_info['description']

        # logging.info(mountain_info)
        logging.info('img_url = ' + str(img_url))
        logging.info('description = ' + str(description))
        

        # if not mountain_info:
        #     context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, no information found for the specified mountain.")
        #     return
        
        # # check if img_url and description exist in mountain_info dictionary
        # if 'img_url' not in mountain_info or 'description' not in mountain_info:
        #     context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, the information for the specified mountain is incomplete.")
        #     return

        
        update.message.reply_text('Mountain Name: ' + mountain_name + '\n\n'
                                  + 'Mountain Image: ' + img_url
                                  + '\n\n' + 'Hiking Route: ' + description)



    except (IndexError, ValueError):
        update.message.reply_text('Usage: /photo <mountain_name>')

#add Mountain info to redis
def addMountain(update: Update, context: CallbackContext) -> None:
    try:
        # read mountains' information from 'mountains.json'
        with open("mountains.json", 'r') as f:
            mountains = json.load(f)

        for mountain_name, mountain_info in mountains.items():
            #push mountain name to mountain_name list in redis
            # if (redis1.hgetall(mountain_name) != None):
            #     redis1.lrem('mountain_name', 0, mountain_name)
            # redis1.lpush('mountain_name', mountain_name)
            # 将每条hiking route以多个键值对的形式存储在redis中，key为山峰的名称，value为包含img_url和description两个字段的hash map
            # redis1.hmset(mountain_name,
            #              {'img_url': mountain_info['img_url'],
            #               'description': mountain_info['description']})
            record = {'mountain_name': mountain_name, 'img_url': mountain_info['img_url'], 'description': mountain_info['description']}
            mountaincol.insert_one(record)
            logging.info(record)
    except(IndexError, ValueError):
        logging.info('mountain info add fail!')

#check all hiking route
def checkHikingRoute(update: Update, context: CallbackContext) -> None:
    msg = ''
    try:
        # hiking_route_list = redis1.lrange('mountain_name',0,-1)
        mountain_info = mountaincol.find()
        hiking_route_list = []
        for result in mountain_info:
            hiking_route_list.append(result)
        logging.info(hiking_route_list)
        for record in hiking_route_list:
            mountain_name = record['mountain_name']
            logging.info(mountain_name)
            # m_str = mountain_name.decode('UTF-8')
            # logging.info('m_str ' + m_str)
            msg += mountain_name + ' \n'
        update.message.reply_text('Mountain name \n' + msg + 'Type /photo mountain_name to check the mountain details')
    except(IndexError, ValueError):
        update.message.reply_text('Usage: /checkHikingRoute <mountain name>')


#clean DB in redis //danger
def cleanDB(update, context) -> None:
    try:
        redis1.flushall()
        logging.info('clean db success!')
    except (IndexError, ValueError):
        logging.info('try again!')


#test
# def Movie(update, context) -> None:
#     try:
#         movie_name = redis1.lrange('movie_name',0,-1)
#         logging.info(movie_name)
#     except(IndexError,ValueError):
#         logging.info('check movie title fail!')

#test
# def Mountain(update, context) -> None:
#     try:
#         mountain_name = redis1.lrange('mountain_name',0,-1)
#         logging.info(mountain_name)
#     except(IndexError,ValueError):
#         logging.info('check movie title fail!')


def cancel(update: Update, context) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':
    
    main()