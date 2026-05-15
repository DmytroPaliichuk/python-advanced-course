from __future__ import annotations

from typing import Iterator


class ByteSlice:
    __slots__ = ('_buffer', '_start', '_end')

    def __init__(
        self,
        data: bytes | bytearray | memoryview,
        start: int = 0,
        end: int | None = None,
    ):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError('Data must be bytes-like')

        mv = data if isinstance(data, memoryview) else memoryview(data)

        if end is None:
            end = len(mv)

        if start < 0 or end < start or end > len(mv):
            raise ValueError('Invalid slice range')

        self._buffer = mv
        self._start = start
        self._end = end

    def __len__(self) -> int:
        return self._end - self._start

    def __getitem__(self, item: int | slice) -> int | ByteSlice:
        if isinstance(item, int):
            if item < 0:
                item += len(self)
            if not 0 <= item < len(self):
                raise IndexError('ByteSlice index out of range')
            return self._buffer[self._start + item]

        if isinstance(item, slice):
            start, stop, step = item.indices(len(self))
            if step != 1:
                raise ValueError('step slicing is not supported')
            return ByteSlice(self._buffer, self._start + start, self._start + stop)

        raise TypeError('Invalid index type')

    def __iter__(self) -> Iterator[int]:
        for i in range(self._start, self._end):
            yield self._buffer[i]

    def __bytes__(self) -> bytes:
        return bytes(self._buffer[self._start : self._end])

    def to_bytes(self) -> bytes:
        return bytes(self)

    def __repr__(self) -> str:
        length = len(self)
        preview_bytes = bytes(self._buffer[self._start : self._end][:20])
        preview = repr(preview_bytes)

        if length > 20:
            preview = preview[:-1] + '...'

        return f'ByteSlice(len={length}, start={self._start}, end={self._end}, preview={preview})'
