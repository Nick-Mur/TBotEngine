from database.data.user import User
from database.data.save import Save
from database.data.choices import Choices
from database.data.game import Game
from database.data.transactions import Transactions

TABLES = {
    0: User,
    1: Save,
    2: Choices,
    3: Game,
    4: Transactions
}

COLUMNS = {
    0: 'id',
    1: 'tg_id',
    2: 'type_id',
    3: 'language',
    4: 'stage_id',
    5: 'choice_id',
    6: 'result_choice',
    7: 'phrase_id',
    8: 'tokens',
    9: 'premium',
    10: 'transaction_id',
    11: 'msg_id',
    12: 'date',
    13: 'refund'
}
