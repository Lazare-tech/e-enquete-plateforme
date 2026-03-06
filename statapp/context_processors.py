from .models import Category

def categories_processor(request):
    """Rend les catégories disponibles partout dans le projet"""
    return {
        'all_categories': Category.objects.all().order_by('title')
    }
###
def contact_processor(request):
    """Rend les informations de contact disponibles partout dans le projet"""
    return {
        'contact_email': 'stat@gmail.com',
        'contact_res': '+226 72 78 72 15',
        'contact_res2': '+226 74 47 81 12',
        'address': 'Bobo-Dioulasso, Burkina Faso'
    }