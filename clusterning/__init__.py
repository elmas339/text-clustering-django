def initialize_django():
    import django
    import os  # Ajoutez cette ligne si elle n'est pas déjà présente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')  # Assurez-vous que le chemin est correct
    django.setup()