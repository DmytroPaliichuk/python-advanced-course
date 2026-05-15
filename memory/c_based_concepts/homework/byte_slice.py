"""
Завдання:
    Реалізувати zero-copy аналог slicing для bytes.

Пояснення:
    ByteSlice повинен працювати як view на частину великого буфера.
    Він НЕ має створювати копії bytes при slicing або індексації - тільки
    перераховувати індекси й тримати посилання на один спільний буфер (memoryview).

Вимоги:
    - ByteSlice(data, start, end) -> не копіює дані;
    - bs[i]       -> повертає один байт як int;
    - bs[i:j]     -> повертає новий ByteSlice без копій;
    - len(bs)     -> довжина піддіапазону;
    - bytes(bs)   -> явне створення копії (дозволено);
    - Працює з bytes, bytearray, memoryview.

Що слід реалізувати:
    - усі методи нижче;
    - логіку обробки меж індексів;
    - zero-copy slicing;
    - докладний repr.

Примітка:
    Заборонено використовувати data[start:end] всередині (крім bytes() / to_bytes()).

Актуальність:
    Ця задача показує, як працювати з великими двійковими буферами без зайвих копій -
    важлива техніка у виробничих системах. Zero-copy slicing використовується під час
    парсингу мережевих протоколів (HTTP, gRPC, TCP-фрейми), роботи з великими файлами
    (логи, відео, сенсорні дані), обробки binary-форматів (Protobuf, Avro), у стрімінгу
    та mmap-файлах. У цих випадках один великий буфер часто нарізається на тисячі
    підфрагментів, і класичний bytes-slice створює стільки ж копій у памʼяті.
    Zero-copy дозволяє уникати цих алокацій, працювати напряму з даними і значно
    зменшувати навантаження на RAM та GC.
"""

from __future__ import annotations

from typing import Iterator


class ByteSlice:
    """
    Zero-copy представлення частини bytes/bytearray.

    Слід реалізувати:
        - ініціалізацію з посиланням на memoryview;
        - індексацію;
        - slicing;
        - перетворення в bytes;
        - коректну роботу з негативними індексами;
        - читабельний __repr__.
    """

    __slots__ = ('_buffer', '_start', '_end')

    def __init__(
        self,
        data: bytes | bytearray | memoryview,
        start: int = 0,
        end: int | None = None,
    ):
        """
        Ініціалізація ByteSlice.

        Параметри:
            data  - вихідні bytes або bytearray.
            start - початок піддіапазону.
            end   - кінець піддіапазону (не обовʼязковий).

        Має створювати memoryview(data) та зберігати тільки вказівники.
        Не повинно бути жодних копій даних.
        """
        # TODO: implement solution
        ...

    def __len__(self) -> int:
        """
        Повернути довжину зрізу.

        Має бути O(1).
        """
        # TODO: implement solution
        ...

    def __getitem__(self, item: int | slice) -> int | ByteSlice:
        """
        Підтримка індексації та slicing.

        Якщо item - int:
            повернути один байт (int 0–255).

        Якщо item - slice:
            повернути новий ByteSlice, який посилається на той же буфер.

        Заборонено робити копії bytes.
        """
        # TODO: implement solution
        ...

    def __iter__(self) -> Iterator[int]:
        """
        Ітерація по байтах, як у звичайних bytes.

        Повертати int для кожного байта.
        """
        # TODO: implement solution
        ...

    def __bytes__(self) -> bytes:
        """
        Створити копію даних.

        Єдиний дозволений спосіб створення bytes-обʼєкта всередині класу.
        """
        # TODO: implement solution
        ...

    def to_bytes(self) -> bytes:
        """
        Alias для bytes(self).

        Можна викликати руками - повинен повертати копію вмісту ByteSlice.
        """
        # TODO: implement solution
        ...

    def __repr__(self) -> str:
        """
        Повернути зручне текстове представлення.
        Має бути корисно для дебагу.
        """
        # TODO: implement solution
        ...
