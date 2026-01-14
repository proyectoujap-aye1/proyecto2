"""
Módulo que implementa el comando TYPE para creación de archivos
"""
from .base import Comando

# Caracteres no permitidos en nombres de archivos
CARACTERES_INVALIDOS = ['*', '?', '<', '>', '|', '"', '/', '\\', ':']
LONGITUD_MAXIMA_NOMBRE = 255
TAMANIO_MAXIMO_CONTENIDO_KB = 1024  # 1 MB


class ComandoTYPE(Comando):
    """Implementación del comando TYPE para árbol binario"""
    
    def validar(self, argumentos=None):
        if not argumentos:
            return False, "TYPE requiere nombre de archivo y contenido"
        
        partes = argumentos.split(' ', 1)
        if len(partes) < 2:
            return False, "TYPE requiere formato: nombre \"contenido\""
        
        nombre_archivo = partes[0]
        contenido_con_comillas = partes[1]
        
        # Validar que el contenido esté entre comillas
        if not contenido_con_comillas.startswith('"') or not contenido_con_comillas.endswith('"'):
            return False, "El contenido debe estar entre comillas"
        
        # Extraer nombre base sin extensión para validar
        if '.' in nombre_archivo:
            nombre_base = nombre_archivo.rsplit('.', 1)[0]
        else:
            nombre_base = nombre_archivo
        
        # Validar caracteres inválidos en nombre
        for char in CARACTERES_INVALIDOS:
            if char in nombre_base:
                return False, f"Error: El caracter '{char}' no está permitido en nombres de archivos. Caracteres no permitidos: {', '.join(CARACTERES_INVALIDOS)}"
        
        # Validar longitud máxima de nombre
        if len(nombre_archivo) > LONGITUD_MAXIMA_NOMBRE:
            return False, f"Error: El nombre del archivo no puede exceder {LONGITUD_MAXIMA_NOMBRE} caracteres"
        
        # Validar nombres reservados en Windows
        nombres_reservados = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                              'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                              'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if nombre_base.upper() in nombres_reservados:
            return False, f"Error: '{nombre_base}' es un nombre reservado del sistema y no puede usarse"
        
        # Validar que el nombre no empiece/termine con espacios
        if nombre_base.startswith(' ') or nombre_base.endswith(' '):
            return False, "Error: El nombre del archivo no puede empezar ni terminar con espacios"
        
        # Validar tamaño del contenido
        contenido = contenido_con_comillas[1:-1]  # Remover comillas
        tamanio_kb = len(contenido.encode('utf-8')) / 1024
        if tamanio_kb > TAMANIO_MAXIMO_CONTENIDO_KB:
            return False, f"Error: El contenido excede el tamaño máximo permitido ({TAMANIO_MAXIMO_CONTENIDO_KB} KB)"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('type'):
                return "Error: Comando TYPE deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            partes = argumentos.split(' ', 1)
            nombre_archivo_completo = partes[0]
            contenido = partes[1][1:-1]  # Remover comillas
            
            # Separar nombre y extensión
            if '.' in nombre_archivo_completo:
                nombre_base, extension = nombre_archivo_completo.rsplit('.', 1)
            else:
                nombre_base = nombre_archivo_completo
                extension = "txt"
            
            unidad_actual = sistema.obtener_unidad_actual()
            directorio_actual = unidad_actual.directorio_actual
            
            # Verificar si el archivo ya existe
            archivo_existente = directorio_actual.buscar_archivo(nombre_base)
            
            if archivo_existente:
                # El archivo existe, actualizarlo
                archivo_existente.actualizar_contenido(contenido)
                archivo_existente.extension = extension
                
                logger.registrar_operacion(f"type {argumentos}", f"Archivo actualizado: {nombre_archivo_completo}")
                
                mensaje = f'Archivo "{nombre_archivo_completo}" actualizado correctamente en {directorio_actual.ruta_completa}\n'
                mensaje += f'Nuevo contenido: "{contenido}"\n'
                mensaje += f'Tamaño: {archivo_existente.tamanio_kb:.2f} KB'
            else:
                # El archivo no existe, crearlo
                nuevo_archivo = unidad_actual.crear_archivo(nombre_base, contenido)
                nuevo_archivo.extension = extension
                
                # Insertar en índice global
                if indice_global:
                    indice_global.insertar_archivo(nuevo_archivo, directorio_actual.ruta_completa)
                
                logger.registrar_operacion(f"type {argumentos}", f"Archivo creado: {nombre_archivo_completo}")
                
                mensaje = f'Archivo "{nombre_archivo_completo}" creado correctamente en {directorio_actual.ruta_completa}\n'
                mensaje += f'Contenido guardado: "{contenido}"\n'
                mensaje += f'Tamaño: {nuevo_archivo.tamanio_kb:.2f} KB'
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"type {argumentos}", str(e))
            return f"Error creando archivo: {e}"


class ComandoRM(Comando):
    """Implementación del comando RM para eliminar archivos"""
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "RM requiere un nombre de archivo"
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('rm'):
                return "Error: Comando RM deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            nombre_archivo = argumentos.strip()
            
            # Separar nombre y extensión si se proporciona
            if '.' in nombre_archivo:
                nombre_base, extension = nombre_archivo.rsplit('.', 1)
            else:
                nombre_base = nombre_archivo
                extension = None
            
            unidad_actual = sistema.obtener_unidad_actual()
            directorio_actual = unidad_actual.directorio_actual
            
            # Buscar el archivo primero por nombre base (sin extensión)
            archivo = directorio_actual.buscar_archivo(nombre_base)
            
            # Si no se encuentra, intentar buscar con el nombre completo (por si acaso)
            if not archivo and extension:
                archivo = directorio_actual.buscar_archivo(nombre_archivo)
            
            if not archivo:
                # Mostrar archivos disponibles para ayudar al usuario
                archivos_disponibles = directorio_actual.listar_archivos()
                if archivos_disponibles:
                    nombres = [f"{a.nombre}.{a.extension}" for a in archivos_disponibles]
                    return f"Error: No se encontró el archivo '{nombre_archivo}'\nArchivos disponibles: {', '.join(nombres)}"
                else:
                    return f"Error: No se encontró el archivo '{nombre_archivo}' (el directorio está vacío)"
            
            # Construir la ruta completa para el índice global
            ruta_archivo = f"{directorio_actual.ruta_completa}/{archivo.nombre}.{archivo.extension}"
            
            # Eliminar del árbol binario de la carpeta
            eliminado = directorio_actual.eliminar_archivo_completo(nombre_base)
            
            if not eliminado:
                return f"Error: No se pudo eliminar el archivo '{nombre_archivo}'"
            
            # Eliminar del índice global
            if indice_global:
                indice_global.eliminar_archivo(ruta_archivo)
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"rm {nombre_archivo}", f"Archivo eliminado: {ruta_archivo}")
            
            mensaje = f'Archivo "{nombre_archivo}" eliminado correctamente de {directorio_actual.ruta_completa}'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"rm {argumentos}", str(e))
            return f"Error eliminando archivo: {e}"


class ComandoRENAME(Comando):
    """Implementación del comando RENAME para renombrar archivos"""
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "RENAME requiere: nombre_actual nuevo_nombre"
        
        partes = argumentos.strip().split()
        if len(partes) < 2:
            return False, "RENAME requiere: nombre_actual nuevo_nombre"
        
        nuevo_nombre = partes[1]
        
        # Validar caracteres inválidos en nuevo nombre
        for char in CARACTERES_INVALIDOS:
            if char in nuevo_nombre:
                return False, f"Error: El caracter '{char}' no está permitido en nombres de archivos"
        
        # Validar longitud máxima
        if len(nuevo_nombre) > LONGITUD_MAXIMA_NOMBRE:
            return False, f"Error: El nombre no puede exceder {LONGITUD_MAXIMA_NOMBRE} caracteres"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('rename'):
                return "Error: Comando RENAME deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            partes = argumentos.strip().split()
            nombre_actual = partes[0]
            nombre_nuevo = partes[1]
            
            # Separar nombre base de extensión para ambos
            if '.' in nombre_actual:
                nombre_base_actual, ext_actual = nombre_actual.rsplit('.', 1)
            else:
                nombre_base_actual = nombre_actual
                ext_actual = None
            
            if '.' in nombre_nuevo:
                nombre_base_nuevo, ext_nuevo = nombre_nuevo.rsplit('.', 1)
            else:
                nombre_base_nuevo = nombre_nuevo
                ext_nuevo = None
            
            unidad_actual = sistema.obtener_unidad_actual()
            directorio_actual = unidad_actual.directorio_actual
            
            # Buscar el archivo actual
            archivo = directorio_actual.buscar_archivo(nombre_base_actual)
            
            if not archivo:
                return f"Error: No se encontró el archivo '{nombre_actual}'"
            
            # Verificar que no exista un archivo con el nuevo nombre
            archivo_existente = directorio_actual.buscar_archivo(nombre_base_nuevo)
            if archivo_existente and archivo_existente != archivo:
                return f"Error: Ya existe un archivo con el nombre '{nombre_nuevo}'"
            
            # Guardar ruta vieja para el índice global
            ruta_vieja = f"{directorio_actual.ruta_completa}/{archivo.nombre}.{archivo.extension}"
            
            # Renombrar el archivo
            archivo.nombre = nombre_base_nuevo
            if ext_nuevo:
                archivo.extension = ext_nuevo
            
            # Nueva ruta
            ruta_nueva = f"{directorio_actual.ruta_completa}/{archivo.nombre}.{archivo.extension}"
            
            # Actualizar en el índice global
            if indice_global:
                indice_global.actualizar_archivo(ruta_vieja, archivo, directorio_actual.ruta_completa)
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"rename {argumentos}", f"Archivo renombrado: {nombre_actual} -> {nombre_nuevo}")
            
            mensaje = f'Archivo renombrado: "{nombre_actual}" -> "{archivo.nombre}.{archivo.extension}"'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"rename {argumentos}", str(e))
            return f"Error renombrando archivo: {e}"

