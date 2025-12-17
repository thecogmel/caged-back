from rest_framework import serializers

from .models import Gathering


class GatheringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gathering
        fields = [
            "id",
            "name",
            "date",
            "location",
            "description",
        ]
