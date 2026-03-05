from django.contrib import admin
from apps.problems.models import ProblemTag, Problem

admin.site.register(ProblemTag)
admin.site.register(Problem)