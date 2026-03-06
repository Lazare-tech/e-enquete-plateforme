from django.urls import path
import statapp.views

app_name = 'statapp'

urlpatterns = [
   path('', statapp.views.homepage, name='homepage'),
   path('faq/', statapp.views.faq_view, name='faq'),
   path('detail/<slug:slug>/', statapp.views.detail_stat, name='detail'),
   path('recherche/', statapp.views.search_files, name='search'),
   path('telecharger/<int:file_id>/', statapp.views.download_stat_file, name='download'),
   
   ################################################################################
   path('connexion/', statapp.views.UserLoginView.as_view(), name='login'),
   path('inscription/', statapp.views.UserRegisterView.as_view(), name='register'),
   path('deconnexion/', statapp.views.LogoutView.as_view(next_page='statapp:homepage'), name='logout'),
]