#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lukwaproject.settings')
    try:
        from django.core.management import execute_from_command_line, call_command
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # If user runs the development server, attempt to create migrations and apply them
    if 'runserver' in sys.argv:
        try:
            import django
            django.setup()
            # create migrations for local apps (non-interactive)
            try:
                call_command('makemigrations', '--noinput')
            except Exception:
                # ignore makemigrations errors (files/permissions) and continue to migrate
                pass
            try:
                call_command('migrate', '--noinput')
            except Exception:
                # ignore migration runtime errors here to avoid blocking runserver startup;
                # user can run migrations manually if needed
                pass
        except Exception:
            # if django.setup() fails, let execute_from_command_line show the proper error
            pass

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
