from django import template
from django.conf import settings
from moodle.models import *


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group_list = []
    for item in user.groups.all():
        group_list.append(item.name)
    return True if group_name in group_list else False

@register.filter
def get_grade_mdluser(Dict, ta):
    return Dict[ta.mdluser_id][ta.mdlquiz_id][0]

@register.filter
def get_grade_mdluser_first_name(id):
    try:
        return MdlUser.objects.using('moodle').get(id=id).firstname
    except MdlUser.DoesNotExist:
        return None

@register.filter
def get_grade_mdluser_last_name(id):
    try:
        return MdlUser.objects.using('moodle').get(id=id).lastname
    except MdlUser.DoesNotExist:
        return None

@register.filter
def get_grade_mdluser_email(id):
    try:
        return MdlUser.objects.using('moodle').get(id=id).email
    except MdlUser.DoesNotExist:
        return None

