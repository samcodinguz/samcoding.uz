from django.contrib import admin
from apps.problems.models import ProblemTag, Problem, ProblemImage, SampleTest, Language

admin.site.register(ProblemTag)
admin.site.register(Problem)
admin.site.register(ProblemImage)
admin.site.register(SampleTest)
admin.site.register(Language)