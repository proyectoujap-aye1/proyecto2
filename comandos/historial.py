"""
Módulo que implementa los comandos LOG y CLEAR LOG para historial
"""
from .base import Comando


class ComandoLOG(Comando):
    """Implementación del comando LOG"""
    
    def validar(self, argumentos=None):
        return True, "OK"
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
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
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
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
