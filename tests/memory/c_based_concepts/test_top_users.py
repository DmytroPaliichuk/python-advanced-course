import os
import tempfile

from unittest import TestCase

from memory.c_based_concepts.homework.top_users import top_users


class TestTopUsers(TestCase):
    def setUp(self):
        """Створює тимчасову директорію для всіх тестових файлів."""
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Автоматично видаляє всі тимчасові файли після тесту."""
        self.tmpdir.cleanup()

    def write_temp_file(self, content: str) -> str:
        """Створює тимчасовий файл у директорії тесту та повертає шлях до нього."""
        path = os.path.join(self.tmpdir.name, 'data.csv')
        with open(path, 'w') as f:
            f.write(content)
        return path

    def test_basic_top_users(self):
        data = """\
2024-01-01,u1,click,10
2024-01-01,u2,click,5
2024-01-01,u1,click,7
2024-01-01,u3,click,1
"""
        path = self.write_temp_file(data)

        result = top_users(path, top_n=2)

        expected = [('u1', 17.0), ('u2', 5.0)]
        self.assertEqual(result, expected)

    def test_ignores_invalid_lines(self):
        data = """\
2024-01-01,u1,click,10
BROKEN_LINE
2024-01-01,u1,click,5
2024-01-01,u2,click,3
BAD,LINE,TOO
"""
        path = self.write_temp_file(data)

        result = top_users(path, top_n=2)

        expected = [('u1', 15.0), ('u2', 3.0)]
        self.assertEqual(result, expected)

    def test_negative_values(self):
        data = """\
2024-01-01,u1,click,10
2024-01-01,u1,click,-4
2024-01-01,u2,click,2
"""
        path = self.write_temp_file(data)

        result = top_users(path, top_n=2)

        expected = [('u1', 6.0), ('u2', 2.0)]
        self.assertEqual(result, expected)

    def test_top_n_greater_than_user_count(self):
        data = """\
2024-01-01,u1,click,5
2024-01-01,u2,click,3
"""
        path = self.write_temp_file(data)

        result = top_users(path, top_n=10)

        expected = [('u1', 5.0), ('u2', 3.0)]
        self.assertEqual(result, expected)

    def test_empty_file(self):
        path = self.write_temp_file('')

        result = top_users(path, top_n=5)

        self.assertEqual(result, [])
