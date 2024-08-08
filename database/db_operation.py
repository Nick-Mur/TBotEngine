from database.data.db_session import *
from database.data.user import User
from database.data.save import Save
from database.data.choices import Choices

from sqlalchemy import desc

from traceback import print_exc


DB_PATH = 'database\project.db'

TABLES = {
    0: User,
    1: Save,
    2: Choices
}

COLUMNS = {
    0: 'id',
    1: 'tg_id',
    2: '',
    3: 'language',
    4: 'stage_id',
    5: 'choice_id',
    6: 'result_choice',
    7: 'phrase_id',
    8: 'text',
    9: 'media',
    10: 'keyboard',
    11: 'msg_id'
}


async def db(table=1, filters=None, method=0, data=None, func=0, offset=0, order_by=None, special_filter=False):
    """
    Выполняет запрос к базе данных с динамическими фильтрами, сортировкой и выборкой полей.

    Параметры:
    table (int): индекс таблицы для запроса.
    filters (dict): Словарь фильтров, где ключ - индекс столбца, а значение - строка с условием фильтрации (например, ">1").
    method (int): Метод запроса ('0' для получения первой записи, или '1' для получения всех записей, или '2' для получения количества записей).
    data (list): Список имен полей, значения которых нужно вернуть.
    offset (int, optional): Смещение для запроса (начиная с какой записи возвращать результат).
    order_by (tuple, optional): Кортеж, где первый элемент - индекс столбца для сортировки, второй - направление (True для возрастания, False для убывания).
    func (int): индекс операции ('0' - возвращение, '1' - обновление, '2' - добавление, '3' - удаление записи)

    Возвращает:
    list: Список значений указанных полей для найденных записей.
    False: В случае возникновения ошибки при выполнении запроса.
    """
    try:
        global_init(DB_PATH)
        session = create_session()
        table_class = TABLES.get(table)
        query = session.query(table_class)

        if not filters:
            filters = dict()
        elif not special_filter:
            for key, value in filters.items():
                value = f"=={value}" if isinstance(value, int) else f'=="{value}"'
                filters[key] = value
        for index_column, filter_value in filters.items():
            column = COLUMNS[index_column]
            query = query.filter(eval(f'{table_class.__name__}.{column}{filter_value}'))
        if order_by:
            index_column, direction = order_by
            column = COLUMNS[index_column]
            if direction:
                query = query.order_by(eval(f'{table_class.__name__}.{column}'))
            else:
                query = query.order_by(desc(eval(f'{table_class.__name__}.{column}')))

        if offset:
            query = query.offset(offset)
        if method == 0:
            entity = query.first()
            if entity is None: return None
            entities = [entity]
        elif method == 1:
            entities = query.all()
        elif method == 2:
            return query.count()
        if func == 0:
            # Возвращение данных
            if data is None: data = list()
            if not isinstance(data, list): data = [data]
            result = list()
            for entity in entities:
                entity_result = list()
                for index_setting_name in data:
                    setting_name = COLUMNS[index_setting_name]
                    if hasattr(entity, setting_name):
                        entity_result.append(getattr(entity, setting_name))
                result.append(entity_result)
            if len(result) == 1:
                result = result[0]
                if len(result) == 1 and result:
                    result = result[0]
                elif len(result) == 0:
                    result = False
            return result

        elif func == 1:
            # Обновление данных
            if not data: data = dict()
            for entity in entities:
                for index_column, value in data.items():
                    column = COLUMNS[index_column]
                    if hasattr(entity, column):
                        setattr(entity, column, value)
            session.commit()
            return True

        elif func == 2:
            # Добавление данных
            if not data: data = dict()
            new_entity = table_class(**{COLUMNS[index_column]: value for index_column, value in data.items()})
            session.add(new_entity)
            session.commit()

            return True

        elif func == 3:
            # Удаление данных
            for entity in entities:
                session.delete(entity)
            session.commit()
            return True

    except Exception:
        print_exc()
        session.rollback()
        return False

    finally:
        session.close()
