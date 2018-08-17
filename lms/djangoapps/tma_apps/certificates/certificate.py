from courseware.courses import get_course_by_id
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from edxmako.shortcuts import render_to_response
import logging
import json
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
import hashlib
from django.conf import settings
log = logging.getLogger(__name__)

class certificate():

    def __init__(self,course_key,user):
        self.course_key = course_key
        self.user = user
        self.course = None
        self.courseGrade = None
        self.metadata = None

    def get_course(self):
        if self.course_key is not None:
            self.course = get_course_by_id(self.course_key)

    def get_course_grade(self):
        if self.course is not None and self.user is not None:
            self.courseGrade = CourseGradeFactory().read(self.user, self.course)

    def get_metadata(self):
        if self.course is not None:
            self.metadata = self.course.__dict__

    def check_certificate(self):
        self.get_course()
        self.get_course_grade()
        self.get_metadata()

        log.info(self.courseGrade.summary)

        passed = False
        total = 0
        add = 0
        finished = 0
        values = []
        from_vue = []
        grade = self.courseGrade.percent
        _is_certified = False
        if not self.metadata.get('custom_cutoff'):
            passed = self.courseGrade.passed
            _is_certified = True
        else:
            user_breakdown = self.courseGrade.grade_value['grade_breakdown']

            for row in self.metadata.get('sub_sections'):
                _type = row.get('type')
                required = row.get('required')
                if required:

                    total = total + 1
                    coef = row.get('coef')
                    value = float((float(row.get('real')) / 100) * coef)
                    values.append(value)
                    log.info('certificate values required {}'.format(value))

                    for n in user_breakdown.keys():
                        if n == _type:
                            add = add + 1
                            from_vue.append(user_breakdown.get(n).get('percent'))
                            if user_breakdown.get(n).get('percent') > value:
                                finished = finished + 1

            if add == total:
                _is_certified = True
                if finished == total and self.courseGrade.passed:
                    passed = True

        context = {
            "passed":passed,
            "finished":finished,
            "regular":_is_certified,
            "add":add,
            "total":total,
            "grade":grade,
            "values":values,
            "from_vue":from_vue
        }

        return context

    def view(self,request):
        grades = self.check_certificate()
	try:
            first_name = json.loads(request.user.profile.custom_field).get('first_name')
	except:
	    first_name = ""
	try:
            last_name = json.loads(request.user.profile.custom_field).get('last_name')
        except:
	    last_name = ""
        name = last_name+" "+first_name
        if self.metadata.get('bg'):
            bg =self.metadata.get('bg')
        else :
            bg =settings.LMS_ROOT_URL+"/media/certificates/certificate_bg.jpg"
        context = {
            "request":request,
            "grades":grades,
            "course_name":self.course.display_name_with_default,
            "signature":self.metadata.get('signature'),
            "pdf":self.metadata.get('pdf'),
            "bg":bg,
            "first_name":first_name,
            "last_name":last_name,
            "hash":hashlib.sha256(name.strip()+"AyuNUNag62wFrApuqErafE"+str(grades.get('grade')*100)).hexdigest()[0:9]
        }

        return render_to_response('tma_apps/certificate.html',context)


    def ensure_certificate(self):

        context = self.check_certificate()

        return JsonResponse(context)
