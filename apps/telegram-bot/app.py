#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using nested ConversationHandlers.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import io
import logging
import os
from typing import Any, Dict, Tuple

from dotenv import dotenv_values
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, ADDING_MEMBER, ADDING_SELF, DESCRIBING_SELF = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(
    PARENTS,
    CHILDREN,
    SELF,
    GENDER,
    MALE,
    FEMALE,
    AGE,
    NAME,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(10, 22))


# Helper
def _name_switcher(level: str) -> Tuple[str, str]:
    if level == PARENTS:
        return 'Pai', 'Mãe'
    return 'Irmão', 'Irmã'


# Top level conversation callbacks
def start(update: Update, context: CallbackContext) -> str:
    """Select an action: Adding parent/child or show data."""
    text = (
        "Você pode escolher adicionar um membro da família, você mesmo, exibir as informações coletadas ou terminar "
        "a nossa coversa. Para abortar, digite /stop."
    )

    buttons = [
        [
            InlineKeyboardButton(text='Adicionar membro da família', callback_data=str(ADDING_MEMBER)),
            InlineKeyboardButton(text='Adicionar você mesmo', callback_data=str(ADDING_SELF)),
        ],
        [
            InlineKeyboardButton(text='Exibir informações', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Finalizar', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(
            "Olá, eu sou a Paola e eu sou um bot que vai ajudar você a coletar informações sobre a sua família."
        )
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def adding_self(update: Update, context: CallbackContext) -> str:
    """Add information about yourself."""
    context.user_data[CURRENT_LEVEL] = SELF
    text = 'Certo, por favor me conte sobre você.'
    button = InlineKeyboardButton(text='Adicionar informação', callback_data=str(MALE))
    keyboard = InlineKeyboardMarkup.from_button(button)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return DESCRIBING_SELF


def show_data(update: Update, context: CallbackContext) -> str:
    """Pretty print gathered data."""

    def prettyprint(user_data: Dict[str, Any], level: str) -> str:
        people = user_data.get(level)
        if not people:
            return '\nSem informações por enquanto.'

        text = ''
        if level == SELF:
            for person in user_data[level]:
                text += f"Nome: {person.get(NAME, '-')}, Idade: {person.get(AGE, '-')}"
        else:
            male, female = _name_switcher(level)

            for person in user_data[level]:
                gender = female if person[GENDER] == FEMALE else male
                text += f"\n{gender}: Nome: {person.get(NAME, '-')}, Idade: {person.get(AGE, '-')}"
        return text

    user_data = context.user_data
    text = f"Você:{prettyprint(user_data, SELF)}"
    text += f"\n\Seus pais:{prettyprint(user_data, PARENTS)}"
    text += f"\n\Seus filhos:{prettyprint(user_data, CHILDREN)}"

    buttons = [[InlineKeyboardButton(text='Voltar', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Certo, até mais!')

    return END


def end(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = 'Até uma próxima!'
    update.callback_query.edit_message_text(text=text)

    return END


# Second level conversation callbacks
def select_level(update: Update, context: CallbackContext) -> str:
    """Choose to add a parent or a child."""
    text = 'Você pode adicionar um de seus pais ou uma criança. Você pode visualizar as informações já coletadas ou voltar.'
    buttons = [
        [
            InlineKeyboardButton(text='Adicionar pais', callback_data=str(PARENTS)),
            InlineKeyboardButton(text='Adicionar filhos', callback_data=str(CHILDREN)),
        ],
        [
            InlineKeyboardButton(text='Visualizar informações', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Voltar', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL


def select_gender(update: Update, context: CallbackContext) -> str:
    """Choose to add mother or father."""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    text = 'Por favor escolha quem você quer adicionar.'

    male, female = _name_switcher(level)

    buttons = [
        [
            InlineKeyboardButton(text=f'Adicionar {male}', callback_data=str(MALE)),
            InlineKeyboardButton(text=f'Adicionar {female}', callback_data=str(FEMALE)),
        ],
        [
            InlineKeyboardButton(text='Visualizar informações', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Voltar', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_GENDER


def end_second_level(update: Update, context: CallbackContext) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


# Third level callbacks
def select_feature(update: Update, context: CallbackContext) -> str:
    """Select a feature to update for the person."""
    buttons = [
        [
            InlineKeyboardButton(text='Nome', callback_data=str(NAME)),
            InlineKeyboardButton(text='Idade', callback_data=str(AGE)),
            InlineKeyboardButton(text='Finalizar', callback_data=str(END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {GENDER: update.callback_query.data}
        text = 'Por favor seleciona a informação que deseja atualizar.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Entendi! Por favor selecione a informação que deseja atualizar.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


def ask_for_input(update: Update, context: CallbackContext) -> str:
    """Prompt user to input data for selected feature."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Ok, me conta aí!'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_input(update: Update, context: CallbackContext) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text

    user_data[START_OVER] = True

    return select_feature(update, context)


def end_describing(update: Update, context: CallbackContext) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]
    if not user_data.get(level):
        user_data[level] = []
    user_data[level].append(user_data[FEATURES])

    # Print upper level menu
    if level == SELF:
        user_data[START_OVER] = True
        start(update, context)
    else:
        select_level(update, context)

    return END


def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    update.message.reply_text('Ok, tchau.')

    return STOPPING


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    #token_file = open('token.txt', 'r')
    #token = token_file.readline()
    config = dotenv_values(".env")
    updater = Updater(config['TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Set up third level ConversationHandler (collecting features)
    description_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_feature, pattern='^' + str(MALE) + '$|^' + str(FEMALE) + '$'
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$')
            ],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input)],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            # Return to second level menu
            END: SELECTING_LEVEL,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )

    # Set up second level ConversationHandler (adding a person)
    add_member_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_level, pattern='^' + str(ADDING_MEMBER) + '$')],
        states={
            SELECTING_LEVEL: [
                CallbackQueryHandler(select_gender, pattern=f'^{PARENTS}$|^{CHILDREN}$')
            ],
            SELECTING_GENDER: [description_conv],
        },
        fallbacks=[
            CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the second level
    # conversation, we need to make sure the top level conversation can also handle them
    selection_handlers = [
        add_member_conv,
        CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
        CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
        CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            DESCRIBING_SELF: [description_conv],
            STOPPING: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
