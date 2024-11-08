from typing import Any, Dict, List, Optional, Tuple, Union
from webbrowser import Galeon

from sqlalchemy import select, update, delete, asc, desc, func as sql_func, and_
from sqlalchemy.exc import SQLAlchemyError

from traceback import print_exc

from database.core.db_consts import Tables, Columns, Operators, Method, Func
from app.consts import DEBUG
from database.core.db_session import create_async_session

# Словарь операторов для фильтрации
operators = {
    Operators.EQ.value: lambda col, val: col == val,
    Operators.NEQ.value: lambda col, val: col != val,
    Operators.GT.value: lambda col, val: col > val,
    Operators.LT.value: lambda col, val: col < val,
    Operators.GTE.value: lambda col, val: col >= val,
    Operators.LTE.value: lambda col, val: col <= val,
}

async def db(
    table: Tables = Tables.GAME,
    filters: Optional[Dict[Columns, Tuple[Operators, Any]]] = None,
    method: Method = Method.FIRST,
    data: Optional[Union[Columns, List[Columns], Dict[Columns, Any]]] = None,
    operation: Func = Func.RETURN,
    offset: int = 0,
    order_by: Optional[Tuple[Columns, bool]] = None
) -> Any:
    """
    Асинхронная функция для взаимодействия с базой данных с использованием Enums для таблиц, столбцов и операторов.

    Параметры:
        table (Tables): Таблица для запроса.
        filters (Optional[Dict[Columns, Tuple[Operators, Any]]]): Словарь фильтров, где ключ - столбец (Columns),
            значение - кортеж (оператор, значение).
        method (Method): Метод запроса (FIRST, ALL, COUNT).
        data (Optional[Union[Columns, List[Columns], Dict[Columns, Any]]]): Данные для выборки или изменения.
            - Для operation=RETURN: столбец или список столбцов для возврата.
            - Для operation=ADD или operation=UPDATE: словарь {столбец: значение}.
        operation (Func): Операция (RETURN, UPDATE, ADD, DELETE).
        offset (int): Смещение для запроса.
        order_by (Optional[Tuple[Columns, bool]]): Кортеж, где первый элемент - столбец для сортировки,
            второй - направление сортировки (True для возрастания, False для убывания).

    Возвращает:
        Any: Результат операции (данные, количество записей или статус выполнения).
    """
    try:
        # Получаем класс таблицы из Enums
        table_class = table.value
        if not table_class:
            raise ValueError(f"Неверная таблица: {table}")

        # Начальное построение запроса
        query = select(table_class)

        # Обработка фильтров
        if filters:
            filter_conditions = []
            for column_enum, (operator_enum, value) in filters.items():
                column_name = column_enum.value
                column_attr = getattr(table_class, column_name)
                op_func = operators.get(operator_enum.value)
                if not op_func:
                    raise ValueError(f"Неподдерживаемый оператор: {operator_enum}")
                filter_conditions.append(op_func(column_attr, value))

            if filter_conditions:
                query = query.where(and_(*filter_conditions))

        # Обработка сортировки
        if order_by:
            column_enum, ascending = order_by
            column_name = column_enum.value
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
                new_entity = table_class(**{col.value: val for col, val in data.items()})
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
                    elif isinstance(data, Columns):
                        column_name = data.value
                        return getattr(entity, column_name)
                    else:
                        return [getattr(entity, col.value) for col in data]

                elif method == Method.ALL:
                    result = await session.execute(query)
                    entities = result.scalars().all()
                    if data is None:
                        return entities
                    elif isinstance(data, Columns):
                        return [getattr(entity, data.value) for entity in entities]
                    else:
                        return [
                            [getattr(entity, col.value) for col in data]
                            for entity in entities
                        ]

                elif method == Method.COUNT:
                    count_query = select(sql_func.count()).select_from(table_class)
                    if filters:
                        count_query = count_query.where(and_(*filter_conditions))
                    result = await session.execute(count_query)
                    count = result.scalar_one()
                    return count

            elif operation == Func.UPDATE:
                if not isinstance(data, dict):
                    raise ValueError("Данные должны быть словарем для операции UPDATE")
                update_data = {col.value: val for col, val in data.items()}
                update_query = (
                    update(table_class)
                    .where(and_(*filter_conditions))
                    .values(**update_data)
                )
                await session.execute(update_query)
                await session.commit()
                return True

            elif operation == Func.DELETE:
                delete_query = delete(table_class).where(and_(*filter_conditions))
                await session.execute(delete_query)
                await session.commit()
                return True

    except SQLAlchemyError as e:
        if DEBUG:
            print_exc()
        return False
    except Exception as e:
        if DEBUG:
            print_exc()
        return False
