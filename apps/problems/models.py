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

    statement = models.TextField(null=True, blank=True)
    
    time_limit = models.IntegerField(default=1000)
    memory_limit = models.IntegerField(default=64)
    difficulty = models.IntegerField(default=1)
    
    test_file = models.FileField(upload_to='problems/test/', null=True, blank=True)
    test_count = models.IntegerField(default=0)

    submission_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (@{self.author.username})"

class SampleTest(models.Model):

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="samples")

    input_data = models.TextField()
    output_data = models.TextField()

    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.problem.title} sample {self.id}"

class ProblemImage(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="problems/image/")
    original_name = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.problem.title} image"