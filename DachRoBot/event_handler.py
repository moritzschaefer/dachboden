from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from event import Event


EVENT, TELL, DONE, LIMITED = range(4)


def isNumber(inputString):
    return any(char.isdigit() for char in inputString)


def create_event(update, context):
    event = Event()
    if event.pinned_event == True:
        update.message.reply_text(
            'You can\'t create a new event, one is already planned.')
        return ConversationHandler.END

    if isNumber(update.message.text):
        text = update.message.text
        event.maxTickets = int(text.split(' ', 1)[1])
        if event.maxTickets > 1:
            event.limited = True
            update.message.reply_text(
                'Tell me more about this limited (' + str(event.maxTickets) + ') event.')
        else:
            event.limited = False
            update.message.reply_text(
                'Tell me more about this crazy event.')
        return TELL

    else:
        update.message.reply_text(
            'How many people can attend? Write 0 if it is unlimited. \n For the next time, you can send me /event with the number of limited tickets.')
        return LIMITED


def tell(update, context):
    event = Event()
    event.event_text = update.message.text
    event.guests = {}

    if event.limited == True:
        message = update.message.bot.send_message(chat_id=event.chat_id, text=update.message.text + '\n\nTickets for this event: ' +
                                                  str(event.maxTickets) + '\nTickets still available: ' + str(event.maxTickets - sum(event.guests.values())))
        update.message.bot.pin_chat_message(chat_id=event.chat_id,
                                            message_id=message.message_id)

    else:
        message = update.message.bot.send_message(
            chat_id=event.chat_id, text=update.message.text)
        update.message.bot.pin_chat_message(chat_id=event.chat_id,
                                            message_id=message.message_id)

    event.pinned_message_id = message.message_id
    event.pinned_message_user = update.effective_user.full_name
    event.pinned_event = True

    return ConversationHandler.END


def limited(update, context):
    event = Event()
    if update.message.text == '0':
        event.limited = False
        update.message.reply_text(
            'Soooo, tell me everything about this random event.')
        return TELL

    else:
        event.limited = True
        event.maxTickets = int(update.message.text)
        update.message.reply_text(
            'Tell me more about this VIP event.')
        return TELL


event_handler = ConversationHandler(
    entry_points=[CommandHandler('event', create_event)],

    states={
        TELL: [MessageHandler(Filters.text, tell)],
        LIMITED: [MessageHandler(Filters.text, limited)],
    },

    fallbacks=[CommandHandler('event', create_event)]
)
