from django.urls import path
from lukwaapp import views

urlpatterns = [
    path('', views.index, name='index'),  
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),

    path('form/', views.form_view, name='form_view'),

    path('person/', views.person, name='person'),

    path('edit/<int:person_id>/', views.edit_person, name='edit_person'),

    path('delete/<int:person_id>/', views.delete_person, name='delete_person'),
]
