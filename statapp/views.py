from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statapp.forms import CleanRegisterForm
from .models import Category, StatFile,UserFileAccess,FAQ, VariableCategory
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import StatFileForm, StatVariableForm

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
# ###
# def check_category(request):
#     title = request.GET.get('title', '').strip()
#     if not title:
#         return HttpResponse("")
    
#     exists = Category.objects.filter(title__iexact=title).exists()
#     if exists:
#         return HttpResponse('<span class="text-danger small"><i class="fas fa-exclamation-triangle"></i> Cette catégorie existe déjà !</span>')
#     else:
#         return HttpResponse('<span class="text-success small"><i class="fas fa-check"></i> Nom disponible (sera soumis à validation)</span>')
def check_category(request):
    # On récupère le titre peu importe le nom du champ envoyé dans le HTML
    title = (request.GET.get('new_file_category_title') or 
             request.GET.get('new_category_title') or 
             '').strip()
    
    category_type = request.GET.get('type', 'file')
    
    if not title:
        return HttpResponse("")
    
    # 1. Logique de sélection du modèle et des éléments visuels
    if category_type == 'variable':
        exists = VariableCategory.objects.filter(title__iexact=title).exists()
        target_btn = "btn-submit-var"
        btn_icon = '<i class="fas fa-check-circle me-2"></i>'
        btn_class = "btn-success"
    else:
        exists = Category.objects.filter(title__iexact=title).exists()
        target_btn = "btn-submit-file"
        btn_icon = '<i class="fas fa-cloud-upload-alt me-2"></i>'
        btn_class = "btn-primary"

    # 2. Construction de la réponse HTML
    if exists:
        content = f'''
            <span class="text-danger small fw-bold">
                <i class="fas fa-exclamation-triangle me-1"></i> Cette catégorie existe déjà !
            </span>
            <button id="{target_btn}" hx-swap-oob="true" disabled class="btn btn-secondary w-100 py-3 mt-2">
                Nom déjà utilisé
            </button>
        '''
    else:
        content = f'''
            <span class="text-success small fw-bold">
                <i class="fas fa-check me-1"></i> Nom disponible (en attente de validation)
            </span>
            <button id="{target_btn}" hx-swap-oob="true" class="btn {btn_class} w-100 py-3 mt-2">
                {btn_icon} Enregistrer
            </button>
        '''
    
    return HttpResponse(content)
######
def error_404_view(request, exception):
    return render(request, '404.html', status=404)
###
def search_files(request):
    # Récupérer les deux paramètres : texte et catégorie
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    # On commence par tous les fichiers actifs
    files = StatFile.objects.filter(is_active=True).order_by('-created_at') # Tri ajouté
    
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
######################

@login_required
@user_passes_test(lambda u: u.is_staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_data_view(request):
    file_form = StatFileForm(request.POST or None, request.FILES or None)
    var_form = StatVariableForm(request.POST or None)

    if request.method == 'POST':
        # --- CAS 1 : FICHIER ---
        if 'submit_file' in request.POST:
            new_file_cat_title = request.POST.get('new_file_category_title', '').strip()
            
            # On vérifie si le formulaire est valide 
            # (ou s'il n'y a QUE l'erreur de catégorie et qu'on a un nouveau titre)
            form_is_ok = file_form.is_valid()
            if not form_is_ok and new_file_cat_title and 'category' in file_form.errors and len(file_form.errors) == 1:
                form_is_ok = True

            if form_is_ok:
                try:
                    stat_file = file_form.save(commit=False)
                    
                    if new_file_cat_title:
                        # On crée la catégorie sans 'is_active'
                        cat, _ = Category.objects.get_or_create(
                            title__iexact=new_file_cat_title,
                            defaults={'title': new_file_cat_title}
                        )
                        stat_file.category = cat
                    else:
                        stat_file.category = file_form.cleaned_data.get('category')

                    # Sécurité : Si aucune catégorie n'est trouvée (ni nouvelle, ni sélectionnée)
                    if not stat_file.category:
                        messages.error(request, "Veuillez indiquer une catégorie.")
                    else:
                        stat_file.save()
                        messages.success(request, "Fichier ajouté avec succès !")
                        return redirect('statapp:search')
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement : {e}")
            else:
                # Si le formulaire échoue, on affiche pourquoi (ex: fichier manquant)
                messages.error(request, f"Le formulaire est invalide : {file_form.errors}")

        # --- CAS 2 : VARIABLE ---
        elif 'submit_var' in request.POST:
            # Ta logique de variable qui fonctionne déjà...
            if var_form.is_valid() or (request.POST.get('new_category_title') and 'category' in var_form.errors):
                variable = var_form.save(commit=False)
                new_title = request.POST.get('new_category_title', '').strip()
                if new_title:
                    cat, _ = VariableCategory.objects.get_or_create(
                        title__iexact=new_title, defaults={'title': new_title, 'is_active': False}
                    )
                    variable.category = cat
                else:
                    variable.category = var_form.cleaned_data.get('category')
                
                variable.created_by = request.user
                variable.save()
                messages.success(request, "Variable ajoutée avec succès.")
                return redirect('statapp:homepage')

    return render(request, 'statapp/stats/add_data.html', {'file_form': file_form, 'var_form': var_form})
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