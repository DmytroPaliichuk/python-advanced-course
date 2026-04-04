from unittest import TestCase

from memory.fragments_and_copies.homework.copy_on_write_array import (
    CopyOnWriteArray,
)


class TestCopyOnWriteArray(TestCase):
    def test_initialization(self):
        arr = CopyOnWriteArray([1, 2, 3])
        self.assertEqual(len(arr), 3)
        self.assertEqual(arr.to_list(), [1, 2, 3])

    def test_cow_copy_shares_storage_initially(self):
        arr1 = CopyOnWriteArray([1, 2, 3])
        arr2 = arr1.cow_copy()

        # Обидві копії мають той самий буфер
        self.assertIs(arr1._storage, arr2._storage)
        self.assertEqual(arr1._storage.refcount, 2)

    def test_read_does_not_trigger_copy(self):
        arr1 = CopyOnWriteArray([10, 20, 30])
        arr2 = arr1.cow_copy()

        _ = arr2[1]  # читання не повинно створювати копію

        self.assertIs(arr1._storage, arr2._storage)
        self.assertEqual(arr1._storage.refcount, 2)

    def test_write_triggers_copy(self):
        arr1 = CopyOnWriteArray([1, 2, 3])
        arr2 = arr1.cow_copy()

        arr2[1] = 99  # тут має відбутися реальна копія

        # Буфери тепер різні
        self.assertIsNot(arr1._storage, arr2._storage)

        # Дані незалежні
        self.assertEqual(arr1.to_list(), [1, 2, 3])
        self.assertEqual(arr2.to_list(), [1, 99, 3])

        # Кожен має свій refcount
        self.assertEqual(arr1._storage.refcount, 1)
        self.assertEqual(arr2._storage.refcount, 1)

    def test_append_triggers_copy(self):
        arr1 = CopyOnWriteArray([1, 2])
        arr2 = arr1.cow_copy()

        arr2.append(3)  # мутація -> відʼєднання

        self.assertEqual(arr1.to_list(), [1, 2])
        self.assertEqual(arr2.to_list(), [1, 2, 3])

        self.assertIsNot(arr1._storage, arr2._storage)

    def test_insert_triggers_copy(self):
        arr1 = CopyOnWriteArray([1, 2])
        arr2 = arr1.cow_copy()

        arr2.insert(1, 99)

        self.assertEqual(arr1.to_list(), [1, 2])
        self.assertEqual(arr2.to_list(), [1, 99, 2])
        self.assertIsNot(arr1._storage, arr2._storage)

    def test_delete_triggers_copy(self):
        arr1 = CopyOnWriteArray([1, 2, 3])
        arr2 = arr1.cow_copy()

        del arr2[1]

        self.assertEqual(arr1.to_list(), [1, 2, 3])
        self.assertEqual(arr2.to_list(), [1, 3])
        self.assertIsNot(arr1._storage, arr2._storage)

    def test_multiple_copies_refcount(self):
        arr1 = CopyOnWriteArray([1])
        arr2 = arr1.cow_copy()
        arr3 = arr1.cow_copy()

        # Три масиви посилаються на один буфер
        self.assertIs(arr1._storage, arr2._storage)
        self.assertIs(arr1._storage, arr3._storage)
        self.assertEqual(arr1._storage.refcount, 3)

        arr2[0] = 10  # arr2 відʼєднується

        # arr1 і arr3 лишилися
        self.assertIs(arr1._storage, arr3._storage)
        self.assertIsNot(arr2._storage, arr1._storage)

        self.assertEqual(arr1._storage.refcount, 2)
        self.assertEqual(arr2._storage.refcount, 1)

    def test_to_list_returns_real_copy(self):
        arr = CopyOnWriteArray([1, 2, 3])
        lst = arr.to_list()

        lst.append(100)

        # Перевіряємо, що зміни у списку не впливають на масив
        self.assertEqual(arr.to_list(), [1, 2, 3])
        self.assertEqual(lst, [1, 2, 3, 100])

    def test_repr_contains_data_and_refcount(self):
        arr = CopyOnWriteArray([1, 2])
        r = repr(arr)
        self.assertIn('data=[1, 2]', r)
        self.assertIn('refcount=1', r)
