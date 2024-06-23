from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.request import Request

from .serializers import GroupSerializer

# Create your views here.

@api_view()
def hello_world_view(request:Request) -> Response:
    return Response({"message": "Hello World!"})


# class GroupsListView(APIView):

#     def get(self, request: Request) -> Response:
#         groups = Group.objects.all()
#         # data = [group.name for group in groups]
#         serialized = GroupSerializer(groups, many=True)
#         return Response({"groups": serialized.data})

# class GroupsListView(ListModelMixin, GenericAPIView):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer

#     def get(self, requerst:Request) -> Response:
#         return self.list(requerst)

class GroupsListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
