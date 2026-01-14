"""
Módulo que define el Árbol N-ario para estructura de directorios
"""

class NodoArbolNario:
    """Nodo para árbol n-ario de directorios"""
    def __init__(self, dato):
        self.dato = dato
        self.hijos = []
    
    def agregar_hijo(self, hijo):
        """Agrega un hijo al nodo"""
        self.hijos.append(hijo)
    
    def eliminar_hijo(self, hijo):
        """Elimina un hijo del nodo"""
        if hijo in self.hijos:
            self.hijos.remove(hijo)
            return True
        return False
    
    def buscar_hijo_por_nombre(self, nombre):
        """Busca un hijo por nombre"""
        for hijo in self.hijos:
            if hijo.dato.nombre == nombre:
                return hijo
        return None


class ArbolNArio:
    """Árbol n-ario para estructura de directorios"""
    def __init__(self, raiz=None):
        self.raiz = raiz
    
    def agregar_nodo(self, padre, nodo):
        """Agrega un nodo al árbol"""
        if not self.raiz:
            self.raiz = nodo
            return
        
        nodo_padre = self.buscar_nodo(padre)
        if nodo_padre:
            nodo_padre.agregar_hijo(nodo)
    
    def buscar_nodo(self, dato, nodo_actual=None):
        """Busca un nodo en el árbol (BFS)"""
        if nodo_actual is None:
            nodo_actual = self.raiz
        
        if nodo_actual.dato == dato:
            return nodo_actual
        
        for hijo in nodo_actual.hijos:
            resultado = self.buscar_nodo(dato, hijo)
            if resultado:
                return resultado
        
        return None
    
    def recorrer_preorden(self, nodo=None, resultado=None):
        """Recorrido preorden del árbol"""
        if resultado is None:
            resultado = []
        
        if nodo is None:
            nodo = self.raiz
            if nodo is None:
                return resultado
        
        resultado.append(nodo.dato)
        
        for hijo in nodo.hijos:
            self.recorrer_preorden(hijo, resultado)
        
        return resultado
    
    def recorrer_postorden(self, nodo=None, resultado=None):
        """Recorrido postorden del árbol"""
        if resultado is None:
            resultado = []
        
        if nodo is None:
            nodo = self.raiz
            if nodo is None:
                return resultado
        
        for hijo in nodo.hijos:
            self.recorrer_postorden(hijo, resultado)
        
        resultado.append(nodo.dato)
        return resultado
