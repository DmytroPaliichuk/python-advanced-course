"""
Оптимізувати клас EventAggregator для мінімізації копій памʼяті.

Завдання:
    Поточна реалізація EventAggregator створює багато непотрібних копій. Потрібно
    переписати логіку так, щоб обробка подій була максимально ефективною за памʼяттю.

Вимоги:
    - Назва класу EventAggregator та метод __init__ мають залишитися незмінними;
    - Метод run() має бути присутнім; його вміст можна змінювати за потреби;
    - Більше обмежень по модифікаціям у класі немає;
    - Мета - мінімізувати алокації, копії в памʼяті;
    - Фінальний результат має формувати payload по користувачах у тому ж форматі.

Актуальність:
    Робота з великими JSON-потоками та S3 - типова задача в системах обробки подій.
    Надмірні копії призводять до високого споживання памʼяті та CPU.
    Оптимізація дозволяє побудувати ефективний pipeline і продемонструвати
    практичне розуміння методів мінімізації алокацій та роботи зі структурами даних у Python.
"""

import copy
import json

from datetime import datetime

from memory.fragments_and_copies.homework import fake_boto3


class EventAggregator:  # <- Залиш назву незмінною
    def __init__(self, bucket: str, prefix: str):  # <- Init метод має залишитися таким
        self.bucket = bucket
        self.prefix = prefix

        self.s3 = fake_boto3.client('s3')

    def load_all_files(self) -> list[dict]:
        objects = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix,
        )['Contents']

        all_events = []
        for obj in objects:
            raw = self.s3.get_object(
                Bucket=self.bucket,
                Key=obj['Key'],
            )['Body'].read()

            events = json.loads(raw)
            all_events.extend(events)

        return all_events

    @staticmethod
    def normalize_events(events: list[dict]) -> list[dict]:
        normalized = copy.deepcopy(events)
        result = []

        for event in normalized:
            event_copy = event.copy()
            event_copy['timestamp'] = datetime.fromisoformat(event_copy['timestamp']).timestamp()

            result.append(
                {
                    'user_id': event_copy['user_id'],
                    'event': event_copy['event'],
                    'value': event_copy.get('value'),
                    'timestamp': event_copy['timestamp'],
                    'extra': {},
                }
            )

        return result

    @staticmethod
    def merge_by_user(events: list[dict]) -> dict:
        merged = {}

        for event in events:
            user = event['user_id']

            if user not in merged:
                merged[user] = {'events': [], 'meta': {}}

            merged[user]['events'].append(event.copy())

        return merged

    @staticmethod
    def build_payload(merged: dict) -> list[dict]:
        payload = []

        for user, data in merged.items():
            events_copy = [copy.deepcopy(e) for e in data['events']]

            payload.append({'user': user, 'count': len(events_copy), 'events': events_copy})

        return payload

    def run(self) -> list[dict]:  # <- метод run має бути наявним у класі, вміст можна змінювати за потреби
        events = self.load_all_files()
        normalized = self.normalize_events(events)
        merged = self.merge_by_user(normalized)
        payload = self.build_payload(merged)

        return payload
