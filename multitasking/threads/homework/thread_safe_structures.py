"""
Завдання:
    Реалізувати потокобезпечні структури даних на основі однозв’язного списку.

    Частина 1 - LinkedList:
        - Реалізувати клас LinkedList;
        - Забезпечити коректне оновлення вказівників head, tail та лічильника елементів.

    Частина 2 - ThreatSafeLinkedList:
        - Усі операції мають бути потокобезпечними (використати Lock);
        - Гарантувати, що одночасні записи/читання не шкодять структурі.

    Частина 3 - HashTable:
        - Реалізувати хеш-таблицю з фіксованою кількістю бакетів;
        - Кожен бакет - окремий LinkedList;
        - Розподіл по бакетах: key % buckets.

    Частина 4 - ThreatSafeHashTable (наївна версія):
        - Зробити потокобезпечну хеш-таблицю з одним глобальним Lock;
        - Проаналізувати: чому така реалізація блокує конкурентність?

    Частина 5 - FastThreatSafeHashTable (оптимальна версія):
        - Замість глобального Lock використовувати ThreatSafeLinkedList у кожному бакеті;
        - Дозволити незалежне виконання операцій у різних бакетах;
        - Проаналізувати: чому це забезпечує реальну конкурентність.

Вимоги:
    - Заборонено використовувати dict, queue, set або готові потокобезпечні структури;
    - Дозволяється лише threading та Lock;
    - Код має бути чистим, інкапсульованим, без глобальних змінних;
    - Інтерфейси класів не змінювати.

Актуальність:
    Робота з потоками у Python часто призводить до неправильної поведінки через гонки потоків,
    якщо дані не захищені від одночасного доступу. LinkedList і HashTable -
    класичні приклади структур, які легко зламати конкурентними операціями.

    Це завдання дозволяє:
        - побачити реальні прояви race conditions;
        - зрозуміти різницю між глобальним блокуванням і локальним блокуванням;
        - навчитись будувати потокобезпечні структури з нуля;
        - виміряти вплив блокувань на продуктивність.

    Цей досвід формує практичне розуміння того, як будувати конкурентні системи,
    як уникати contention, та чому важливо правильно обирати рівень блокування.
"""


class Node:
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value
        self.next = None

    def __repr__(self):
        return f'Node({self.key}, {self.value})'


class LinkedList:
    def __init__(self):
        # TODO: implement solution
        ...

    def add_node(self, node: Node) -> None:
        """Додає вузол у хвіст списку."""
        # TODO: implement solution
        ...

    def pop_head(self) -> Node | None:
        """Видаляє та повертає вузол з голови (FIFO)."""
        # TODO: implement solution
        ...

    def find(self, key: int) -> Node | None:
        """Повертає вузол із заданим ключем або None."""
        # TODO: implement solution
        ...

    @property
    def count(self) -> int:
        """Поточна кількість елементів."""
        # TODO: implement solution
        ...


class ThreatSafeLinkedList(LinkedList):
    def __init__(self):
        # TODO: implement solution
        ...

    def add_node(self, node: Node) -> None:
        """Потокобезпечне додавання елемента."""
        # TODO: implement solution
        ...

    def pop_head(self) -> Node | None:
        """Потокобезпечне повернення голови."""
        # TODO: implement solution
        ...

    def find(self, key: int) -> Node | None:
        """Потокобезпечний пошук."""
        # TODO: implement solution
        ...


class HashTable:
    def __init__(self, buckets: int = 3):
        # TODO: implement solution
        ...

    def add(self, key: int, value: int) -> None:
        """Додає елемент у відповідний бакет."""
        # TODO: implement solution
        ...

    def get(self, key: int) -> Node | None:
        """Повертає елемент за ключем."""
        # TODO: implement solution
        ...


class ThreatSafeHashTable(HashTable):
    """Потокобезпечна, але з одним глобальним блокуванням."""

    def __init__(self, buckets: int = 3):
        """
        Кожен бакет має бути LinkedList.
        З глобальним lock.
        """
        # TODO: implement solution
        ...

    def add(self, key: int, value: int) -> None:
        """Потокобезпечне додавання з глобальним Lock."""
        # TODO: implement solution
        ...

    def get(self, key: int) -> Node | None:
        """Потокобезпечний пошук з глобальним Lock."""
        # TODO: implement solution
        ...


class FastThreatSafeHashTable(HashTable):
    """Оптимальна потокобезпечна."""

    def __init__(self, buckets: int = 3):
        """
        Кожен бакет має бути ThreatSafeLinkedList.
        Без глобального lock.
        """
        # TODO: implement solution
        ...

    def add(self, key: int, value: int) -> None:
        """Додає елемент, блокуючи тільки потрібний бакет."""
        # TODO: implement solution
        ...

    def get(self, key: int) -> Node | None:
        """Пошук у відповідному бакеті."""
        # TODO: implement solution
        ...
