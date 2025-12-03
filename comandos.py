"""
Módulo que implementa el patrón Command para los comandos del sistema
"""
import os
from abc import ABC, abstractmethod

class Comando(ABC):
    """Interfaz abstracta para el patrón Command"""
    
    @abstractmethod
    def ejecutar(self, sistema, logger, config, argumentos=None):
        pass
    
    @abstractmethod
    def validar(self, argumentos=None):
        pass

class ComandoCD(Comando):
    """Implementación del comando CD"""
    
    def validar(self, argumentos=None):
        if not argumentos:
            return False, "CD requiere una ruta como argumento"
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('cd'):
                return "Error: Comando CD deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            nuevo_directorio = sistema.navegar_a_ruta(argumentos)
            sistema.directorio_actual = nuevo_directorio
            
            logger.registrar_operacion(f"cd {argumentos}", f"Directorio: {nuevo_directorio.ruta_completa}")
            return f"Directorio actual: {nuevo_directorio.ruta_completa}"
            
        except Exception as e:
            logger.registrar_error(f"cd {argumentos}", str(e))
            return f"Error cambiando directorio: {e}"

class ComandoMKDIR(Comando):
    """Implementación del comando MKDIR"""
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "MKDIR requiere un nombre de carpeta"
        
        nombre = argumentos.strip()
        if '/' in nombre or '\\' in nombre:
            return False, "Nombre de carpeta no puede contener / o \\"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('mkdir'):
                return "Error: Comando MKDIR deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            nombre_carpeta = argumentos.strip()
            nueva_carpeta = sistema.crear_carpeta(nombre_carpeta)
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"mkdir {nombre_carpeta}", f"Carpeta creada: {nueva_carpeta.ruta_completa}")
            
            mensaje = f'Carpeta "{nombre_carpeta}" creada exitosamente en {sistema.directorio_actual.ruta_completa}'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"mkdir {argumentos}", str(e))
            return f"Error creando carpeta: {e}"

class ComandoRMDIR(Comando):
    """Implementación del comando RMDIR"""
    
    def validar(self, argumentos=None):
        if not argumentos or not argumentos.strip():
            return False, "RMDIR requiere un nombre de carpeta"
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('rmdir'):
                return "Error: Comando RMDIR deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            nombre_carpeta = argumentos.strip()
            eliminado = sistema.eliminar_carpeta(nombre_carpeta)
            
            if not eliminado:
                return f"Error: No se encontró la carpeta '{nombre_carpeta}'"
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"rmdir {nombre_carpeta}", f"Carpeta eliminada")
            
            mensaje = f'Carpeta "{nombre_carpeta}" eliminada exitosamente de {sistema.directorio_actual.ruta_completa}'
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"rmdir {argumentos}", str(e))
            return f"Error eliminando carpeta: {e}"

class ComandoTYPE(Comando):
    """Implementación del comando TYPE"""
    
    def validar(self, argumentos=None):
        if not argumentos:
            return False, "TYPE requiere nombre de archivo y contenido"
        
        partes = argumentos.split(' ', 1)
        if len(partes) < 2:
            return False, "TYPE requiere formato: nombre \"contenido\""
        
        if not partes[1].startswith('"') or not partes[1].endswith('"'):
            return False, "El contenido debe estar entre comillas"
        
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('type'):
                return "Error: Comando TYPE deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            partes = argumentos.split(' ', 1)
            nombre_archivo = partes[0]
            contenido = partes[1][1:-1]  # Remover comillas
            
            nuevo_archivo = sistema.crear_archivo(nombre_archivo, contenido)
            
            # Backup automático
            estructura = sistema.obtener_estructura_completa()
            archivo_backup = config.hacer_backup(estructura)
            
            logger.registrar_operacion(f"type {argumentos}", f"Archivo creado: {nombre_archivo}")
            
            mensaje = f'Archivo "{nombre_archivo}" creado correctamente en {sistema.directorio_actual.ruta_completa}\n'
            mensaje += f'Contenido guardado: "{contenido}"'
            
            if archivo_backup:
                mensaje += f"\nRespaldo automático realizado en {archivo_backup}"
            
            return mensaje
            
        except Exception as e:
            logger.registrar_error(f"type {argumentos}", str(e))
            return f"Error creando archivo: {e}"

class ComandoDIR(Comando):
    """Implementación del comando DIR"""
    
    def validar(self, argumentos=None):
        # DIR puede tener argumentos opcionales
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('dir'):
                return "Error: Comando DIR deshabilitado"
            
            destino = None
            if argumentos:
                destino = sistema._encontrar_carpeta_por_ruta(argumentos)
            
            contenido = sistema.listar_contenido(destino)
            directorio_actual = destino.ruta_completa if destino else sistema.directorio_actual.ruta_completa
            
            resultado = f"Directorio de {directorio_actual}\n"
            for elemento in contenido:
                resultado += f"{elemento}\n"
            
            if not contenido:
                resultado += "El directorio está vacío\n"
            
            logger.registrar_operacion(f"dir {argumentos if argumentos else ''}", f"Elementos listados: {len(contenido)}")
            return resultado
            
        except Exception as e:
            logger.registrar_error(f"dir {argumentos}", str(e))
            return f"Error listando directorio: {e}"

class ComandoLOG(Comando):
    """Implementación del comando LOG"""
    
    def validar(self, argumentos=None):
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('log'):
                return "Error: Comando LOG deshabilitado"
            
            operaciones = logger.mostrar_operaciones()
            
            resultado = "--- Historial de Operaciones (LIFO) ---\n"
            for op in operaciones:
                resultado += f"{op}\n"
            
            if not operaciones:
                resultado += "No hay operaciones registradas\n"
            
            logger.registrar_operacion("log", "Historial mostrado")
            return resultado
            
        except Exception as e:
            logger.registrar_error("log", str(e))
            return f"Error mostrando log: {e}"

class ComandoCLEAR(Comando):
    """Implementación del comando CLEAR LOG"""
    
    def validar(self, argumentos=None):
        if argumentos != "log":
            return False, "CLEAR solo acepta 'log' como argumento"
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, argumentos=None):
        try:
            if not config.comando_habilitado('clear'):
                return "Error: Comando CLEAR deshabilitado"
            
            valido, mensaje = self.validar(argumentos)
            if not valido:
                return mensaje
            
            logger.limpiar_logs()
            logger.registrar_operacion("clear log", "Logs limpiados")
            return "El historial de errores y operaciones ha sido limpiado."
            
        except Exception as e:
            logger.registrar_error("clear log", str(e))
            return f"Error limpiando logs: {e}"

class FabricaComandos:
    """Fábrica para crear instancias de comandos"""
    
    @staticmethod
    def crear_comando(comando_str):
        comandos = {
            'cd': ComandoCD,
            'mkdir': ComandoMKDIR,
            'rmdir': ComandoRMDIR,
            'type': ComandoTYPE,
            'dir': ComandoDIR,
            'log': ComandoLOG,
            'clear': ComandoCLEAR
        }
        
        comando_base = comando_str.lower().split()[0] if comando_str else ''
        clase_comando = comandos.get(comando_base)
        
        if clase_comando:
            return clase_comando()
        else:
            raise ValueError(f"Comando no reconocido: {comando_str}")