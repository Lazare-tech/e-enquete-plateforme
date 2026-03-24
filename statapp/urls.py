from django.urls import path
import statapp.views

app_name = 'statapp'

urlpatterns = [
   path('', statapp.views.homepage, name='homepage'),
   path('faq/', statapp.views.faq_view, name='faq'),
   path('contact/', statapp.views.contact_view, name='contact'),
   path('detail/<slug:slug>/', statapp.views.detail_stat, name='detail'),
   path('newsletter/subscribe/', statapp.views.newsletter_subscribe, name='subscribe_newsletter'),
   path('catalogue/', statapp.views.search_files, name='search'),
   path('telecharger/<int:file_id>/', statapp.views.download_stat_file, name='download'),
   path('ajout/', statapp.views.add_data_view, name='add_data'),
   path('categorie/check/', statapp.views.check_category, name='check_category'),
   ################################################################################
   path('connexion/', statapp.views.UserLoginView.as_view(), name='login'),
   path('inscription/', statapp.views.UserRegisterView.as_view(), name='register'),
   path('deconnexion/', statapp.views.LogoutView.as_view(next_page='statapp:homepage'), name='logout'),
]