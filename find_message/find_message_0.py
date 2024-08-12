async def find_message_0(stage_id, choice):
    if stage_id == 0:
        if choice == 'a':
            return 1
        return 2
    elif stage_id < 3:
        return 3
