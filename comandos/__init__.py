"""
Paquete de comandos del sistema
Implementa el patrón Command para todos los comandos disponibles
"""

from .base import Comando
from .navegacion import ComandoCD
from .carpetas import ComandoMKDIR, ComandoRMDIR
from .archivos import ComandoTYPE
from .listado import ComandoDIR
from .historial import ComandoLOG, ComandoCLEAR
from .busqueda import ComandoINDEX


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
            'clear': ComandoCLEAR,
            'index': ComandoINDEX
        }
        
        comando_base = comando_str.lower().split()[0] if comando_str else ''
        clase_comando = comandos.get(comando_base)
        
        if clase_comando:
            return clase_comando()
        else:
            raise ValueError(f"Comando no reconocido: {comando_str}")


__all__ = [
    'Comando',
    'ComandoCD',
    'ComandoMKDIR',
    'ComandoRMDIR',
    'ComandoTYPE',
    'ComandoDIR',
    'ComandoLOG',
    'ComandoCLEAR',
    'ComandoINDEX',
    'FabricaComandos'
]
