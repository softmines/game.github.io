import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties

from bot.general.states import Admin
from bot.general.bothandler import BotHandler
from bd.database import Database
from properties.config import BOT_TOKEN, DATABASE_PATH

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
router = Dispatcher()
logging.basicConfig(level=logging.INFO)
botHandler = BotHandler(bot, Database(DATABASE_PATH))


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await botHandler.start(message, state)
    await botHandler.notify_about_new_press_start(message)


@router.message(Command('mail_reg'))
async def prepare_send_mailing_for_reg(message: Message, state: FSMContext):
    await botHandler.prepare_send_mailing_for_reg(message, state)


@router.message(Command('mail_unreg'))
async def prepare_send_mailing_for_unreg(message: Message, state: FSMContext):
    await botHandler.prepare_send_mailing_for_unreg(message, state)


@router.message(StateFilter(Admin.sending_message))
async def get_mail_for_send(message: Message, state: FSMContext):
    await botHandler.send_mail(message, state)


@router.callback_query()
async def handler_callbacks(callbackQuery: CallbackQuery, state: FSMContext):
    message = callbackQuery.message
    queryType = callbackQuery.data.split("$")[0]
    queryData = callbackQuery.data.split("$")[1]

    if queryType == "show_registration":
        await botHandler.registration(message)
    elif queryType == "show_instruction":
        await botHandler.show_instruction(message)
    elif queryType == "get_signal":
        await botHandler.get_signal(message, state)
    elif queryType == "back_to_welcome_menu":
        await botHandler.back_to_welcome_menu(message, state)
    elif queryType == "set_language":
        await botHandler.register_user(message, queryData)
        await botHandler.start(message, state)


async def main():
    await botHandler.init()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
