from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Evaluation
from .forms import ProjectForm, EvaluationForm
from django.db.models import Avg


# 메인 홈
def home(request):
    popular_projects = Project.objects.order_by('-id')[:5]
    latest_projects = Project.objects.order_by('-id')[:5]
    all_projects = Project.objects.order_by('-id')  # 전체 포폴 추가

    return render(request, 'home.html', {
        'popular_projects': popular_projects,
        'latest_projects': latest_projects,
        'all_projects': all_projects
    })


# 전체 프로젝트 리스트
def project_list(request):
    projects = Project.objects.all()

    # 평균 점수 계산 (최신 평가만 반영)
    for project in projects:
        evaluations = Evaluation.objects.filter(project=project)
        unique_users = {}
        for eval in evaluations:
            unique_users[eval.user] = eval.score  # 마지막 평가만 반영됨
        if unique_users:
            project.average_score = sum(unique_users.values()) / len(unique_users)
        else:
            project.average_score = None

    # 등위 계산
    sorted_projects = sorted(projects, key=lambda p: p.average_score or 0, reverse=True)
    for idx, project in enumerate(sorted_projects, start=1):
        project.rank = idx

    return render(request, 'project_list.html', {'projects': sorted_projects})


# 프로젝트 상세 보기 + 평가 처리
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    author = project.author
    other_projects = Project.objects.filter(author=author).exclude(pk=pk)

    # 평균 점수 계산
    evaluations = Evaluation.objects.filter(project=project)
    unique_users = {}
    for eval in evaluations:
        unique_users[eval.user] = eval.score
    if unique_users:
        project.average_score = round(sum(unique_users.values()) / len(unique_users), 2)
    else:
        project.average_score = None

    # 등위 계산용 (전체 프로젝트 기준)
    all_projects = Project.objects.all()
    score_dict = {}
    for p in all_projects:
        user_scores = {}
        for ev in Evaluation.objects.filter(project=p):
            user_scores[ev.user] = ev.score
        if user_scores:
            score_dict[p.pk] = sum(user_scores.values()) / len(user_scores)

    sorted_ids = sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    rank = next((idx + 1 for idx, (proj_id, _) in enumerate(sorted_ids) if proj_id == project.pk), None)
    project.rank = rank

    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            username = request.user.username
            score = form.cleaned_data['score']

            existing = Evaluation.objects.filter(project=project, user=username).first()
            if existing:
                existing.score = score
                existing.save()
            else:
                evaluation = form.save(commit=False)
                evaluation.project = project
                evaluation.user = username
                evaluation.save()

            return redirect('project_detail', pk=pk)
    else:
        form = EvaluationForm()

    return render(request, 'project_detail.html', {
        'project': project,
        'form': form,
        'author': author,
        'other_projects': other_projects
    })


# 프로젝트 등록
@login_required
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.save()
            return redirect('mypage')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form, 'edit': False})


# 프로젝트 수정 (자기 글만 가능)
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.author != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('mypage')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_form.html', {'form': form, 'edit': True})


# 프로젝트 삭제
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # 권한 체크
    if project.author != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")

    # POST 요청만 삭제 처리
    if request.method == 'POST':
        project.delete()
        return redirect('mypage')

    # GET 요청이면 아무 일 안 하고 마이페이지로 돌려보냄
    return redirect('mypage')


# 회원가입
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# 마이페이지
@login_required
def mypage(request):
    my_projects = Project.objects.filter(author=request.user)

    # 평균 및 등위 계산 (본인 글에 대해서만)
    for project in my_projects:
        evaluations = Evaluation.objects.filter(project=project)
        unique_users = {}
        for eval in evaluations:
            unique_users[eval.user] = eval.score
        if unique_users:
            project.average_score = sum(unique_users.values()) / len(unique_users)
        else:
            project.average_score = None

    sorted_projects = sorted(my_projects, key=lambda p: p.average_score or 0, reverse=True)
    for idx, project in enumerate(sorted_projects, start=1):
        project.rank = idx

    return render(request, 'user_page.html', {
        'owner': request.user,
        'projects': sorted_projects,
        'is_mypage': True
    })


# 다른 사람 유저 페이지
def user_page(request, username):
    user = get_object_or_404(User, username=username)
    projects = Project.objects.filter(author=user)

    for project in projects:
        evaluations = Evaluation.objects.filter(project=project)
        unique_users = {}
        for eval in evaluations:
            unique_users[eval.user] = eval.score
        if unique_users:
            project.average_score = sum(unique_users.values()) / len(unique_users)
        else:
            project.average_score = None

    sorted_projects = sorted(projects, key=lambda p: p.average_score or 0, reverse=True)
    for idx, project in enumerate(sorted_projects, start=1):
        project.rank = idx

    return render(request, 'user_page.html', {
        'owner': user,
        'projects': sorted_projects,
        'is_mypage': request.user == user
    })
