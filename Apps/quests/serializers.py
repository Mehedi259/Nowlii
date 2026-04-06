from rest_framework import serializers
from .models import Quests, SubTasks


# ------------------------------------------------------------------------------
# SUBTASKS
# ------------------------------------------------------------------------------
class SubTasksSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubTasks
        exclude = ['task']


# ------------------------------------------------------------------------------
# QUESTS
# ------------------------------------------------------------------------------
class QuestsSerializers(serializers.ModelSerializer):
    subtasks = SubTasksSerializers(many=True, required=False)
    
    class Meta:
        model = Quests
        exclude = ['user']

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        quest = Quests.objects.create(**validated_data)
        for subtask_data in subtasks_data:
            SubTasks.objects.create(task=quest, **subtask_data)
        return quest

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', None)
        instance = super().update(instance, validated_data)
        if subtasks_data is not None:
            instance.subtasks.all().delete()
            for subtask_data in subtasks_data:
                SubTasks.objects.create(task=instance, **subtask_data)
        return instance