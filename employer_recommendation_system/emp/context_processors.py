from django.conf import settings
from .models import Student
from .views import getFieldsInfo
import re
def student_context_processor(request):
    data = {}
    empty_fields = ''
    pattern = r"/\d+/profile"
    match = re.match(pattern, request.path)
    if match:
        ctx_profile_completed = True
    else:
        try:
            student = Student.objects.get(user=request.user)
            
            complete,empty_fields = getFieldsInfo(student)
            ctx_profile_completed = False if empty_fields else True
            empty_fields = ', '.join(empty_fields)
            data['ctx_empty_fields'] = empty_fields
        except Exception as e:
            ctx_profile_completed = True
    data['ctx_profile_completed'] = ctx_profile_completed
    return data
