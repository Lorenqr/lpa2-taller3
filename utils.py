"""
Módulo de utilidades para la aplicación.
Contiene funciones auxiliares utilizadas en diferentes partes de la aplicación.
"""
import re
from datetime import datetime

def validar_correo(correo):
    """
    Valida que un correo electrónico tenga un formato válido.
    
    Args:
        correo (str): Correo electrónico a validar
        
    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    # TODO: crear la expresión regular para validar el correo
    patron = ""
    return bool(re.match(patron, correo))

def formatear_duracion(segundos):
    """
    Convierte una duración en segundos a formato mm:ss.
    
    Args:
        segundos (int): Duración en segundos
        
    Returns:
        str: Duración formateada como mm:ss
    """
    # TODO: pendiente de implementar
    pass 

def generar_slug(texto):
    """
    Genera un slug a partir de un texto.
    Un slug es una versión de texto amigable para URLs.
    
    Args:
        texto (str): Texto a convertir en slug
        
    Returns:
        str: Slug generado
    """
    # TODO: Convertir a minúsculas
    slug = texto
    
    # TODO: Reemplazar espacios con guiones
    
    # TODO: Eliminar caracteres no alfanuméricos (excepto guiones)
    
    # TODO: Reemplazar múltiples guiones con uno solo
    
    # TODO: Eliminar guiones al inicio y final
    
    return slug

def obtener_año_actual():
    """
    Obtiene el año actual.
    
    Returns:
        int: Año actual
    """
    # TODO: pendiente por implementar
    return ""

def validar_año(año):
    """
    Valida que un año sea válido (no futuro y no muy antiguo).
    
    Args:
        año (int): Año a validar
        
    Returns:
        bool: True si el año es válido, False en caso contrario
    """
    año_actual = obtener_año_actual()
    return 1900 <= año <= año_actual

