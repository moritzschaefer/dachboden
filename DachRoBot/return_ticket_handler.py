from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from event import Event

RETURNTICKET, NEW_FREE_TICKET = range(2)


def isNumber(inputString):
    return any(char.isdigit() for char in inputString)


def returnticket(update, context):
    event = Event()
    if not update.effective_user.full_name in event.guests:
        update.message.reply_text(
            'You didn\'t book a ticket for this event.')
        return ConversationHandler.END

    if isNumber(update.message.text):
        text = update.message.text
        personCount = int(text.split(' ', 1)[1])

        if personCount > event.maxTickets:
            update.message.reply_text(
                'You can\'t return more than the maximum number of tickets for this event.')
            return ConversationHandler.END

        full_name = update.effective_user.full_name
        if full_name in event.guests:
            if event.guests[full_name] >= personCount:
                event.upsertGuest(full_name, - personCount)
                if event.guests[full_name] == 0:
                    event.deleteGuest(full_name)

            else:
                update.message.reply_text(
                    'You booked less tickets than the number you want to return.')
                return ConversationHandler.END

        update.message.bot.edit_message_text(chat_id=update.message.chat_id, message_id=event.pinned_message_id, text=str(event.event_text) + '\nTickets for this event: ' +
                                             str(event.maxTickets) + '\nTickets still available: ' + str(event.maxTickets - sum(event.guests.values())))
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'How many tickets do you want to return? \n Next time, you can send me /returnticket with the number of tickets you want return.')
        return NEW_FREE_TICKET


def new_free_ticket(update, context):
    event = Event()
    if update.effective_user.full_name in event.guests:
        full_name = update.effective_user.full_name
        if event.guests[full_name] >= int(update.message.text):
            event.upsertGuest(full_name, - int(update.message.text))
        else:
            update.message.reply_text(
                'You booked less tickets than the number you want to return.')
            return ConversationHandler.END

    update.message.bot.edit_message_text(chat_id=update.message.chat_id, message_id=event.pinned_message_id, text=str(event.event_text) + '\nTickets for this event: ' +
                                         str(event.maxTickets) + '\nTickets still available: ' + str(event.maxTickets - sum(event.guests.values())))

    return ConversationHandler.END


return_ticket_handler = ConversationHandler(
    entry_points=[CommandHandler('returnticket', returnticket)],

    states={
        NEW_FREE_TICKET: [MessageHandler(Filters.text, new_free_ticket)],
    },

    fallbacks=[CommandHandler('returnticket', returnticket)]
)
