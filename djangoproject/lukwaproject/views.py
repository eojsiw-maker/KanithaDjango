from django.shortcuts import render, redirect, get_object_or_404
from people.models import Person

def index(request):
    return render(request, 'index.html', {'message': 'สวัสดี — หน้าแรก'})

def about(request):
    return render(request, 'about.html', {'title': 'About', 'content': 'ข้อมูลเกี่ยวกับโปรเจกต์'})

def gallery(request):
    images = ['/static/images/sample1.jpg', '/static/images/sample2.jpg']
    return render(request, 'gallery.html', {'images': images, 'title': 'Gallery'})

def contact(request):
    return render(request, 'contact.html', {'title': 'Contact', 'email': 'support@example.com'})

def form_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        message = request.POST.get('message', '').strip()
        return render(request, 'form.html', {'submitted': True, 'name': name, 'message': message, 'title': 'Contact Form'})
    return render(request, 'form.html', {'submitted': False, 'title': 'Contact Form'})

def person(request):
    people = Person.objects.all()
    return render(request, 'person.html', {'people': people, 'title': 'People'})

def edit_person(request, person_id):
    """
    Edit Person: GET shows form, POST updates and redirects to person list.
    """
    person_obj = get_object_or_404(Person, pk=person_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        role = request.POST.get('role', '').strip()
        if name:
            person_obj.name = name
        person_obj.role = role
        person_obj.save()
        return redirect('person')
    return render(request, 'edit_person.html', {'person': person_obj, 'title': 'Edit Person'})
