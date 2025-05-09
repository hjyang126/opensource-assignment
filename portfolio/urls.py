from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import mypage


urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('mypage/', mypage, name='mypage'),
    path('user/<str:username>/', views.user_page, name='user_page'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

]


   
