#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from telegram import Bot
from telegram.ext import CommandHandler, ConversationHandler, Updater

from event import Event
from event_handler import event_handler
from book_handler import book_handler
from return_ticket_handler import return_ticket_handler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def guestlist(update, context):
    event = Event()
    if event.limited == False:
        update.message.reply_text(
            'This event isn\'t a VIP one, there is no guestlist.')

    else:
        if len(event.guests) == 0:
            update.message.reply_text(
                'No one has booked a ticket yet.')
        else:
            guestList = ['\n' + name + ': ' + str(personCount)
                         for name, personCount in event.guests.items()]
            update.message.reply_text(' '.join(guestList))

    return ConversationHandler.END


def done(update, context):
    event = Event()
    if event.pinned_message_user == update.effective_user.full_name:
        update.message.bot.unpin_chat_message(chat_id=event.chat_id)
        event.pinned_event = False
    else:
        update.message.reply_text(
            'Sorry, only the person who created the event can unpin it.')

    return ConversationHandler.END


def help_command(update, context):
    update.message.reply_text(
        'These are commands that I understand:\n /event to create a new event \n /done to unpin a past event \n /book to book a ticket \n /returnticket if you want to give ticket(s) back \n /guestlist to know the guestlist of a VIP event \n /help if you want help again')
    return ConversationHandler.END


def main():
    updater = Updater(os.environ['DACHBODEN_KEY'], use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(event_handler)
    dp.add_handler(book_handler)
    dp.add_handler(return_ticket_handler)

    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(CommandHandler("guestlist", guestlist))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
