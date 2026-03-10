from rest_framework import serializers
from .models import Quests, SubTasks


# ------------------------------------------------------------------------------
# QUESTS
# ------------------------------------------------------------------------------
class QuestsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Quests
        fields = '__all__'


# ------------------------------------------------------------------------------
# SUBTASKS
# ------------------------------------------------------------------------------
class SubTasksSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubTasks
        fields = '__all__'