from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestsViewset


router = DefaultRouter()
router.register(r'quests', QuestsViewset)

urlpatterns = [
    path('', include(router.urls)),
]