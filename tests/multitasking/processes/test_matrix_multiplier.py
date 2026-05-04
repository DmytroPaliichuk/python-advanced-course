import pytest

from multitasking.processes.homework.matrix_multiplier import (
    MatrixGenerator,
    MatrixMultiplier,
)


class TestMatrixMultiplier:
    def test_sequential_basic(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        multiplier = MatrixMultiplier(A, B)

        result = multiplier.multiply_sequentially()
        expected = [
            [19, 22],
            [43, 50],
        ]

        assert result == expected

    def test_parallel_basic(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        multiplier = MatrixMultiplier(A, B)

        seq = multiplier.multiply_sequentially()
        par = multiplier.multiply_in_parallel()

        assert par == seq

    def test_random_small_correctness(self):
        A = MatrixGenerator.random_matrix(5, 4)
        B = MatrixGenerator.random_matrix(4, 6)
        multiplier = MatrixMultiplier(A, B)

        seq = multiplier.multiply_sequentially()
        par = multiplier.multiply_in_parallel()

        assert seq == par

    def test_invalid_dimensions(self):
        A = [[1, 2, 3]]
        B = [[1, 2]]  # неправильна форма

        with pytest.raises(ValueError):
            MatrixMultiplier(A, B)

    def test_parallel_and_sequential_match_for_various_sizes(self):
        sizes = [(2, 2, 2), (5, 5, 5), (10, 3, 6)]
        for n, m, p in sizes:
            A = MatrixGenerator.random_matrix(n, m)
            B = MatrixGenerator.random_matrix(m, p)
            multiplier = MatrixMultiplier(A, B)

            seq = multiplier.multiply_sequentially()
            par = multiplier.multiply_in_parallel()

            assert seq == par

    def test_parallel_handles_large_input(self):
        A = MatrixGenerator.random_matrix(50, 40)
        B = MatrixGenerator.random_matrix(40, 60)
        multiplier = MatrixMultiplier(A, B)

        seq = multiplier.multiply_sequentially()
        par = multiplier.multiply_in_parallel()

        assert seq == par

    def test_output_dimension(self):
        A = MatrixGenerator.random_matrix(7, 9)
        B = MatrixGenerator.random_matrix(9, 4)
        multiplier = MatrixMultiplier(A, B)

        result = multiplier.multiply_sequentially()

        assert len(result) == 7
        assert len(result[0]) == 4

    def test_parallel_output_dimension(self):
        A = MatrixGenerator.random_matrix(7, 9)
        B = MatrixGenerator.random_matrix(9, 4)
        multiplier = MatrixMultiplier(A, B)

        result = multiplier.multiply_in_parallel()

        assert len(result) == 7
        assert len(result[0]) == 4
