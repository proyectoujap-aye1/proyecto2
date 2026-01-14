"""
Módulo que implementa el comando CD para navegación
"""
from .base import Comando

# Caracteres no permitidos en nombres de carpetas
CARACTERES_INVALIDOS = ['*', '?', '<', '>', '|', '"']


class ComandoCD(Comando):
    """Implementación del comando CD para múltiples unidades"""
    
    def validar(self, argumentos=None):
        if not argumentos:
            return False, "CD requiere una ruta como argumento"
        
        # Validar caracteres inválidos (excepto / y \ que son separadores)
        for char in CARACTERES_INVALIDOS:
            if char in argumentos:
                return False, f"Error: El caracter '{char}' no está permitido en nombres de carpetas"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('cd'):
                return "Error: Comando CD deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            unidad_actual = sistema.obtener_unidad_actual()
            
            # Cambiar de unidad si el argumento es una unidad (ej: "D:")
            if argumentos.endswith(':') and len(argumentos) == 2:
                nombre_unidad = argumentos.upper()
                if sistema.cambiar_unidad(nombre_unidad):
                    nueva_unidad = sistema.obtener_unidad_actual()
                    logger.registrar_operacion(f"cd {argumentos}", f"Unidad cambiada: {nueva_unidad.nombre}")
                    return f"Unidad actual: {nueva_unidad.nombre}\\"
                else:
                    return f"Error: Unidad {nombre_unidad} no encontrada"
            
            # Navegar a directorio padre
            if argumentos == "..":
                nuevo_directorio = unidad_actual.navegar_a_ruta(argumentos)
                if nuevo_directorio:
                    unidad_actual.directorio_actual = nuevo_directorio
                    logger.registrar_operacion(f"cd {argumentos}", f"Directorio: {nuevo_directorio.ruta_completa}")
                    return f"Directorio actual: {nuevo_directorio.ruta_completa}"
                return f"Directorio actual: {unidad_actual.directorio_actual.ruta_completa}"
            
            # Verificar si es una ruta multinivel (contiene / o \)
            if '/' in argumentos or '\\' in argumentos:
                return self._navegar_multinivel(unidad_actual, argumentos, logger, config)
            
            # Navegar dentro de la unidad actual (ruta simple)
            nuevo_directorio = unidad_actual.navegar_a_ruta(argumentos)
            
            # Si la carpeta no existe, la creamos automáticamente
            if nuevo_directorio is None:
                # Crear la carpeta automáticamente
                try:
                    nueva_carpeta = unidad_actual.crear_carpeta(argumentos)
                    unidad_actual.directorio_actual = nueva_carpeta
                    logger.registrar_operacion(f"cd {argumentos}", f"Carpeta creada y navegada: {nueva_carpeta.ruta_completa}")
                    return f"La carpeta '{argumentos}' no existía. Se ha creado automáticamente.\nDirectorio actual: {nueva_carpeta.ruta_completa}"
                except ValueError as e:
                    logger.registrar_error(f"cd {argumentos}", str(e))
                    return f"Error: {e}"
            
            unidad_actual.directorio_actual = nuevo_directorio
            
            logger.registrar_operacion(f"cd {argumentos}", f"Directorio: {nuevo_directorio.ruta_completa}")
            return f"Directorio actual: {nuevo_directorio.ruta_completa}"
            
        except Exception as e:
            logger.registrar_error(f"cd {argumentos}", str(e))
            return f"Error cambiando directorio: {e}"
    
    def _navegar_multinivel(self, unidad, ruta, logger, config):
        """Navega a través de múltiples niveles de carpetas, creando las que no existan"""
        # Normalizar separadores
        ruta_normalizada = ruta.replace('\\', '/')
        partes = [p for p in ruta_normalizada.split('/') if p]
        
        carpetas_creadas = []
        
        for parte in partes:
            if parte == "..":
                # Subir un nivel
                nuevo_dir = unidad.navegar_a_ruta("..")
                if nuevo_dir:
                    unidad.directorio_actual = nuevo_dir
            else:
                # Intentar navegar a la carpeta desde el directorio actual de la unidad
                siguiente_dir = unidad.directorio_actual.buscar_carpeta(parte)
                
                if siguiente_dir is None:
                    # Crear la carpeta si no existe (usa unidad.directorio_actual internamente)
                    try:
                        siguiente_dir = unidad.crear_carpeta(parte)
                        carpetas_creadas.append(parte)
                    except ValueError as e:
                        logger.registrar_error(f"cd {ruta}", str(e))
                        return f"Error creando carpeta '{parte}': {e}"
                
                # Verificar que se creó/encontró correctamente
                if siguiente_dir:
                    unidad.directorio_actual = siguiente_dir
                else:
                    logger.registrar_error(f"cd {ruta}", f"No se pudo crear/encontrar carpeta '{parte}'")
                    return f"Error: No se pudo crear o encontrar la carpeta '{parte}'"
        
        # Obtener el directorio final
        directorio_final = unidad.directorio_actual
        mensaje = f"Directorio actual: {directorio_final.ruta_completa}"
        if carpetas_creadas:
            mensaje = f"Carpetas creadas: {', '.join(carpetas_creadas)}\n{mensaje}"
            logger.registrar_operacion(f"cd {ruta}", f"Ruta multinivel creada: {directorio_final.ruta_completa}")
        else:
            logger.registrar_operacion(f"cd {ruta}", f"Directorio: {directorio_final.ruta_completa}")
        
        return mensaje

