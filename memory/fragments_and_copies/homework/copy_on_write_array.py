"""
Реалізувати Copy-On-Write масив.

Copy-On-Write (COW) - структура, де кілька масивів можуть ділити один
спільний буфер даних. Копія створюється лише під час першої операції
запису у конкретний масив; читання не робить копій.

Вимоги:
    - Використати внутрішній @dataclass Storage(data, refcount);
    - Масиви, створені через cow_copy(), ділять один буфер;
    - Будь-який запис (set, delete, insert, append) має:
        - перевіряти refcount;
        - від’єднувати буфер (copy), якщо refcount > 1.
    - Не створювати копій при cow_copy() або читанні.

Актуальність:
    Програміст стикається з Copy-On-Write у задачах, де потрібно працювати
    з великими масивами даних без зайвих копій. Це підхід, який лежить в основі:
        - snapshot-структур (історія змін, undo/redo);
        - кешів та memoization, де потрібні lightweight-копії стану;
        - паралельних обчислень, коли кілька процесів читають спільні дані;
        - zero-copy операцій у NumPy, PyArrow, Pandas;
        - обробки файлів та буферів без дублювання памʼяті;
        - fork-процесів у Python, де сторінки памʼяті COW до першого запису.

    Вміння реалізувати COW у Python допомагає оптимізувати памʼять,
    будувати ефективні структури даних і розуміти, як працюють сучасні high-performance бібліотеки.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class Storage:
    """
    Внутрішній буфер для Copy-On-Write масиву.

    Поля:
        data     - фактичний список елементів.
        refcount - кількість масивів, що спільно використовують цей буфер.
    """

    data: list[Any]
    refcount: int = 1


class CopyOnWriteArray:
    """
    Copy-On-Write масив.

    Працює як звичайний список, але копіює дані лише тоді,
    коли відбувається запис у масив, що ділить буфер з іншими екземплярами.
    Корисно для оптимального використання памʼяті та легких "знімків" стану.
    """

    def __init__(self, items: Iterable[Any] | None = None) -> None:
        """
        Ініціалізує масив із власним буфером.
        Створює окремий Storage й не ділить його з іншими масивами (назви його _storage).
        """
        self._storage = Storage(list(items) if items is not None else [])

    def cow_copy(self) -> CopyOnWriteArray:
        """
        Повертає легку копію масиву, що розділяє той самий буфер.
        Копіювання даних не відбувається.
        """
        _array = CopyOnWriteArray.__new__(CopyOnWriteArray)
        _array._storage = self._storage
        self._storage.refcount += 1
        return _array

    def __len__(self) -> int:
        return len(self._storage.data)

    def __getitem__(self, index: int) -> Any:
        """
        Повертає елемент за індексом.
        Завжди читає напряму зі спільного буфера.
        """
        return self._storage.data[index]

    def _ensure_unique(self) -> None:
        if self._storage.refcount <= 1:
            return
        data = self._storage.data.copy()
        self._storage.refcount -= 1
        self._storage = Storage(data)  # refcount defaults to 1

    def __setitem__(self, index: int, value: Any) -> None:
        """
        Записує значення за індексом.
        Якщо буфер спільний - створює власну копію перед записом.
        """
        self._ensure_unique()
        self._storage.data[index] = value

    def __delitem__(self, index: int) -> None:
        """
        Видаляє елемент.
        Перед операцією може знадобитися відʼєднати власний буфер.
        """
        if self._storage.refcount > 1:
            self._storage = Storage(self._storage.data.copy())
        del self._storage.data[index]

    def insert(self, index: int, value: Any) -> None:
        """
        Вставляє новий елемент за індексом.
        При спільному буфері створює власну копію перед модифікацією.
        """
        if self._storage.refcount > 1:
            self._storage = Storage(self._storage.data.copy())
        self._storage.data.insert(index, value)

    def append(self, value: Any) -> None:
        """
        Додає елемент у кінець масиву.
        Викликає відʼєднання буфера за потреби.
        """
        if self._storage.refcount > 1:
            self._storage = Storage(self._storage.data.copy())
        self._storage.data.append(value)

    def to_list(self) -> list[Any]:
        """
        Повертає новий звичайний Python-список.
        Це завжди реальна копія даних.
        """
        return self._storage.data.copy()

    def __repr__(self) -> str:
        """
        Повертає зручне текстове представлення масиву для дебагу.
        Показує дані й стан буфера.
        """
        return f'CopyOnWriteArray(data={self._storage.data}, refcount={self._storage.refcount})'


### Self Checks ###
def test_copy_on_write_array():
    print('test_copy_on_write_array:')
    arr = CopyOnWriteArray([1, 2, 3])
    print(arr)
    arr2 = arr.cow_copy()
    print(arr2)
    arr2[1] = 99
    print('arr:', arr.to_list())
    print('arr2:', arr2.to_list())


def test_copy_on_write_array_2():
    print('test_copy_on_write_array_2:')
    arr = CopyOnWriteArray([1, 2, 3])
    print(arr)
    arr2 = arr.cow_copy()
    print(arr2)
    arr2[1] = 99
    print('arr:', arr.to_list())
    print('arr2:', arr2.to_list())
    del arr2
    print(arr)


def test_copy_on_write_array_3():
    print('test_copy_on_write_array_3:')
    arr = CopyOnWriteArray([1, 2, 3])
    arr2 = arr.cow_copy()
    print(f' is: {arr._storage is arr2._storage}')
    print(f' ==: {arr._storage == arr2._storage}')


def test_copy_on_write_array_4():
    print('test_copy_on_write_array_4:')
    arr = CopyOnWriteArray([1, 2, 3])
    arr2 = arr.cow_copy()
    print(f'refcount: {arr._storage.refcount}')
    print(f'refcount: {arr2._storage.refcount}')


def test_copy_list():
    print('test_copy_list:')
    arr = [1, 2, 3]
    arr2 = arr.copy()
    arr2[1] = 99
    print('arr:', arr)
    print('arr2:', arr2)


def test_copy_list_2():
    print('test_copy_list_2:')
    arr = [1, 2, 3]
    arr2 = arr
    arr2[1] = 99
    print('arr:', arr)
    print('arr2:', arr2)


def test_copy_list_3():
    print('test_copy_list_3:')
    arr = [1, 2, 3]
    arr2 = arr
    arr2.append(4)
    print('arr:', arr)
    print('arr2:', arr2)


def test_insert():
    print('test_insert:')
    arr = CopyOnWriteArray([1, 2, 3])
    arr.insert(1, 99)
    print(arr)


def test_insert_2():
    print('test_insert_2:')
    arr = CopyOnWriteArray([1, 2, 3])
    arr2 = arr.cow_copy()
    arr.insert(1, 99)
    print(arr)
    print(arr2)


if __name__ == '__main__':
    print('Self Checks:')
    # test_copy_on_write_array()
    # test_copy_on_write_array_2()
    # test_copy_on_write_array_3()
    # test_copy_on_write_array_4()

    # test_copy_list()
    # test_copy_list_2()
    # test_copy_list_3()

    # test_insert()
    # test_insert_2()
