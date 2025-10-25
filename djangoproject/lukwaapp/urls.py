from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),
    path('form/', views.form_view, name='form'),
    path('person/', views.person, name='person'),
    path('person/edit/<int:person_id>/', views.edit_person, name='edit_person'),
    path('person/delete/<int:person_id>/', views.delete_person, name='delete_person'),
]