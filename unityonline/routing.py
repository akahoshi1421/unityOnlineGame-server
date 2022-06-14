from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/matchingroom/<slug:room_name>/', consumers.MatchingConsumer.as_asgi()),#1のみ
    path('ws/waitingroom/<slug:room_name>/', consumers.WaitingConsumer.as_asgi()),
    path('ws/fightingroom/<slug:room_name>/', consumers.FightingConsumer.as_asgi()),
]