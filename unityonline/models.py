from statistics import mode
from django.db import models
import uuid

# Create your models here.
class MatchingQueue(models.Model):
    waiting_users = models.TextField()


class FightingRomm(models.Model):
    id = models.UUIDField(primary_key=True)
    two_players = models.TextField()