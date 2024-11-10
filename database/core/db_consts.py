from enum import Enum
from database.models.user import User
from database.models.choices import Choices
from database.models.game import Game
from database.models.transactions import Transactions
from database.models.promo import Promo
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
    USER = User
    PROMO = Promo
    CHOICES = Choices
    GAME = Game
    TRANSACTIONS = Transactions

class Columns(Enum):
    ID = 'id'
    TG_ID = 'tg_id'
    MESSAGE_ID = 'message_id'
    LANGUAGE = 'language'
    SENT_MESSAGE_ID = 'sent_message_id'
    CHOICE = 'choice'
    CODE = 'code'
    TOKENS = 'tokens'
    PREMIUM = 'premium'
    TRANSACTIONS_ID = 'transaction_id'
    MSG_ID = 'msg_id'
    DATE = 'date'
    REFUND = 'refund'
    VALUE = 'value'

class Operators(Enum):
    EQ = '=='
    NEQ = '!='
    GT = '>'
    LT = '<'
    GTE = '>='
    LTE = '<='

# Словарь операторов для фильтрации
operators = {
    Operators.EQ.value: eq,
    Operators.NEQ.value: ne,
    Operators.GT.value: gt,
    Operators.LT.value: lt,
    Operators.GTE.value: ge,
    Operators.LTE.value: le,
}
