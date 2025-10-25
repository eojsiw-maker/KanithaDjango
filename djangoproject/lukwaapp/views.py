from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from lukwaapp.models import Person
from lukwaapp.forms import PersonForm

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def gallery(request):
    return render(request, "gallery.html")

def contact(request):
    return render(request, 'contact.html')

def form_view(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลสำเร็จ')
            return redirect('person')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
    else:
        form = PersonForm()
    return render(request, 'form_view.html', {'form': form})

def person(request):
    all_person = Person.objects.all()
    return render(request, "person.html", {'all_person': all_person})

def edit_person(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลสำเร็จ')
            return redirect('person')
    else:
        form = PersonForm(instance=person)
    return render(request, 'edit_person.html', {'form': form})

def delete_person(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    if request.method == 'POST':
        person.delete()
        messages.success(request, 'ลบข้อมูลสำเร็จ')
        return redirect('person')
    return render(request, 'delete_person.html', {'person': person})