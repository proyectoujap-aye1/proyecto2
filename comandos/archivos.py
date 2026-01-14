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

