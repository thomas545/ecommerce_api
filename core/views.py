from django.shortcuts import render
from django.db import transaction
# Create your views here.

# class Get_Host(APIView):
#     def post(self, request):
#         host = request.META.get('HTTP_USER_AGENT')
#         return Response({"Host": host})