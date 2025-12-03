"""
Módulo que define la estructura del sistema de archivos
con carpetas y archivos organizados en colas
"""
import os
import json
from datetime import datetime
from estructuras_datos import Cola

class Archivo:
    """Clase que representa un archivo en el sistema"""
    def __init__(self, nombre, contenido="", extension="txt"):
        self.nombre = nombre
        self.contenido = contenido
        self.extension = extension
        self.fecha_creacion = datetime.now()
        self.fecha_modificacion = datetime.now()
    
    def __str__(self):
        return f"[ARCHIVO] {self.nombre}.{self.extension}"
    
    def to_dict(self):
        """Convierte el archivo a diccionario para serialización"""
        return {
            'nombre': self.nombre,
            'contenido': self.contenido,
            'extension': self.extension,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_modificacion': self.fecha_modificacion.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un archivo desde diccionario"""
        archivo = cls(data['nombre'], data['contenido'], data['extension'])
        archivo.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        archivo.fecha_modificacion = datetime.fromisoformat(data['fecha_modificacion'])
        return archivo

class Carpeta:
    """Clase que representa una carpeta en el sistema"""
    def __init__(self, nombre, ruta=""):
        self.nombre = nombre
        self.ruta = ruta
        self.ruta_completa = os.path.join(ruta, nombre).replace('\\', '/')
        self.archivos = Cola()
        self.subcarpetas = Cola()
        self.fecha_creacion = datetime.now()
    
    def __str__(self):
        return f"[CARPETA] {self.nombre}"
    
    def agregar_archivo(self, archivo):
        """Agrega un archivo a la carpeta"""
        self.archivos.encolar(archivo)
    
    def agregar_subcarpeta(self, carpeta):
        """Agrega una subcarpeta"""
        self.subcarpetas.encolar(carpeta)
    
    def buscar_archivo(self, nombre):
        """Busca un archivo por nombre"""
        archivos = self.archivos.obtener_todos()
        for archivo in archivos:
            if archivo.nombre == nombre:
                return archivo
        return None
    
    def buscar_carpeta(self, nombre):
        """Busca una subcarpeta por nombre"""
        carpetas = self.subcarpetas.obtener_todos()
        for carpeta in carpetas:
            if carpeta.nombre == nombre:
                return carpeta
        return None
    
    def eliminar_archivo(self, nombre):
        """Elimina un archivo por nombre"""
        archivos_temp = []
        encontrado = False
        
        while not self.archivos.esta_vacia():
            archivo = self.archivos.desencolar()
            if archivo.nombre != nombre:
                archivos_temp.append(archivo)
            else:
                encontrado = True
        
        for archivo in archivos_temp:
            self.archivos.encolar(archivo)
        
        return encontrado
    
    def eliminar_carpeta(self, nombre):
        """Elimina una subcarpeta por nombre"""
        carpetas_temp = []
        encontrado = False
        
        while not self.subcarpetas.esta_vacia():
            carpeta = self.subcarpetas.desencolar()
            if carpeta.nombre != nombre:
                carpetas_temp.append(carpeta)
            else:
                encontrado = True
        
        for carpeta in carpetas_temp:
            self.subcarpetas.encolar(carpeta)
        
        return encontrado
    
    def to_dict(self):
        """Convierte la carpeta a diccionario para serialización"""
        return {
            'nombre': self.nombre,
            'ruta': self.ruta,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'archivos': [archivo.to_dict() for archivo in self.archivos.obtener_todos()],
            'subcarpetas': [carpeta.to_dict() for carpeta in self.subcarpetas.obtener_todos()]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una carpeta desde diccionario"""
        carpeta = cls(data['nombre'], data['ruta'])
        carpeta.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        
        # Recargar archivos
        for archivo_data in data['archivos']:
            carpeta.agregar_archivo(Archivo.from_dict(archivo_data))
        
        # Recargar subcarpetas recursivamente
        for subcarpeta_data in data['subcarpetas']:
            carpeta.agregar_subcarpeta(cls.from_dict(subcarpeta_data))
        
        return carpeta

class SistemaArchivos:
    """Clase principal del sistema de archivos"""
    def __init__(self):
        self.unidad_actual = "C:"
        # La raíz y el directorio actual deben referenciar la misma Carpeta
        self.raiz = Carpeta("", "/")
        self.directorio_actual = self.raiz
        self.raiz.ruta_completa = "C:\\"
    
    def navegar_a_ruta(self, ruta):
        """Navega a una ruta específica en el sistema de archivos"""
        if ruta == "..":
            return self._subir_directorio()
        
        if ruta.startswith("C:/") or ruta.startswith("C:\\"):
            return self._navegar_ruta_absoluta(ruta)
        
        return self._navegar_ruta_relativa(ruta)
    
    def _subir_directorio(self):
        """Sube al directorio padre"""
        if self.directorio_actual.ruta != "/":
            partes = self.directorio_actual.ruta_completa.split('/')
            nueva_ruta = '/'.join(partes[:-1]) if len(partes) > 1 else "/"
            return self._encontrar_carpeta_por_ruta(nueva_ruta)
        return self.directorio_actual
    
    def _navegar_ruta_absoluta(self, ruta):
        """Navega a una ruta absoluta"""
        ruta_limpia = ruta.replace('C:', '').replace('\\', '/').strip('/')
        return self._encontrar_carpeta_por_ruta(f"/{ruta_limpia}")
    
    def _navegar_ruta_relativa(self, ruta):
        """Navega a una ruta relativa"""
        carpeta = self.directorio_actual.buscar_carpeta(ruta)
        if carpeta:
            return carpeta
        return self.directorio_actual
    
    def _encontrar_carpeta_por_ruta(self, ruta):
        """Encuentra una carpeta por su ruta completa"""
        if ruta == "/" or ruta == "C:\\":
            return self.raiz
        
        partes = ruta.strip('/').split('/')
        actual = self.raiz
        
        for parte in partes:
            if parte:
                siguiente = actual.buscar_carpeta(parte)
                if not siguiente:
                    return actual  # No se encontró, retorna el último directorio válido
                actual = siguiente
        
        return actual
    
    def crear_carpeta(self, nombre, ruta_destino=None):
        """Crea una nueva carpeta"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        ruta_base = destino.ruta_completa if destino != self.raiz else "C:\\"
        
        nueva_carpeta = Carpeta(nombre, ruta_base)
        
        # Verificar si ya existe
        if destino.buscar_carpeta(nombre):
            raise ValueError(f"La carpeta '{nombre}' ya existe en este directorio")
        
        destino.agregar_subcarpeta(nueva_carpeta)
        return nueva_carpeta
    
    def crear_archivo(self, nombre, contenido="", ruta_destino=None):
        """Crea un nuevo archivo"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        
        # Verificar si ya existe
        if destino.buscar_archivo(nombre):
            raise ValueError(f"El archivo '{nombre}' ya existe en este directorio")
        
        nuevo_archivo = Archivo(nombre, contenido)
        destino.agregar_archivo(nuevo_archivo)
        return nuevo_archivo
    
    def eliminar_carpeta(self, nombre, ruta_destino=None):
        """Elimina una carpeta y su contenido"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        return destino.eliminar_carpeta(nombre)
    
    def listar_contenido(self, ruta_destino=None):
        """Lista el contenido de un directorio"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        
        contenido = []
        contenido.extend(destino.subcarpetas.obtener_todos())
        contenido.extend(destino.archivos.obtener_todos())
        
        return contenido
    
    def obtener_estructura_completa(self):
        """Obtiene toda la estructura del sistema de archivos para backup"""
        return self.raiz.to_dict()
    
    def cargar_estructura(self, data):
        """Carga la estructura del sistema de archivos desde backup"""
        self.raiz = Carpeta.from_dict(data)
        self.directorio_actual = self.raiz