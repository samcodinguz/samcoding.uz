from django.db import models
from apps.accounts.models import CustomUser
from apps.problems.models import Problem, Language

class Submission(models.Model):
    # 1. Foydalanuvchi va masala
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True, blank=True)

    # 2. Til python, c++, java
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    # 3. Kod ...
    code = models.TextField(null=True, blank=True)

    # 4. Natija ac, wa, tl, ml, re, ce
    status = models.CharField(max_length=50, default="Pending")

    # 4.1 Qo'shimcha ma'lumotlar
    time_used = models.IntegerField(default=0)
    memory_used = models.IntegerField(default=0)

    # 5. Sana
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.problem.title} [{self.language}]"