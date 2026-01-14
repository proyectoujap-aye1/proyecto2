"""
Módulo que implementa los comandos MKDIR y RMDIR para gestión de carpetas
"""
from .base import Comando

# Caracteres no permitidos en nombres de carpetas
CARACTERES_INVALIDOS = ['*', '?', '<', '>', '|', '"', '/', '\\', ':']
LONGITUD_MAXIMA_NOMBRE = 255


class ComandoMKDIR(Comando):
    """Implementación del comando MKDIR para árbol n-ario"""
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "MKDIR requiere un nombre de carpeta"
        
        nombre = argumentos.strip()
        
        # Validar caracteres inválidos
        for char in CARACTERES_INVALIDOS:
            if char in nombre:
                return False, f"Error: El caracter '{char}' no está permitido en nombres de carpetas. Caracteres no permitidos: {', '.join(CARACTERES_INVALIDOS)}"
        
        # Validar longitud máxima
        if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
            return False, f"Error: El nombre de la carpeta no puede exceder {LONGITUD_MAXIMA_NOMBRE} caracteres"
        
        # Validar nombres reservados en Windows
        nombres_reservados = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                              'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                              'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if nombre.upper() in nombres_reservados:
            return False, f"Error: '{nombre}' es un nombre reservado del sistema y no puede usarse"
        
        # Validar que no empiece o termine con espacio o punto
        if nombre.startswith(' ') or nombre.endswith(' ') or nombre.endswith('.'):
            return False, "Error: El nombre no puede empezar/terminar con espacio ni terminar con punto"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('mkdir'):
                return "Error: Comando MKDIR deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            nombre_carpeta = argumentos.strip()
            unidad_actual = sistema.obtener_unidad_actual()
            
            nueva_carpeta = unidad_actual.crear_carpeta(nombre_carpeta)
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"mkdir {nombre_carpeta}", f"Carpeta creada: {nueva_carpeta.ruta_completa}")
            
            mensaje = f'Carpeta "{nombre_carpeta}" creada exitosamente en {unidad_actual.directorio_actual.ruta_completa}'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"mkdir {argumentos}", str(e))
            return f"Error creando carpeta: {e}"


class ComandoRMDIR(Comando):
    """Implementación del comando RMDIR con argumentos /s /q"""
    
    # Variable de clase para almacenar confirmación pendiente
    _confirmacion_pendiente = None
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "RMDIR requiere un nombre de carpeta"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('rmdir'):
                return "Error: Comando RMDIR deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            # Parsear argumentos
            partes = argumentos.split()
            modo_silencioso = '/q' in argumentos.lower() or '/s/q' in argumentos.lower() or '/q/s' in argumentos.lower()
            modo_recursivo = '/s' in argumentos.lower() or '/s/q' in argumentos.lower() or '/q/s' in argumentos.lower()
            
            # Obtener nombre de carpeta (último argumento que no sea flag)
            nombre_carpeta = None
            for parte in reversed(partes):
                if not parte.lower().startswith('/'):
                    nombre_carpeta = parte
                    break
            
            if not nombre_carpeta:
                return "Error: RMDIR requiere un nombre de carpeta"
            
            unidad_actual = sistema.obtener_unidad_actual()
            dir_actual = unidad_actual.directorio_actual
            
            # Verificar si el usuario está intentando eliminar el directorio actual
            if dir_actual.nombre == nombre_carpeta:
                return f"Error: No puedes eliminar el directorio actual '{nombre_carpeta}'. Primero navega al directorio padre con 'cd ..'"
            
            # Verificar si estamos dentro de una subcarpeta de la carpeta a eliminar
            carpeta_a_eliminar = dir_actual.buscar_carpeta(nombre_carpeta)
            
            if not carpeta_a_eliminar:
                return f"Error: No se encontró la carpeta '{nombre_carpeta}'"
            
            # Verificar si la carpeta tiene contenido
            tiene_archivos = len(carpeta_a_eliminar.listar_archivos()) > 0
            tiene_subcarpetas = len(carpeta_a_eliminar.listar_subcarpetas()) > 0
            tiene_contenido = tiene_archivos or tiene_subcarpetas
            
            if tiene_contenido and not modo_recursivo:
                num_archivos = len(carpeta_a_eliminar.listar_archivos())
                num_subcarpetas = len(carpeta_a_eliminar.listar_subcarpetas())
                return f"Error: La carpeta '{nombre_carpeta}' no está vacía ({num_archivos} archivos, {num_subcarpetas} subcarpetas). Use /s para eliminar recursivamente o /s/q para eliminar sin confirmación."
            
            # Si modo recursivo pero no silencioso, advertir
            if modo_recursivo and not modo_silencioso and tiene_contenido:
                num_archivos = len(carpeta_a_eliminar.listar_archivos())
                num_subcarpetas = len(carpeta_a_eliminar.listar_subcarpetas())
                return f"⚠️ ADVERTENCIA: Va a eliminar la carpeta '{nombre_carpeta}' con todo su contenido:\n" + \
                       f"   - {num_archivos} archivo(s)\n" + \
                       f"   - {num_subcarpetas} subcarpeta(s)\n\n" + \
                       f"Para confirmar, ejecute: rmdir /s/q {nombre_carpeta}"
            
            # Proceder con la eliminación
            # Primero eliminar todos los archivos del índice global recursivamente
            if indice_global:
                self._eliminar_archivos_indice(carpeta_a_eliminar, indice_global)
            
            eliminado = unidad_actual.eliminar_carpeta(nombre_carpeta)
            
            if not eliminado:
                return f"Error: No se pudo eliminar la carpeta '{nombre_carpeta}'"

            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"rmdir {argumentos}", f"Carpeta eliminada: {nombre_carpeta}")
            
            mensaje = f'Carpeta "{nombre_carpeta}" eliminada exitosamente de {dir_actual.ruta_completa}'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"rmdir {argumentos}", str(e))
            return f"Error eliminando carpeta: {e}"
    
    def _eliminar_archivos_indice(self, carpeta, indice_global):
        """Elimina todos los archivos de una carpeta del índice global recursivamente"""
        # Eliminar archivos de esta carpeta
        for archivo in carpeta.listar_archivos():
            ruta_archivo = f"{carpeta.ruta_completa}/{archivo.nombre}.{archivo.extension}"
            indice_global.eliminar_archivo(ruta_archivo)
        
        # Recursivamente eliminar archivos de subcarpetas
        for subcarpeta in carpeta.listar_subcarpetas():
            self._eliminar_archivos_indice(subcarpeta, indice_global)

