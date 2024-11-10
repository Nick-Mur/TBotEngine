import re
from typing import Dict, List, Tuple, Optional


"""
example
1 > 2
2 > 3
3 > 4 [1=A + 2=B]
3 > 5 [1=B + 2=A]
3 > 6 [1=C + 3=A]
3 > 7 [else]
"""

def load_message_map(filepath: str) -> Dict[int, List[Tuple[int, Optional[List[Tuple[int, str]]]]]]:
    """
    Загружает карту сообщений из текстового файла.

    :param filepath: Путь к файлу карты сообщений.
    :return: Словарь с переходами между сообщениями.
    """
    transitions = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            # Парсим строку
            match = re.match(r'^(\d+)\s*>\s*(\d+)(?:\s*\[(.*)])?$', line)
            if not match:
                continue
            from_id = int(match.group(1))
            to_id = int(match.group(2))
            conditions_str = match.group(3)
            if conditions_str:
                conditions = parse_conditions(conditions_str)
            else:
                conditions = None
            if from_id not in transitions:
                transitions[from_id] = []
            transitions[from_id].append((to_id, conditions))
    return transitions

def parse_conditions(conditions_str: str) -> Optional[List[Tuple[int, str]]]:
    """
    Парсит строку условий в список кортежей.

    :param conditions_str: Строка условий, например "[1=A + 2=B]".
    :return: Список условий в виде кортежей (message_id, choice).
    """
    conditions = []
    conditions_parts = conditions_str.strip('[]').split('+')
    for cond in conditions_parts:
        cond = cond.strip()
        if cond.lower() == 'else':
            conditions.append(('else', None))
        else:
            match = re.match(r'^(\d+)=(\w+)$', cond)
            if match:
                message_id = int(match.group(1))
                choice = match.group(2)
                conditions.append((message_id, choice))
    return conditions
