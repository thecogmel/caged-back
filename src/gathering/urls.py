from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GatheringViewSet

router = DefaultRouter()

router.register("gatherings", GatheringViewSet, basename="gatherings")

urlpatterns = [
    path("", include(router.urls)),
]
