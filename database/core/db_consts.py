from database.models.user import User
from database.models.choices import Choices
from database.models.game import Game
from database.models.transactions import Transactions
from database.models.promo import Promo

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

class Tables(Enum):
    USER = 0
    PROMO = 1
    CHOICES = 2
    GAME = 3
    TRANSACTIONS = 4


class Columns(Enum):
    ID = 0
    TG_ID = 1
    MESSAGE_ID = 2
    LANGUAGE = 3
    SENT_MESSAGE_ID = 4
    CHOICES_ID = 5
    RESULT_CHOICES = 6
    CODE = 7
    TOKENS = 8
    PREMIUM = 9
    TRANSACTIONS_ID = 10
    MSG_ID = 11
    DATE = 12
    REFUND = 13
    VALUE = 14


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
    1: Promo,
    2: Choices,
    3: Game,
    4: Transactions
}

COLUMNS = {
    0: 'id',
    1: 'tg_id',
    2: 'message_id',
    3: 'language',
    4: 'sent_message_id',
    5: 'choice_id',
    6: 'result_choice',
    7: 'code',
    8: 'tokens',
    9: 'premium',
    10: 'transaction_id',
    11: 'msg_id',
    12: 'date',
    13: 'refund',
    14: 'value'
}
