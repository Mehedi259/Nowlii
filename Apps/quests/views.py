from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Quests, SubTasks
from .serializers import QuestsSerializers, SubTasksSerializers
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema


# ------------------------------------------------------------------------------
# QUESTS
# ------------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List all quests",
    operation_description="Get a list of all quests entries.",
    tags=['Quests']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create quest",
    operation_description="Create a new profile entry.",
    tags=['Quests']
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Get quest details",
    operation_description="Get details of a specific quest entry by ID.",
    tags=['Quests']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Update quest",
    operation_description="Update a specific quest entry by ID.",
    tags=['Quests']
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partially update quest",
    operation_description="Partially update a specific quest entry by ID.",
    tags=['Quests']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Delete quest",
    operation_description="Delete a specific quest entry by ID.",
    tags=['Quests']
))
class QuestsViewset(viewsets.ModelViewSet):
    queryset = Quests.objects.all()
    serializer_class = QuestsSerializers
    permission_classes = [IsAuthenticated]


# ------------------------------------------------------------------------------
# SUBTASKS
# ------------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List all subtasks",
    operation_description="Get a list of all subtasks entries.",
    tags=['SubTasks']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create subtask",
    operation_description="Create a new subtask entry.",
    tags=['SubTasks']
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Get subtask details",
    operation_description="Get details of a specific subtask entry by ID.",
    tags=['SubTasks']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Update subtask",
    operation_description="Update a specific subtask entry by ID.",
    tags=['SubTasks']
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partially update subtask",
    operation_description="Partially update a specific subtask entry by ID.",
    tags=['SubTasks']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Delete subtask",
    operation_description="Delete a specific subtask entry by ID.",
    tags=['SubTasks']
))
class SubTasksViewset(viewsets.ModelViewSet):
    queryset = SubTasks.objects.all()
    serializer_class = SubTasksSerializers
    permission_classes = [IsAuthenticated]