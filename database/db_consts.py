from database.data.user import User
from database.data.save import Save
from database.data.choices import Choices
from database.data.game import Game
from database.data.transactions import Transactions

from enum import Enum
from operator import eq, ne, gt, lt, ge, le


# Перечисления для методов и функций
class Method(Enum):
    FIRST = 0
    ALL = 1
    COUNT = 2

class Func(Enum):
    RETURN = 0
    UPDATE = 1
    ADD = 2
    DELETE = 3

# Словарь операторов для фильтрации
operators = {
    '==': eq,
    '!=': ne,
    '>': gt,
    '<': lt,
    '>=': ge,
    '<=': le,
}


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
