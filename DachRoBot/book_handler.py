from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from event import Event

BOOK, TICKETS = range(2)


def isNumber(inputString):
    return any(char.isdigit() for char in inputString)


def check_available_tickets(update, personCount):
    event = Event()
    if personCount < 1:
        update.message.reply_text(
            'Sorry but ghosts aren\'t invited.')
        return False

    elif (event.maxTickets - sum(event.guests.values())) - personCount < 0:
        update.message.reply_text(
            'There are only ' + str(event.maxTickets - sum(event.guests.values())) + ' available. How many of these tickets do you want to book?')
        return False

    else:
        return True


def tickets(update, context):
    event = Event()
    if not isNumber(update.message.text):
        update.message.reply_text(
            'Please write a number.')
        return TICKETS

    if check_available_tickets(update, int(update.message.text)) == True:
        event.upsertGuest(update.effective_user.full_name,
                          int(update.message.text))

        update.message.bot.edit_message_text(chat_id=event.chat_id, message_id=event.pinned_message_id, text=str(event.event_text) + '\nTickets for this event: ' +
                                             str(event.maxTickets) + '\nTickets still available: ' + str(event.maxTickets - sum(event.guests.values())))

        return ConversationHandler.END
    else:
        return TICKETS


def book(update, context):
    event = Event()
    if event.limited == False:
        update.message.reply_text(
            'This event isn\'t a limited one, you can\'t book ticket.')
        return ConversationHandler.END

    elif event.maxTickets - sum(event.guests.values()) == 0:
        update.message.reply_text(
            'Be faster next time because this event is already sold out.')
        return ConversationHandler.END

    elif isNumber(update.message.text):
        if ' ' in update.message.text:
            text = update.message.text
            personCount = int(text.split(' ', 1)[1])
        else:
            personCount = int(update.message.text)

        if check_available_tickets(update, personCount) == True:
            event.upsertGuest(update.effective_user.full_name, personCount)

            update.message.bot.edit_message_text(chat_id=event.chat_id, message_id=event.pinned_message_id, text=str(event.event_text) + '\nTickets for this event: ' +
                                                 str(event.maxTickets) + '\nTickets still available: ' + str(event.maxTickets - sum(event.guests.values())))
            return ConversationHandler.END
        else:
            return TICKETS

    else:
        update.message.reply_text(
            'For how many people do you want to book?')
        return TICKETS


book_handler = ConversationHandler(
    entry_points=[CommandHandler('book', book)],

    states={
        TICKETS: [MessageHandler(Filters.text, tickets)],
        BOOK: [MessageHandler(Filters.text, book)],
    },

    fallbacks=[CommandHandler('book', book)]
)
