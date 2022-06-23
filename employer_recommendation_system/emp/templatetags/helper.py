from django.contrib.auth.models import User
from django import template
from django.conf import settings
from emp.helper import has_fossee_role, has_ilw_role, has_spk_student_role
from moodle.models import *
from spoken.models import *
from emp.models import JobShortlist,NUM_OF_EMPS
from spoken.models import *
from events.models import Testimonial
RATING = {
    'ONLY_VISIBLE_TO_ADMIN_HR':0,
    'DISPLAY_ON_HOMEPAGE':1,
    'VISIBLE_TO_ALL_USERS':2
}
JOB_RATING=[(RATING['VISIBLE_TO_ALL_USERS'],'Visible to all users'),(RATING['ONLY_VISIBLE_TO_ADMIN_HR'],'Only visible to Admin/HR'),(RATING['DISPLAY_ON_HOMEPAGE'],'Display on homepage')]

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

@register.simple_tag
def application_count(job):
    return JobShortlist.objects.filter(job=job).count()

@register.simple_tag
def get_statedetails(stateid):
    return SpokenState.objects.get(id=stateid)

@register.simple_tag
def get_citydetails(cityid):
    return SpokenCity.objects.get(id=cityid)

@register.filter()
def format_char(value):
    s=''
    for val in value.split():
        if len(val)>1:
            s+=val[0].capitalize()+val[1:].lower()+' '
        else:
            s+=val[0].capitalize()+' '
    return s

# @register.filter()
# def display_foss(value):
#     foss = FossCategory.objects.get(id=int(value)).foss
#     return foss

@register.filter()
def display_gender(value):
    if value is not None:
        d = {'f':'Female','m':'Male','a':'No criteria'}
        return d[value]
    return ''

@register.filter()
def display_foss(value):
    if value:
    # if value is not None:
        foss_ids = list(map(int,value.split(',')))
        foss = [FossCategory.objects.get(id=x).foss for x in foss_ids]
        if foss:
            return ' , '.join(foss)
    return ''

@register.filter()
def display_states(value):
    # if value is not None:
    if value:
        state_ids = list(map(int,value.split(',')))
        # states = [SpokenState.objects.get(id=x).name for x in state_ids]
        states = [x.name for x in SpokenState.objects.filter(id__in=state_ids)]
        if states:
            return ' , '.join(states)
    return ''

@register.filter()
def display_cities(value):
    # if value is not None:
    if value:
        city_ids = list(map(int,value.split(',')))
        # cities = [SpokenCity.objects.get(id=x).name for x in city_ids]
        cities = [x.name for x in SpokenCity.objects.filter(id__in=city_ids)]
        if cities:
            return ' , '.join(cities)
    return ''

@register.filter()
def display_institute(value):
    if value:
    # if value is not None:
        insti_ids = list(map(int,value.split(',')))
        # type_institutes = [InstituteType.objects.get(id=x).name for x in insti_ids]
        type_institutes = [x.name for x in InstituteType.objects.filter(id__in=insti_ids)]
        if type_institutes:
            return ' , '.join(type_institutes)
    return ''

@register.filter()
def display_ac_status(value):
    ac_status = {1:'Active',3:'Inactive'}
    try:
        return ac_status[value]
    except:
        return ''

@register.filter()
def display_degrees(value):
    # if value is not None:
    if value:
        degree_ids = list(map(int,value.split(',')))
        # cities = [SpokenCity.objects.get(id=x).name for x in city_ids]
        degrees = [x.name for x in Degree.objects.filter(id__in=degree_ids)]
        if degrees:
            return ' , '.join(degrees)
    return ''

@register.filter()
def display_disciplines(value):
    # if value is not None:
    if value:
        discipline_ids = list(map(int,value.split(',')))
        # cities = [SpokenCity.objects.get(id=x).name for x in city_ids]
        disciplines = [x.name for x in Discipline.objects.filter(id__in=discipline_ids)]
        if disciplines:
            return ' , '.join(disciplines)
    return ''


@register.simple_tag
def get_url(value):
    if value =='GRADE_FILTER':
        return settings.GRADE_FILTER
    if value =='MASS_MAIL_PAGE':
        return settings.MASS_MAIL_PAGE
    return ''

@register.filter()
def format_status(value):
    d={0:'warning',1:'success'}
    return d[value]

@register.filter()
def status_value(value):
    d={0:'In process',1:'shortlisted'}
    return d[value]

@register.filter()
def get_student_fullname(value):
    try:
        user = SpokenUser.objects.get(id=value)
        return user.first_name + ' ' + user.last_name
    except Exception as e:
        return 'Error in fetching name'

@register.filter()
def get_institute_name(value):
    return AcademicCenter.objects.get(id=value).institution_name

@register.filter()
def get_num_emp(value):
    l,v = zip(*NUM_OF_EMPS)
    if value:
        return v[l.index(value)]
    return ''

@register.filter()
def get_rating(value):
    l,v = zip(*JOB_RATING)
    try:
        return v[l.index(value)]
    except:
        return ''
@register.filter()
def get_status(value):
    if value:
        return 'Active'
    return 'Inactive'

@register.filter()
def get_employees(value):
    l,v = zip(*NUM_OF_EMPS)
    try:
        return v[l.index(value)]
    except:
        return ''

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) 


@register.filter
def format_date(value,arg):
    if value is not None:
        start = value
        end = arg
        s = ''   
        if start.year!=end.year:
            s = str(start.day) + " "+start.strftime("%b") + " "+str(start.year)
            e = str(end.day) +" "+ end.strftime("%b")+" " + str(end.year)
        else:
            if start.month!=end.month:
                s = str(start.day) + " "+start.strftime("%b")+" - "+ str(end.day) + end.strftime("%b") + str(start.year)
            else:
                if start.day == end.day:
                    s = str(start.day) + " "+start.strftime("%b") + " "+str(start.year)
                else:
                    s = str(start.day) + " - "+ str(end.day) + " "+end.strftime("%b") + " "+ str(start.year)
                
        return s
    return ''


@register.filter()
def get_event_testimonials(eventid):
    return Testimonial.objects.filter(event_id=eventid,active=True)


@register.filter()
def get_value(dictionary,key):
    value = dictionary.get(key) 
    return value

@register.filter()
def is_student(student_id):
    try:
        user = User.objects.get(id=student_id.id)
        groups = [x.name for x in user.groups.all()]
        if has_spk_student_role(user.student) or has_ilw_role(user.student) or has_fossee_role(user.student):
            return True
        else:
            return False
    except Exception as e:
        return False

