from django.contrib.auth.models import User
from emp.models import Student
from spoken.models import SpokenStudent
from spoken.models import SpokenUser 
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.update_table()

# iterate over auth_user table
    def update_table(self):
        count = 0
        student_exist = 0
        student_created = 0
        users_student = User.objects.filter(groups__in=[2])
        f = open("static/update_student_table.txt", "a")
        for user in users_student:
            try:
                student = Student.objects.get(user_id=user)
                student_exist+=1
                f.write(f"1 - {student}\n")
            except Student.DoesNotExist:
                f.write(f"0 - {user}\n")
                self.stdout.write(self.style.ERROR('************* error "%s"' % user))
                user_email = user.email
                f.write(f"*********** user_email - {user_email}")
                try:
                    spk_user = SpokenUser.objects.get(email=user_email)
                    f.write("*********** got by email")
                    f.write(f"*********** spk_user - {spk_user}")
                except:
                    spk_user = SpokenUser.objects.get(username=user_email)
                    f.write("*********** got by username")
                    f.write(f"*********** spk_user - {spk_user}")
                try:
                    spk_student = SpokenStudent.objects.get(user_id=spk_user)
                    f.write(f"*********** spk_student - {spk_student}")
                except:
                    f.write(f"failed to fetch student for {spk_user} ")
                s=Student.objects.create(user_id=user.id, spk_student_id=spk_student.id,spk_usr_id=spk_user.id,gender=spk_student.gender)
                student_created+=1
                f.write(f"created - {s}\n")
        f.write(f"\nstudent_exist - {student_exist}\ncreated - {student_created}\n")
        f.close()
            
    
# for each user; 
# if user is student;
# check if student table has entry:
# if not :
#     create entry in student table:
#     user_email = user.email
#     get spk_user using email
#     get spk_student from above spk_user;
#     id : auto
#     user_id : emp user id
#     spk_user_id : ?
#     spk_student_id : ?
    # spk_gender : ?

