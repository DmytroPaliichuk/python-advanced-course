import sys

from pympler import asizeof

from memory.c_based_concepts.homework.byte_slice import ByteSlice


class TestByteSlice:
    def test_basic_len_and_indexing(self):
        data = b'HelloWorld'
        bs = ByteSlice(data, 2, 7)

        assert len(bs) == 5  # 'lloWo'
        assert bs[0] == ord('l')
        assert bs[1] == ord('l')
        assert bs[4] == ord('o')

    def test_negative_indexing(self):
        data = b'abcdef'
        bs = ByteSlice(data, 1, 5)  # 'bcde'

        assert bs[-1] == ord('e')
        assert bs[-2] == ord('d')

    def test_slice_of_slice(self):
        data = b'ABCDEFGHIJK'
        bs1 = ByteSlice(data, 2, 10)  # 'CDEFGHIJ'
        bs2 = bs1[3:7]  # 'FGHI'

        assert isinstance(bs2, ByteSlice)
        assert bytes(bs2) == b'FGHI'
        assert bs2._start == bs1._start + 3
        assert bs2._end == bs1._start + 7

    def test_iter(self):
        data = b'xyz'
        bs = ByteSlice(data, 0, 3)
        assert list(bs) == [ord('x'), ord('y'), ord('z')]

    def test_repr(self):
        data = b'HelloAmazingWorld!'
        bs = ByteSlice(data, 5, 15)
        rep = repr(bs)

        assert 'ByteSlice' in rep
        assert 'len=' in rep
        assert 'start=' in rep
        assert 'preview=' in rep

    def test_to_bytes_and_dunder_bytes(self):
        data = b'1234567890'
        bs = ByteSlice(data, 3, 7)
        assert bs.to_bytes() == b'4567'
        assert bytes(bs) == b'4567'

    def test_underlying_buffer_shared(self):
        """Усі вкладені ByteSlice повинні посилатися на той самий buffer."""
        data = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        bs1 = ByteSlice(data, 5, 20)
        bs2 = bs1[3:10]
        bs3 = bs2[2:5]

        assert id(bs1._buffer) == id(bs2._buffer) == id(bs3._buffer)

    def test_no_copy_memory_size_difference(self):
        """
        Копія bytes-слайсу повинна займати більше памʼяті,
        ніж ByteSlice, який лише зберігає метадані.
        """
        data = b'x' * 1_000_000  # 1MB buffer

        bs_copy = data[100:800]  # копія 100 байтів
        bs_view = ByteSlice(data, 100, 800)  # zero-copy

        size_copy = asizeof.asizeof(bs_copy)
        size_view = asizeof.asizeof(bs_view)

        assert size_copy > size_view

    def test_modifying_underlying_bytearray_affects_slice(self):
        """
        Zero-copy доказ: зміна bytearray має змінити і ByteSlice.
        """
        data = bytearray(b'HelloWorld')
        bs = ByteSlice(data, 0, 5)  # 'Hello'

        assert bytes(bs) == b'Hello'

        data[1] = ord('a')  # змінюємо data -> має змінитися slice

        assert bytes(bs) == b'Hallo'

    def test_no_intermediate_byte_copies_created(self):
        """
        Перевіряємо, що ByteSlice slicing не створює нових bytes-обʼєктів,
        лише легкі обʼєкти ByteSlice.
        """
        data = b'abcdef' * 100

        bs1 = ByteSlice(data, 10, 200)
        bs2 = bs1[50:120]
        bs3 = bs2[10:30]

        assert sys.getsizeof(bs1) < 200
        assert sys.getsizeof(bs2) < 200
        assert sys.getsizeof(bs3) < 200
