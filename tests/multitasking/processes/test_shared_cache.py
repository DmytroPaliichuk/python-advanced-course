from multiprocessing import shared_memory

import numpy as np
import pytest

from pytest_mock import MockerFixture

from multitasking.processes.homework.shared_cache import (
    CacheSlotState,
    SharedCacheStorage,
    SharedPrimeCache,
)


class TestSharedCacheStorage:
    def test_descriptor_and_shapes(self):
        storage = SharedCacheStorage(capacity=8)
        keys_name, values_name, states_name, cap = storage.descriptor()

        assert cap == 8
        assert isinstance(keys_name, str)
        assert isinstance(values_name, str)
        assert isinstance(states_name, str)

        shm_k = shared_memory.SharedMemory(name=keys_name)
        arr_k = np.ndarray((cap,), dtype=np.int64, buffer=shm_k.buf)
        assert arr_k.shape == (8,)
        assert np.all(arr_k == -1)

        shm_k.close()
        storage.close()

    def test_close_unlinks(self):
        storage = SharedCacheStorage(capacity=4)
        keys_name, _, _, _ = storage.descriptor()
        storage.close()

        # Після unlink відкриття має падати
        with pytest.raises(FileNotFoundError):
            shared_memory.SharedMemory(name=keys_name)


class TestSharedPrimeCache:
    def test_find_ready_and_in_progress(self, cache: SharedPrimeCache):
        # ручне заповнення
        cache._keys[2] = 100
        cache._states[2] = CacheSlotState.READY

        cache._keys[5] = 200
        cache._states[5] = CacheSlotState.IN_PROGRESS

        assert cache._find_ready(100) == 2
        assert cache._find_ready(200) == -1

        assert cache._find_in_progress(200) == 5
        assert cache._find_in_progress(999) == -1

    def test_reserve_slot(self, cache: SharedPrimeCache):
        # спочатку всі EMPTY
        slot = cache._reserve_slot(123)
        assert slot == 0
        assert cache._keys[0] == 123
        assert cache._states[0] == CacheSlotState.IN_PROGRESS

        # друге резервування
        slot2 = cache._reserve_slot(456)
        assert slot2 == 1
        assert cache._keys[1] == 456
        assert cache._states[1] == CacheSlotState.IN_PROGRESS

    def test_get_or_compute_basic(self, cache: SharedPrimeCache, mocker: MockerFixture):
        # Патчимо count_primes_up_to, щоб не рахувати реально
        mocker.patch(
            'multitasking.processes.homework_answers.shared_cache.count_primes_up_to',
            return_value=777,
        )

        # Перше обчислення -> MISS -> CALC -> READY
        res = cache.get_or_compute(50)
        assert res == 777

        # Перевіримо, що збережено
        slot = cache._find_ready(50)
        assert slot != -1
        assert cache._values[slot] == 777

        # Другий виклик -> HIT
        res2 = cache.get_or_compute(50)
        assert res2 == 777

    def test_wait_logic(self, cache: SharedPrimeCache, mocker: MockerFixture):
        """
        Імітуємо ситуацію:
        - інший процес вже рахує n (IN_PROGRESS)
        - поточний процес має WAIT всередині циклу
        """
        cache._keys[3] = 999
        cache._states[3] = CacheSlotState.IN_PROGRESS

        # count_primes_up_to викликатись не повинен
        spy = mocker.spy(cache, '_reserve_slot')

        # Патчимо sleep, щоб не чекати реально
        mocker.patch('time.sleep')

        # Очікуємо, що get_or_compute не зможе резервувати новий слот
        # і вийде ДО обчислень, коли інший 'процес' закінчить.
        # Ми імітуємо завершення IN_PROGRESS:
        def release_progress(*args, **kwargs):
            cache._states[3] = CacheSlotState.READY
            cache._values[3] = 123
            return 0.01

        mocker.patch(
            'multitasking.processes.homework_answers.shared_cache.time.sleep',
            side_effect=release_progress,
        )

        result = cache.get_or_compute(999)
        assert result == 123

        # Ніхто не резервував слот
        spy.assert_not_called()

    def test_snapshot(self, cache: SharedPrimeCache):
        cache._keys[0] = 10
        cache._values[0] = 5
        cache._states[0] = CacheSlotState.READY

        snap = list(cache.snapshot())
        assert snap[0] == (10, 5, CacheSlotState.READY)
        assert len(snap) == cache.capacity
