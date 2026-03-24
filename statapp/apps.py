from django.apps import AppConfig


class StatappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "statapp"

    def ready(self):
        import statapp.signals # Assure-toi que le chemin est correct