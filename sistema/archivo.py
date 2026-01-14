"""
Módulo que define la clase Archivo del sistema
"""
from datetime import datetime


class Archivo:
    """Clase que representa un archivo en el sistema"""
    def __init__(self, nombre, contenido="", extension="txt"):
        self.nombre = nombre
        self.contenido = contenido
        self.extension = extension
        self.fecha_creacion = datetime.now()
        self.fecha_modificacion = datetime.now()
        self.tamanio_kb = len(contenido.encode('utf-8')) / 1024
    
    def __str__(self):
        return f"[ARCHIVO] {self.nombre}.{self.extension} ({self.tamanio_kb:.2f} KB)"
    
    def actualizar_contenido(self, nuevo_contenido):
        """Actualiza el contenido del archivo"""
        self.contenido = nuevo_contenido
        self.tamanio_kb = len(nuevo_contenido.encode('utf-8')) / 1024
        self.fecha_modificacion = datetime.now()
    
    def to_dict(self):
        """Convierte el archivo a diccionario para serialización"""
        return {
            'nombre': self.nombre,
            'contenido': self.contenido,
            'extension': self.extension,
            'tamanio_kb': self.tamanio_kb,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_modificacion': self.fecha_modificacion.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un archivo desde diccionario"""
        archivo = cls(data['nombre'], data['contenido'], data['extension'])
        archivo.tamanio_kb = data['tamanio_kb']
        archivo.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        archivo.fecha_modificacion = datetime.fromisoformat(data['fecha_modificacion'])
        return archivo
