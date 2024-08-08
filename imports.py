import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from text.phrases.ru_phrases import *
from text.media import *
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, FSInputFile


from special.special_func import *

from sqlalchemy import Column, Integer, String
from database.data.db_session import SqlAlchemyBase
