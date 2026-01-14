"""
Módulo que define la clase Carpeta del sistema
"""
from datetime import datetime
from arboles import ArbolBinarioBusqueda, NodoArbolNario
from .archivo import Archivo


class Carpeta:
    """Clase que representa una carpeta en el sistema (nodo del árbol n-ario)"""
    def __init__(self, nombre, ruta=""):
        self.nombre = nombre
        self.ruta = ruta
        # Construir ruta completa correctamente
        # Normalizar la ruta (quitar barras finales y reemplazar backslash)
        ruta_normalizada = ruta.replace('\\', '/').rstrip('/')
        
        if not ruta_normalizada:
            # Si no hay ruta, solo usar el nombre
            self.ruta_completa = nombre
        elif ruta_normalizada.endswith(':'):
            # Es una raíz de unidad (ej: "D:")
            self.ruta_completa = f"{ruta_normalizada}/{nombre}"
        else:
            # Ruta normal
            self.ruta_completa = f"{ruta_normalizada}/{nombre}"
        self.arbol_archivos = ArbolBinarioBusqueda()
        self.nodo_arbol = NodoArbolNario(self)
        self.fecha_creacion = datetime.now()
    
    def __str__(self):
        return f"[CARPETA] {self.nombre} ({len(self.listar_archivos())} archivos)"
    
    def agregar_archivo(self, archivo):
        """Agrega un archivo al árbol binario de la carpeta"""
        self.arbol_archivos.insertar(archivo)
    
    def agregar_subcarpeta(self, carpeta):
        """Agrega una subcarpeta al árbol n-ario"""
        self.nodo_arbol.agregar_hijo(carpeta.nodo_arbol)
    
    def buscar_archivo(self, nombre):
        """Busca un archivo por nombre en el árbol binario"""
        return self.arbol_archivos.buscar(nombre)
    
    def buscar_archivos_parcial(self, texto):
        """Busca archivos que contengan texto en su nombre"""
        return self.arbol_archivos.buscar_parcial(texto)
    
    def buscar_archivos_por_tamanio(self, min_kb, max_kb):
        """Busca archivos por rango de tamaño"""
        return self.arbol_archivos.buscar_por_rango_tamanio(min_kb, max_kb)
    
    def buscar_carpeta(self, nombre):
        """Busca una subcarpeta por nombre (case-insensitive)"""
        nombre_lower = nombre.lower()
        for hijo in self.nodo_arbol.hijos:
            if hijo.dato.nombre.lower() == nombre_lower:
                return hijo.dato
        return None
    
    def eliminar_archivo(self, nombre):
        """Elimina un archivo por nombre (simulación - solo verifica existencia)"""
        archivo = self.buscar_archivo(nombre)
        if archivo:
            return True
        return False
    
    def eliminar_archivo_completo(self, nombre):
        """Elimina un archivo completamente del árbol binario"""
        return self.arbol_archivos.eliminar(nombre)

    
    def eliminar_carpeta(self, nombre):
        """Elimina una subcarpeta por nombre (case-insensitive)"""
        nombre_lower = nombre.lower()
        for i, hijo in enumerate(self.nodo_arbol.hijos):
            if hijo.dato.nombre.lower() == nombre_lower:
                del self.nodo_arbol.hijos[i]
                return True
        return False
    
    def listar_archivos(self):
        """Lista todos los archivos en orden"""
        return self.arbol_archivos.recorrer_inorden()
    
    def listar_archivos_preorden(self):
        """Lista archivos en preorden"""
        return self.arbol_archivos.recorrer_preorden()
    
    def listar_archivos_postorden(self):
        """Lista archivos en postorden"""
        return self.arbol_archivos.recorrer_postorden()
    
    def listar_subcarpetas(self):
        """Lista todas las subcarpetas"""
        return [hijo.dato for hijo in self.nodo_arbol.hijos]
    
    def to_dict(self):
        """Convierte la carpeta a diccionario para serialización"""
        return {
            'nombre': self.nombre,
            'ruta': self.ruta,
            'ruta_completa': self.ruta_completa,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'archivos': [archivo.to_dict() for archivo in self.listar_archivos()],
            'subcarpetas': [carpeta.to_dict() for carpeta in self.listar_subcarpetas()]
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
        subcarpetas_temp = []
        for subcarpeta_data in data['subcarpetas']:
            subcarpeta = cls(subcarpeta_data['nombre'], subcarpeta_data['ruta'])
            subcarpeta.fecha_creacion = datetime.fromisoformat(subcarpeta_data['fecha_creacion'])
            subcarpetas_temp.append((subcarpeta, subcarpeta_data))
        
        for subcarpeta, subcarpeta_data in subcarpetas_temp:
            for archivo_data in subcarpeta_data['archivos']:
                subcarpeta.agregar_archivo(Archivo.from_dict(archivo_data))
            
            for subsubcarpeta_data in subcarpeta_data['subcarpetas']:
                subsubcarpeta = cls.from_dict(subsubcarpeta_data)
                subcarpeta.agregar_subcarpeta(subsubcarpeta)
            
            carpeta.agregar_subcarpeta(subcarpeta)
        
        return carpeta
