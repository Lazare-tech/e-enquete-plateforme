from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import StatFile, Newsletter

@receiver(pre_save, sender=StatFile)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = StatFile.objects.get(pk=instance.pk)
            instance._was_active = old_instance.is_active
        except StatFile.DoesNotExist:
            instance._was_active = False
    else:
        instance._was_active = False

@receiver(post_save, sender=StatFile)
def notify_subscribers_on_activation(sender, instance, created, **kwargs):
    # On vérifie si on vient de passer de 'Invisible' à 'Visible'
    was_active_before = getattr(instance, '_was_active', False)
    
    if instance.is_active and not was_active_before:
        subscribers = list(Newsletter.objects.values_list('email', flat=True))
        
        if subscribers:
            # 1. Génération du lien vers la vue détail
            # reverse('statapp:detail', kwargs={'slug': instance.slug})
            relative_url = reverse('statapp:detail', kwargs={'slug': instance.slug})
            
            # 2. Construction de l'URL absolue
            domain = getattr(settings, 'SITE_URL', 'https://2034-41-138-107-85.ngrok-free.app')
            full_url = f"{domain}{relative_url}"
            
            subject = f"📊 Nouvelle ressource : {instance.title}"
            
            message = f"""
            Bonjour,
            
            Un nouveau fichier statistique vient d'être publié sur notre portail.
            
            📂 Titre : {instance.title}
            📝 Description : {instance.description[:200]}...
            
            Consultez les détails:
            {full_url}
            
            L'équipe du Portail de Données.
            """
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                subscribers,
                fail_silently=False,
            )