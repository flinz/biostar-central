from django.conf import settings

from celery import task
from django.core.mail import send_mail
from django.contrib.sites.models import Site

# import all constants
from main.server.const import *

@task
def demo_add(x, y):
    return x + y

@task
def send_test_email():
    subject = "test email"
    sender  = "istvan.albert@gmail.com"
    recipient = "iua1@psu.edu"
    body = "this is a test email"

    print "sending test email"

    #send_mail(subject, body, sender, [recipient], fail_silently=False)

@task
def send_email_note(sender, target, content, type=NOTE_USER, date=None, url=''):
    """
    Sends an email notification for a note. 
    """

    subject = "NeuroStars: Activity in a bookmarked question"
    sender  = "seeholzer@gmail.com"
    recipient = "seeholzer@gmail.com"
    body = content + '\n\n' + url

    print "sending email notice to %s: \n %s \n %s" % (target.email, subject, body)
    send_mail(subject=subject, from_email=settings.DEFAULT_FROM_EMAIL, message=content, recipient_list=[recipient], fail_silently=False)
	#send_mail(subject, body, sender, [recipient], fail_silently=False)

if __name__ == '__main__':
    send_test_email()
