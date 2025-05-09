from django.contrib import admin
from .models import Project, Evaluation

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title','average_score_display','rank_display')
    
    def average_score_display(self,obj):
        return obj.average_score()
    average_score_display.short_description = '평균 점수'
    
    def rank_display(self, obj):
        # 전체 프로젝트 평균 점수 리스트 +평균 점수 정렬 + tie-break(제목 오름차순)
        projects = list(Project.objects.all())
        scored = sorted(
            [(p, p.average_score() if isinstance(p.average_score(), (int, float)) else 0) for p in projects],
            key=lambda x: (-x[1], x[0].title)
        )

        # 현재 obj의 등수 계산
        for i, (p, _) in enumerate(scored, 1):
            if p.id == obj.id:
                if i == 1:
                    return f"★ {i}등"
                elif i == 2:
                    return f"★ {i}등"
                elif i == 3:
                    return f"★ {i}등"
                else:
                    return f"{i}등"
    
        return '-'
    rank_display.short_description = '등위'
    
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('project','user','score')
