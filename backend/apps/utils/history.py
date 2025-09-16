from rest_framework import serializers
from django.forms.models import model_to_dict


class HistoryRecordField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        event_list = []
        diff_list = {}

        event_old = None
        for event in data.all():
            diff = None
            if event_old is not None:
                delta = event_old.diff_against(event)
                diff = {}
                for change in delta.changes:
                    diff[change.field] = change.new
                    if (change.new):
                        obj = model_to_dict(event)
                        diff['id'] = obj['id']

            else:
                initial_event = model_to_dict(event)

                del initial_event['history_user']
                del initial_event['history_date']
                del initial_event['history_change_reason']
                del initial_event['history_type']
                del initial_event['history_id']
                diff = initial_event

            diff_list[event.history_id] = diff
            event_old = event

        model = data.all().model.__name__.replace('Historical', '')
        historic_queryset = data.values()
        for event in historic_queryset:
            obj = {
                'model': model,
                'date': event['history_date'],
                'change_reason': event['history_change_reason'],
                'type': event['history_type'],
                'user': event['history_user_id'],
                'diff': None
            }

            if diff_list[event['history_id']] is not None:
                obj['diff'] = diff_list[event['history_id']]

            event_list.append(obj)

        return super().to_representation(event_list)
