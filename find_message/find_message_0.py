from database.db_operation import db


async def find_next_message_0(stage_id, choice):
    if stage_id == 0:
        if choice == 'a':
            return 1
        return 2
    elif stage_id < 3:
        return 3


async def find_previous_message_0(stage_id, tg_id):
    if stage_id < 3:
        await db(table=2, filters={1: tg_id, 5: '0_0'}, func=3)
        return 0
    elif stage_id == 3:
        choice = await db(table=2, filters={1: tg_id, 5: '0_0'}, data=6)
        if choice == 'a':
            return 1
        return 2
