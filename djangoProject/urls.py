from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirection de la page d'accueil vers l'application de clustering
def redirect_to_clustering(request):
    return redirect('upload')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clustering/', include('clusterning.urls')),
    path('', redirect_to_clustering, name='home'),  # Ajout de la redirection pour la racine
]