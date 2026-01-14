"""
Módulo que define el gestor principal del sistema de archivos
"""
from .unidad import UnidadAlmacenamiento


class NodoUnidad:
    """Nodo para lista enlazada de unidades"""
    def __init__(self, unidad):
        self.unidad = unidad
        self.siguiente = None


class ListaUnidades:
    """Lista enlazada para múltiples unidades de almacenamiento"""
    def __init__(self):
        self.cabeza = None
        self.unidad_actual = None
    
    def agregar_unidad(self, unidad):
        """Agrega una unidad a la lista"""
        nuevo_nodo = NodoUnidad(unidad)
        
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            self.unidad_actual = unidad
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
    
    def obtener_unidad(self, nombre):
        """Obtiene una unidad por nombre"""
        actual = self.cabeza
        while actual:
            if actual.unidad.nombre == nombre:
                return actual.unidad
            actual = actual.siguiente
        return None
    
    def cambiar_unidad_actual(self, nombre):
        """Cambia la unidad actual"""
        unidad = self.obtener_unidad(nombre)
        if unidad:
            self.unidad_actual = unidad
            return True
        return False
    
    def listar_unidades(self):
        """Lista todas las unidades"""
        unidades = []
        actual = self.cabeza
        while actual:
            unidades.append(actual.unidad)
            actual = actual.siguiente
        return unidades
    
    def to_dict(self):
        """Convierte la lista de unidades a diccionario"""
        unidades_dict = []
        actual = self.cabeza
        while actual:
            unidades_dict.append(actual.unidad.to_dict())
            actual = actual.siguiente
        
        return {
            'unidades': unidades_dict,
            'unidad_actual': self.unidad_actual.nombre if self.unidad_actual else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea lista de unidades desde diccionario"""
        lista = cls()
        
        for unidad_data in data['unidades']:
            unidad = UnidadAlmacenamiento.from_dict(unidad_data)
            lista.agregar_unidad(unidad)
        
        if data['unidad_actual']:
            lista.cambiar_unidad_actual(data['unidad_actual'])
        
        return lista


class SistemaArchivos:
    """Clase principal del sistema de archivos con múltiples unidades"""
    def __init__(self):
        self.unidades = ListaUnidades()
        self.indice_global = None
        self._inicializar_unidades_predeterminadas()
    
    def _inicializar_unidades_predeterminadas(self):
        """Inicializa unidades predeterminadas C:, D:, F:"""
        for unidad_nombre in ["C:", "D:", "F:"]:
            unidad = UnidadAlmacenamiento(unidad_nombre)
            self.unidades.agregar_unidad(unidad)
    
    def obtener_unidad_actual(self):
        """Obtiene la unidad actual"""
        return self.unidades.unidad_actual
    
    def cambiar_unidad(self, nombre_unidad):
        """Cambia la unidad actual"""
        return self.unidades.cambiar_unidad_actual(nombre_unidad)
    
    def obtener_todos_archivos(self):
        """Obtiene todos los archivos de todas las unidades"""
        todos_archivos = []
        actual = self.unidades.cabeza
        while actual:
            todos_archivos.extend(actual.unidad.obtener_todos_archivos())
            actual = actual.siguiente
        return todos_archivos
    
    def actualizar_indice_global(self, indice):
        """Actualiza el índice global del sistema"""
        self.indice_global = indice
    
    def obtener_estructura_completa(self):
        """Obtiene toda la estructura del sistema para backup"""
        return self.unidades.to_dict()
    
    def cargar_estructura(self, data):
        """Carga la estructura del sistema desde backup"""
        self.unidades = ListaUnidades.from_dict(data)
