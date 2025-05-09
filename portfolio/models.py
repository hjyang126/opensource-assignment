from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    score_total = models.IntegerField(default=0)  # ✅ 이름 변경: evaluation → score_total
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def average_score(self):
        avg = self.evaluations.aggregate(models.Avg('score'))['score__avg']
        return round(avg, 2) if avg else "평가 없음"

class Evaluation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='evaluations')
    user = models.CharField(max_length=100)
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f"{self.user}-{self.project.title}: {self.score}"
