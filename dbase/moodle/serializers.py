from rest_framework import serializers
from .models import MdlQuizGrades
# from .models import Todo

# class TodoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Todo
#         fields = ('id', 'title', 'description', 'completed')

class MdlQuizGradesSerializer(serializers.ModelSerializer):
	class Meta:
		model = MdlQuizGrades
		fields = '__all__'