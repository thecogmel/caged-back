from rest_framework import viewsets

from authentication.permissions import IsSuperUserPermission

from .models import Gathering
from .serializers import GatheringSerializer


class GatheringViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserPermission]
    queryset = Gathering.objects.all().order_by("name")
    serializer_class = GatheringSerializer
