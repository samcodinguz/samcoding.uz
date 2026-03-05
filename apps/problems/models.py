from django.db import models
from apps.accounts.models import CustomUser

class ProblemTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Problem(models.Model):

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(ProblemTag, blank=True)

    description = models.TextField(null=True, blank=True)
    input_txt = models.TextField(null=True, blank=True)
    output_txt = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    time_limit = models.IntegerField(default=1000)
    memory_limit = models.IntegerField(default=64)
    difficulty = models.IntegerField(default=1)

    sample_tests = models.IntegerField(default=0)
    test_file = models.FileField(upload_to='problems/test/', null=True, blank=True)

    submission_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (@{self.author.username})"