"""
Módulo para el registro de operaciones y errores usando Pila
"""
from datetime import datetime
from estructuras_datos import Pila

class Logger:
    """Sistema de registro de operaciones y errores"""
    def __init__(self):
        self.operaciones = Pila()
        self.errores = Pila()
    
    def registrar_operacion(self, comando, resultado="Éxito"):
        """Registra una operación en el log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entrada = f"[{timestamp}] {comando} -> {resultado}"
        self.operaciones.apilar(entrada)
    
    def registrar_error(self, comando, error):
        """Registra un error en el log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entrada = f"[{timestamp}] {comando} -> ERROR: {error}"
        self.errores.apilar(entrada)
        self.operaciones.apilar(entrada)
    
    def mostrar_operaciones(self):
        """Muestra el historial de operaciones (LIFO)"""
        return self.operaciones.obtener_todos()
    
    def mostrar_errores(self):
        """Muestra el historial de errores (LIFO)"""
        return self.errores.obtener_todos()
    
    def limpiar_logs(self):
        """Limpia todos los logs"""
        self.operaciones.vaciar()
        self.errores.vaciar()
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de los logs"""
        return {
            'total_operaciones': self.operaciones.tamanio,
            'total_errores': self.errores.tamanio
        }