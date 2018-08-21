from lms.djangoapps.tma_apps.certificates.certificate import certificate

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from opaque_keys.edx.locations import SlashSeparatedCourseKey

@login_required
@require_GET
def ensure(request,course_id):

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    return certificate(course_key,request.user).ensure_certificate()

@login_required
@require_GET
def render(request,course_id):

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    return certificate(course_key,request.user).view(request)

@login_required
@require_GET
def generic(request,course_id):

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    return certificate(course_key,request.user).generic(request)
