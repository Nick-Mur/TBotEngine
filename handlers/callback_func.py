from imports import *

from database.db_operation import *

from send_func import send


router = Router()


@router.callback_query(lambda call: 'plot' in call.data)
async def get_plot(call: CallbackQuery):
    tg_id = call.from_user.id
    phrase_id = await db(filters={1: tg_id}, data=7)
    if call.data.split('_')[1] == 'next':
        await db(filters={1: tg_id}, func=1, data={7: phrase_id + 1})
        back = False
    else:
        await db(filters={1: tg_id}, func=1, data={7: phrase_id - 1})
        back = True
    await send(call=call, back=back)


@router.callback_query()
async def handle_any_callback(call: CallbackQuery):
    print(1)
