"""
Módulo que define la clase UnidadAlmacenamiento
"""
from arboles import ArbolNArio, NodoArbolNario
from .archivo import Archivo
from .carpeta import Carpeta


class UnidadAlmacenamiento:
    """Clase que representa una unidad de almacenamiento (C:, D:, etc.)"""
    def __init__(self, nombre):
        self.nombre = nombre
        self.arbol_directorios = ArbolNArio()
        self.directorio_actual = None
        self._inicializar_estructura()
    
    def __str__(self):
        return f"[UNIDAD] {self.nombre}"
    
    def _inicializar_estructura(self):
        """Inicializa la estructura de directorios de la unidad"""
        # Crear carpeta raíz con formato consistente
        raiz = Carpeta("", "")
        raiz.nombre = self.nombre
        raiz.ruta = ""
        raiz.ruta_completa = f"{self.nombre}:/"
        
        # Usar el mismo nodo_arbol de la carpeta como raíz del árbol de directorios
        # Esto asegura que cuando se agregan subcarpetas, el árbol esté correctamente conectado
        self.arbol_directorios.raiz = raiz.nodo_arbol
        self.directorio_actual = raiz
    
    def navegar_a_ruta(self, ruta):
        """Navega a una ruta específica"""
        if not ruta or ruta == ".":
            return self.directorio_actual
        
        if ruta == "..":
            return self._subir_directorio()
        
        if ruta.startswith(f"{self.nombre}:/") or ruta.startswith(f"{self.nombre}:\\"):
            return self._navegar_ruta_absoluta(ruta)
        
        return self._navegar_ruta_relativa(ruta)
    
    def _subir_directorio(self):
        """Sube al directorio padre"""
        # Si ya estamos en la raíz, no hacemos nada
        raiz = self.arbol_directorios.raiz.dato
        if self.directorio_actual == raiz:
            return self.directorio_actual
        
        # Comparar la ruta actual con la ruta de la raíz
        ruta_actual = self.directorio_actual.ruta_completa.replace('\\', '/')
        ruta_raiz = raiz.ruta_completa.replace('\\', '/')
        
        # Si ya estamos en la raíz (por ruta)
        if ruta_actual == ruta_raiz:
            return self.directorio_actual
        
        # Separar la ruta en partes
        partes = [p for p in ruta_actual.split('/') if p]
        
        # Si tenemos 2 o menos partes (ej: ['D:', 'hola']), el padre es la raíz
        if len(partes) <= 2:
            return raiz
        
        # Construir ruta del padre (sin el último elemento)
        # Ejemplo: ['D:', 'hola', 'prueba'] -> 'D:/hola'
        ruta_padre = partes[0] + '/' + '/'.join(partes[1:-1])
        
        # Buscar la carpeta padre
        carpeta_padre = self._encontrar_carpeta_por_ruta(ruta_padre)
        
        # Si no se encontró el padre, retornar la raíz
        if carpeta_padre is None:
            return raiz
        
        return carpeta_padre
    
    def _navegar_ruta_absoluta(self, ruta):
        """Navega a una ruta absoluta"""
        ruta_limpia = ruta.replace(f"{self.nombre}:", '').replace('\\', '/').strip('/')
        ruta_completa = f"{self.nombre}:/{ruta_limpia}" if ruta_limpia else f"{self.nombre}:/"
        return self._encontrar_carpeta_por_ruta(ruta_completa)
    
    def _navegar_ruta_relativa(self, ruta):
        """Navega a una ruta relativa"""
        carpeta = self.directorio_actual.buscar_carpeta(ruta)
        if carpeta:
            return carpeta
        return None  # Retorna None si la carpeta no existe
    
    def _encontrar_carpeta_por_ruta(self, ruta):
        """Encuentra una carpeta por su ruta completa"""
        # Normalizar la ruta
        ruta_normalizada = ruta.replace('\\', '/')
        
        # Si es la raíz
        if ruta_normalizada == f"{self.nombre}:/" or ruta_normalizada == f"{self.nombre}:":
            return self.arbol_directorios.raiz.dato
        
        # Remover el prefijo de unidad y separar en partes
        ruta_sin_unidad = ruta_normalizada.replace(f"{self.nombre}:/", '').replace(f"{self.nombre}:", '')
        partes = [p for p in ruta_sin_unidad.split('/') if p]
        
        if not partes:
            return self.arbol_directorios.raiz.dato
        
        # Navegar desde la raíz siguiendo las partes
        actual = self.arbol_directorios.raiz.dato
        
        for i, parte in enumerate(partes):
            encontrado = None
            # Buscar en los hijos del nodo actual
            for hijo in actual.nodo_arbol.hijos:
                if hijo.dato.nombre == parte:
                    encontrado = hijo.dato
                    break
            
            if encontrado is None:
                # No se encontró la carpeta, retornar None
                return None
            
            actual = encontrado
        
        return actual
    
    def crear_carpeta(self, nombre, ruta_destino=None):
        """Crea una nueva carpeta"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        
        if destino.buscar_carpeta(nombre):
            raise ValueError(f"La carpeta '{nombre}' ya existe en este directorio")
        
        nueva_carpeta = Carpeta(nombre, destino.ruta_completa)
        destino.agregar_subcarpeta(nueva_carpeta)
        return nueva_carpeta
    
    def crear_archivo(self, nombre, contenido="", ruta_destino=None):
        """Crea un nuevo archivo"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        
        if destino.buscar_archivo(nombre):
            raise ValueError(f"El archivo '{nombre}' ya existe en este directorio")
        
        nuevo_archivo = Archivo(nombre, contenido)
        destino.agregar_archivo(nuevo_archivo)
        return nuevo_archivo
    
    def eliminar_carpeta(self, nombre, ruta_destino=None):
        """Elimina una carpeta y su contenido"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        return destino.eliminar_carpeta(nombre)
    
    def listar_contenido(self, ruta_destino=None, modo='normal'):
        """Lista el contenido de un directorio"""
        destino = ruta_destino if ruta_destino else self.directorio_actual
        
        contenido = []
        contenido.extend(destino.listar_subcarpetas())
        
        if modo == 'preorden':
            contenido.extend(destino.listar_archivos_preorden())
        elif modo == 'postorden':
            contenido.extend(destino.listar_archivos_postorden())
        elif modo == 'inorden':
            contenido.extend(destino.listar_archivos())
        else:
            contenido.extend(destino.listar_archivos())
        
        return contenido
    
    def buscar_directorio_postorden(self, nombre_parcial):
        """Busca directorios que contengan nombre_parcial (recorrido postorden)"""
        resultados = []
        self._buscar_directorio_postorden_rec(self.arbol_directorios.raiz, nombre_parcial, resultados)
        return resultados
    
    def _buscar_directorio_postorden_rec(self, nodo, nombre_parcial, resultados):
        """Recorrido postorden para buscar directorios"""
        if not nodo:
            return
        
        for hijo in nodo.hijos:
            self._buscar_directorio_postorden_rec(hijo, nombre_parcial, resultados)
        
        if nombre_parcial.lower() in nodo.dato.nombre.lower():
            resultados.append(nodo.dato)
    
    def obtener_todos_archivos(self):
        """Obtiene todos los archivos de la unidad"""
        archivos = []
        self._obtener_archivos_rec(self.arbol_directorios.raiz, archivos)
        return archivos
    
    def _obtener_archivos_rec(self, nodo, archivos):
        """Recorre el árbol para obtener todos los archivos"""
        if not nodo:
            return
        
        archivos.extend(nodo.dato.listar_archivos())
        
        for hijo in nodo.hijos:
            self._obtener_archivos_rec(hijo, archivos)
    
    def to_dict(self):
        """Convierte la unidad a diccionario para serialización"""
        return {
            'nombre': self.nombre,
            'directorio_actual': self.directorio_actual.ruta_completa if self.directorio_actual else "",
            'estructura': self.arbol_directorios.raiz.dato.to_dict() if self.arbol_directorios.raiz else {}
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una unidad desde diccionario"""
        unidad = cls(data['nombre'])
        
        if data['estructura']:
            # Cargar la carpeta raíz desde el diccionario
            carpeta_raiz = Carpeta.from_dict(data['estructura'])
            # Usar el nodo_arbol de la carpeta cargada como raíz del árbol
            # Esto asegura que las subcarpetas estén correctamente conectadas
            unidad.arbol_directorios.raiz = carpeta_raiz.nodo_arbol
            unidad.directorio_actual = carpeta_raiz
        
        if data['directorio_actual']:
            carpeta_encontrada = unidad._encontrar_carpeta_por_ruta(data['directorio_actual'])
            if carpeta_encontrada:
                unidad.directorio_actual = carpeta_encontrada
        
        return unidad
