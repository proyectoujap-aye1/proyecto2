"""
Módulo base que define la interfaz abstracta para comandos
"""
from abc import ABC, abstractmethod


class Comando(ABC):
    """Interfaz abstracta para el patrón Command"""
    
    @abstractmethod
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        pass
    
    @abstractmethod
    def validar(self, argumentos=None):
        pass
