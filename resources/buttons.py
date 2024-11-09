from aiogram.types import InlineKeyboardButton


Button = InlineKeyboardButton

close_btn = Button(text='❌', callback_data='close')
close_ad_btn = Button(text="❌", callback_data="close_ad")

rus_btn = Button(text="Русский", callback_data="language_ru")
eng_btn = Button(text="English", callback_data="language_eng")



next_0_btn = Button(text='➡️', callback_data='next_0')
back_0_btn = Button(text='⬅️', callback_data='back_0')

a_0_btn = Button(text='A', callback_data='next_0_a')
b_0_btn = Button(text='B', callback_data='next_0_b')
