from django.core.mail import send_mail
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from smtplib import SMTPException, SMTPServerDisconnected
from django.core.mail import BadHeaderError

def send_mail_shortlist(subject,message,emails,job):
	subject = subject
	message = message
	from_host = settings.EMAIL_HOST_USER
	students_email = emails
	fail_silently = False
	job_id = job

	sent = 0
	errors = 0
	count = 0

	now = datetime.now()
	
	log_file_name = 'log_email_job_'+str(job_id)+'_'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+".csv"
	log_file_name=os.path.join(settings.EMAIL_LOG_FILE,log_file_name)
	log_file=open(log_file_name, "w+")
	for email in students_email:
		print(email)
		mail = EmailMultiAlternatives(subject,message,from_host,students_email,headers = {"Content-type" : "text/html"})
		try:
			validate_email(email)
			mail.attach_alternative(message, "text/html")
			mail.send()
			sent += 1
			if sent%100 == 0:
				time.sleep(10)
			log_file.write(email+','+str(1)+'\n')
		except ValidationError as mail_error:
			log_file.write(email+','+str(0)+','+str(mail_error)+'\n')
			errors+=1
		except SMTPException as send_error:
			log_file.write(email+','+str(0)+','+str('SMTP mail send error.')+'\n')
			errors+=1
		except BadHeaderError as header_error:
			log_file.write(email+','+str(0)+','+str(header_error)+'\n')
			errors+=1
		except ConnectionRefusedError as refused:
			log_file.write(email+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
			errors+=1
		except SMTPServerDisconnected as disconnect:
			log_file.write(email+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
			errors+=1
	print("Total: "+ str(sent+errors)+"\n"+ "Sent: " +str(sent)+"\n"+"Errors: "+ str(errors))
	log_file.close()
	return len(students_email), sent, errors
