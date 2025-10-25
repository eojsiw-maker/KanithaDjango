from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, blank=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='core.Faculty')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('units', models.PositiveIntegerField(default=3)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='core.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('address', models.TextField(blank=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='core.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('semester', models.CharField(max_length=20)),
                ('units', models.PositiveIntegerField()),
                ('grade', models.CharField(blank=True, max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='core.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='core.Student')),
            ],
            options={
                'unique_together': {('student', 'course', 'year', 'semester')},
            },
        ),
    ]
