from rest_framework import serializers
from .models import Quests, SubTasks


# ------------------------------------------------------------------------------
# QUESTS
# ------------------------------------------------------------------------------
class QuestsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Quests
        exclude = ['user']


# ------------------------------------------------------------------------------
# SUBTASKS
# ------------------------------------------------------------------------------
class SubTasksSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubTasks
        fields = '__all__'