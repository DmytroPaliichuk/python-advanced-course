import json

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Iterator, TypedDict

from memory.fragments_and_copies.homework_answers import fake_boto3


@dataclass(slots=True)
class NormalizedEvent:
    user_id: str
    event: str
    value: Any
    timestamp: float
    extra: dict


class UserEventsGroup(TypedDict):
    events: list[NormalizedEvent]


MergedEvents = dict[str, UserEventsGroup]


class EventAggregator:
    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix

        self.s3 = fake_boto3.client('s3')

    def iter_raw_events(self) -> Iterator[dict]:
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix,
        )
        objects = response.get('Contents', [])

        for obj in objects:
            body = self.s3.get_object(
                Bucket=self.bucket,
                Key=obj['Key'],
            )['Body']

            raw = body.read()
            events_in_file = json.loads(raw)

            for event in events_in_file:
                yield event

    def iter_normalized_events(self) -> Iterator[NormalizedEvent]:
        for event in self.iter_raw_events():
            normalized_event = NormalizedEvent(
                user_id=event['user_id'],
                event=event['event'],
                value=event.get('value'),
                timestamp=datetime.fromisoformat(event['timestamp']).timestamp(),
                extra=event.get('metadata') or {},
            )
            yield normalized_event

    @staticmethod
    def merge_by_user(events: Iterable[NormalizedEvent]) -> MergedEvents:
        merged: defaultdict[str, UserEventsGroup] = defaultdict(lambda: {'events': []})
        for event in events:
            merged[event.user_id]['events'].append(event)

        return dict(merged)

    @staticmethod
    def build_payload(merged: MergedEvents) -> Iterator[dict[str, Any]]:
        for user, user_events in merged.items():
            yield {
                'user': user,
                'count': len(user_events['events']),
                'events': user_events['events'],
            }

    def run(self) -> Iterable[dict]:
        normalized_events = self.iter_normalized_events()
        merged = self.merge_by_user(normalized_events)
        payload = self.build_payload(merged)

        return payload
