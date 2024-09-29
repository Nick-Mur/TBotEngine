from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import select, update, delete, asc, desc, func as sql_func

from traceback import print_exc

from database.db_consts import *
from consts import DEBUG
from database.data.db_session import create_async_session


async def db(
    table: int = 3,
    filters: Optional[Dict[int, Tuple[str, Any]]] = None,
    method: Method = Method.FIRST,
    data: Optional[Union[int, List[int], Dict[int, Any]]] = None,
    operation: Func = Func.RETURN,
    offset: int = 0,
    order_by: Optional[Tuple[int, bool]] = None
) -> Any:
    """
    Асинхронная функция для взаимодействия с базой данных с динамическими фильтрами, сортировкой и выборкой полей.

    Параметры:
        session (AsyncSession): Асинхронная сессия базы данных.
        table (int): Индекс таблицы для запроса (см. словарь TABLES).
        filters (Optional[Dict[int, Tuple[str, Any]]]): Словарь фильтров, где ключ - индекс столбца,
            а значение - кортеж (оператор, значение). Операторы: '==', '!=', '>', '<', '>=', '<='.
        method (Method): Метод запроса (FIRST, ALL, COUNT).
        data (Optional[Union[int, List[int], Dict[int, Any]]]): Данные для выборки или изменения.
            - Для db_func=RETURN: индекс или список индексов столбцов для возврата.
            - Для db_func=ADD или func=UPDATE: словарь {индекс_столбца: значение}.
        db_func (Func): Операция (RETURN, UPDATE, ADD, DELETE).
        offset (int): Смещение для запроса (начиная с какой записи возвращать результаты).
        order_by (Optional[Tuple[int, bool]]): Кортеж, где первый элемент - индекс столбца для сортировки,
            второй - направление (True для возрастания, False для убывания).

    Возвращает:
        Any: Результат операции (данные, количество записей или статус выполнения).
    """
    try:
        table_class = TABLES.get(table)
        if not table_class:
            raise ValueError(f"Неверный индекс таблицы: {table}")

        # Начальное построение запроса
        query = select(table_class)

        # Обработка фильтров
        if filters:
            for index_column, (operator_str, value) in filters.items():
                column_name = COLUMNS.get(index_column)
                if not column_name:
                    raise ValueError(f"Неверный индекс столбца: {index_column}")
                column_attr = getattr(table_class, column_name)
                op_func = operators.get(operator_str)
                if not op_func:
                    raise ValueError(f"Неподдерживаемый оператор: {operator_str}")
                query = query.where(op_func(column_attr, value))

        # Обработка сортировки
        if order_by:
            index_column, ascending = order_by
            column_name = COLUMNS.get(index_column)
            if not column_name:
                raise ValueError(f"Неверный индекс столбца для сортировки: {index_column}")
            column_attr = getattr(table_class, column_name)
            query = query.order_by(asc(column_attr) if ascending else desc(column_attr))

        # Обработка смещения
        if offset:
            query = query.offset(offset)
        async with create_async_session() as session:
            # Выполнение операций
            if operation == Func.ADD:
                if not isinstance(data, dict):
                    raise ValueError("Данные должны быть словарем для операции ADD")
                new_entity = table_class(**{COLUMNS[k]: v for k, v in data.items()})
                session.add(new_entity)
                await session.commit()
                return True

            elif operation == Func.RETURN:
                if method == Method.FIRST:
                    result = await session.execute(query)
                    entity = result.scalars().first()
                    if not entity:
                        return None
                    if data is None:
                        return entity
                    elif isinstance(data, int):
                        column_name = COLUMNS.get(data)
                        return getattr(entity, column_name)
                    else:
                        return [getattr(entity, COLUMNS[idx]) for idx in data]

                elif method == Method.ALL:
                    result = await session.execute(query)
                    entities = result.scalars().all()
                    if data is None:
                        return entities
                    else:
                        return [
                            [getattr(entity, COLUMNS[idx]) for idx in data]
                            for entity in entities
                        ]

                elif method == Method.COUNT:
                    count_query = select(sql_func.count()).select_from(table_class)
                    result = await session.execute(count_query)
                    count = result.scalar_one()
                    return count

            elif operation == Func.UPDATE:
                if not isinstance(data, dict):
                    raise ValueError("Данные должны быть словарем для операции UPDATE")
                update_data = {COLUMNS[k]: v for k, v in data.items()}
                update_query = (
                    update(table_class)
                    .where(*query._where_criteria)
                    .values(**update_data)
                )
                await session.execute(update_query)
                await session.commit()
                return True

            elif operation == Func.DELETE:
                delete_query = delete(table_class).where(*query._where_criteria)
                await session.execute(delete_query)
                await session.commit()
                return True

    except Exception as e:
        if DEBUG:
            print_exc()
        return False
