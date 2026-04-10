from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import StatFile, Newsletter
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
### Signal pour capturer l'ancien état d'un fichier
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
    was_active_before = getattr(instance, '_was_active', False)
    
    if instance.is_active and not was_active_before:
        subscribers = Newsletter.objects.all()
        
        for sub in subscribers:
            # 1. Préparation des liens
            domain = getattr(settings, 'SITE_URL', 'https://aeaf-41-138-107-85.ngrok-free.app')
            detail_url = f"{domain}{reverse('statapp:detail', kwargs={'slug': instance.slug})}"
            unsub_url = f"{domain}{reverse('statapp:unsubscribe_newsletter', kwargs={'email': sub.email})}"
            
            subject = f"📊 Nouveau fichier : {instance.title}"
            
            # 2. Contenu HTML du mail
            html_content = f"""
            <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                <h2 style="color: #122046;">Bonjour,</h2>
                <p>Un nouveau jeu de données vient d'être publié sur notre portail.</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">{instance.title}</h3>
                    <p>{instance.description[:150]}...</p>
                    <a href="{detail_url}" style="display: inline-block; padding: 10px 20px; background-color: #1D5DA3;; color: white; text-decoration: none; border-radius: 50px; font-weight: bold;">Consulter le fichier</a>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                
                <footer style="font-size: 12px; color: #777; text-align: center;">
                    <p><strong>Statisticiens - Portail de Données</strong></p>
                    <p>Burkina Faso, Bobo-Dioulasso <br> Tel : <a href="tel:+226XXXXXXXX">+226 XX XX XX XX</a></p>
                    <p>Responsable : M. Traoré</p>
                    <p style="margin-top: 20px;">
                        Vous ne souhaitez plus recevoir ces emails ? 
                        <a href="{unsub_url}" style="color: #dc3545; text-decoration: underline;">Se désabonner de la newsletter</a>
                    </p>
                </footer>
            </div>
            """
            
            # 3. Version texte brut (fallback)
            text_content = strip_tags(html_content)
            
            # 4. Envoi de l'e-mail
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [sub.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()