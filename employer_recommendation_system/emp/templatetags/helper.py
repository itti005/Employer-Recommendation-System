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
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    #Return encoded URL parameters that are the same as the current
    #request's parameters, only with the specified GET parameters added or changed.
    #It also removes any empty parameters to keep things neat,
    #so you can remove a parm by setting it to ``""``.
    #For example, if you're on the page ``/things/?with_frosting=true&page=5``, then
    #<a href="/things/?{% param_replace page=3 %}">Page 3</a> would expand to
    #<a href="/things/?with_frosting=true&page=3">Page 3</a>
    #Based on
    #https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@property
def image_url(self):
    if self.logo and hasattr(self.logos, 'url'):
        return self.logo.url

@register.filter()
def to_int(value):
    return int(value)

@register.simple_tag(takes_context=True)
def job_accepted(value, args):
    return True
