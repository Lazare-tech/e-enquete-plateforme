from django.shortcuts import render
from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statapp.forms import CleanRegisterForm
from .models import StatFile,UserFileAccess,FAQ
from django.db.models import Q
# Create your views here.
def homepage(request):
    # On récupère les fichiers actifs, triés par date (géré par Meta dans le modèle)
    files = StatFile.objects.filter(is_active=True)
    ##
    context={
        'files': files
    }
    return render(request, 'statapp/index.html', context)
###

def faq_view(request):
    faqs = FAQ.objects.filter(is_active=True)
    context={
        'faqs': faqs
    }
    return render(request, 'statapp/partials/faq.html', context)
###
def error_404_view(request, exception):
    return render(request, '404.html', status=404)
###
def search_files(request):
    # Récupérer les deux paramètres : texte et catégorie
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    print("cccccccc",category_slug)
    # On commence par tous les fichiers actifs
    files = StatFile.objects.filter(is_active=True)
    
    # Filtre 1 : Par texte (Titre ou Description)
    if query:
        files = files.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_slug:
        files = files.filter(category__slug=category_slug)
    # Filtre 2 : Par catégorie (via le slug de la catégorie)
    if category_slug:
        files = files.filter(category__slug=category_slug)

    # LOGIQUE HTMX : Indispensable pour la fluidité Shine Agency
    if request.headers.get('HX-Request'):
        context={
            'files':files,
            'current_query': query,        
        'current_category': category_slug
        }
        return render(request, 'statapp/partials/file_list.html', context)

    return render(request, 'statapp/index.html', {'files': files})
###
@login_required
def download_stat_file(request, file_id):
    stat_file = get_object_or_404(StatFile, id=file_id)
    
    # Vérification : est-ce que l'utilisateur a l'autorisation ?
    # (Soit il est staff, soit il a une entrée dans UserFileAccess)
    has_access = UserFileAccess.objects.filter(user=request.user, stat_file=stat_file).exists()
    
    if not request.user.is_staff and not has_access:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de télécharger ce fichier.")

    # Si autorisé, on sert le fichier
    file_path = stat_file.file.path
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    return response
    return response
#################3
def detail_stat(request, slug):
    file = get_object_or_404(StatFile, slug=slug, is_active=True)
    
    # Vérification de l'accès spécifique
    has_access = False
    if request.user.is_authenticated:
        has_access = UserFileAccess.objects.filter(user=request.user, stat_file=file).exists()
    
    context = {
        'file': file,
        'has_access': has_access,
    }
    return render(request, 'statapp/stats/detail.html', context)
#########################################################################################
class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True  # Redirige si déjà connecté
    
    def get_success_url(self):
        return reverse_lazy('statapp:search') # Redirection après connexion

class UserRegisterView(CreateView):
    form_class = CleanRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('statapp:login') # Redirige vers connexion après succès

    def form_valid(self, form):
        # Petit message de succès senior pour l'UX
        messages.success(self.request, "Compte créé avec succès ! Vous pouvez vous connecter.")
        return super().form_valid(form)