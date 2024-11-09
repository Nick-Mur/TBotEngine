from resources.buttons import *
from aiogram.types import InlineKeyboardMarkup


Keyboard = InlineKeyboardMarkup
basic_0 = [[back_0_btn, next_0_btn]]
back_0 = [[back_0_btn]]
next_0 = [[next_0_btn]]

ab_0 = [[a_0_btn, b_0_btn], [back_0_btn]]

close_keyboard = Keyboard(inline_keyboard=[[close_btn]])
close_ad_keyboard = Keyboard(inline_keyboard=[[close_ad_btn]])
language_keyboard = Keyboard(inline_keyboard=[[close_btn], [rus_btn, eng_btn]])
restart_keyboard = Keyboard(inline_keyboard=[[confirm_restart_btn, close_btn]])
