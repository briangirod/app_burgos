from django import template
from ..models import PerfilUsuario

register = template.Library()

@register.filter
def nombre_completo(user):
    """
    Obtiene el nombre completo del usuario desde su perfil o fallback al username
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.nombre_completo()
    except PerfilUsuario.DoesNotExist:
        return user.get_full_name() if user.get_full_name() else user.username