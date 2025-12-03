"""
Módulo que define las estructuras de datos: Pila y Cola
Implementadas con listas enlazadas para el sistema de archivos
"""

class Nodo:
    """Nodo para listas enlazadas"""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class Pila:
    """Implementación de Pila (LIFO) para logs y operaciones"""
    def __init__(self):
        self.tope = None
        self.tamanio = 0
    
    def apilar(self, dato):
        """Apila un elemento en la pila"""
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.siguiente = self.tope
        self.tope = nuevo_nodo
        self.tamanio += 1
    
    def desapilar(self):
        """Desapila y retorna el elemento del tope"""
        if self.tope is None:
            return None
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.tamanio -= 1
        return dato
    
    def esta_vacia(self):
        """Verifica si la pila está vacía"""
        return self.tope is None
    
    def ver_tope(self):
        """Muestra el elemento del tope sin desapilar"""
        return self.tope.dato if self.tope else None
    
    def obtener_todos(self):
        """Retorna todos los elementos de la pila como lista (LIFO)"""
        elementos = []
        actual = self.tope
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos
    
    def vaciar(self):
        """Vacía completamente la pila"""
        self.tope = None
        self.tamanio = 0

class Cola:
    """Implementación de Cola (FIFO) para archivos y carpetas"""
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamanio = 0
    
    def encolar(self, dato):
        """Encola un elemento"""
        nuevo_nodo = Nodo(dato)
        if self.final is None:
            self.frente = self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self.tamanio += 1
    
    def desencolar(self):
        """Desencola y retorna el elemento del frente"""
        if self.frente is None:
            return None
        
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        
        if self.frente is None:
            self.final = None
        
        self.tamanio -= 1
        return dato
    
    def esta_vacia(self):
        """Verifica si la cola está vacía"""
        return self.frente is None
    
    def ver_frente(self):
        """Muestra el elemento del frente sin desencolar"""
        return self.frente.dato if self.frente else None
    
    def obtener_todos(self):
        """Retorna todos los elementos de la cola como lista (FIFO)"""
        elementos = []
        actual = self.frente
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos