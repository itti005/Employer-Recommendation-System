from django.shortcuts import render
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
# from .serializers import TodoSerializer
from .models import MdlQuizGrades
from .serializers import MdlQuizGradesSerializer
from django.http import  JsonResponse
from rest_framework import status,generics

# Create your views here.

# class TodoView(viewsets.ModelViewSet):
#     serializer_class = TodoSerializer
#     queryset = Todo.objects.all()

@csrf_exempt
def get_score(request):
	# data = MdlQuizGrades.objects.using('moodle').all()
	data = MdlQuizGrades.objects.using('moodle').get(pk=2)
	if request.method == 'GET':
		serializer = MdlQuizGradesSerializer(data)
		return JsonResponse(serializer.data, safe=False)

class MdlQuizGradesList(generics.ListAPIView):
	serializer_class  =  MdlQuizGradesSerializer
	def get_queryset(self):
		grades = MdlQuizGrades.objects.using('moodle').filter(userid = 1399)
		return grades
		