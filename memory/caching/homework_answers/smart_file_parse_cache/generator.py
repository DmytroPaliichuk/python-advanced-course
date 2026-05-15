"""
Допоміжний скрипт для домашнього завдання: генерація тестового JSON-файлу для задачі FileParseCache.

Призначення:
    Цей файл НЕ містить основну логіку домашнього завдання. Його роль - згенерувати тестовий JSON-файл, який потім буде
    використовуватися для перевірки та демонстрації роботи кешу.
    Змінювати код в рамках виконання основного домашнього завдання не потрібно;
    основне завдання - реалізувати кешування результатів парсингу файлу.

Що робить скрипт:
    - створює великий JSON-файл із вкладеною структурою;
    - генерує набір сервісів, конфігурацій і features;
    - записує результат у файл на диску.
"""

from __future__ import annotations

import json
import random

from pathlib import Path


class JsonConfigGenerator:
    """
    Генерує тестовий JSON-файл для задачі FileParseCache.
    """

    __slots__ = ('_services', '_features_per_service', '_seed')

    def __init__(
        self,
        services: int = 100,
        features_per_service: int = 200,
        seed: int = 42,
    ):
        self._services = services
        self._features_per_service = features_per_service
        self._seed = seed

    def generate(self, path: Path) -> None:
        random.seed(self._seed)

        data = {
            'version': 1,
            'environment': 'production',
            'services': {},
        }

        for service_idx in range(self._services):
            service_name = f'service_{service_idx}'

            service_config = {
                'enabled': random.choice([True, False]),
                'timeout_seconds': random.randint(1, 60),
                'retries': random.randint(0, 10),
                'thresholds': {
                    'warning': round(random.uniform(0.1, 0.8), 3),
                    'critical': round(random.uniform(0.8, 1.0), 3),
                },
                'features': {},
            }

            features = service_config['features']

            for feature_idx in range(self._features_per_service):
                feature_name = f'feature_{feature_idx}'

                features[feature_name] = {
                    'weight': round(random.uniform(0.0, 10.0), 4),
                    'enabled': random.choice([True, False]),
                    'tags': [f'tag_{random.randint(1, 20)}' for _ in range(random.randint(2, 6))],
                    'limits': {
                        'min': random.randint(0, 100),
                        'max': random.randint(100, 1000),
                    },
                }

            data['services'][service_name] = service_config

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
