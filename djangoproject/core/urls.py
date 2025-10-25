from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('faculties/', views.faculty_list, name='faculties'),
    path('faculties/<int:pk>/', views.faculty_detail, name='faculty_detail'),
    path('departments/', views.department_list, name='departments'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('courses/', views.course_list, name='courses'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('students/', views.student_list, name='students'),
    path('students/<int:pk>/', views.student_profile, name='student_profile'),
    path('register/', views.registration_create, name='register'),
    path('registrations/', views.registration_list, name='registrations'),
    path('results/', views.results_view, name='results'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('signup/', views.signup_view, name='signup'),
]
