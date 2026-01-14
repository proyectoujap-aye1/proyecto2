"""
Módulo que define el Árbol Binario de Búsqueda para archivos
"""

class NodoArbolBinario:
    """Nodo para árbol binario de archivos"""
    def __init__(self, archivo):
        self.archivo = archivo
        self.nombre = archivo.nombre.lower()
        self.izquierda = None
        self.derecha = None
        self.tamanio_kb = len(archivo.contenido.encode('utf-8')) / 1024
    
    def __str__(self):
        return f"{self.nombre} ({self.tamanio_kb:.2f} KB)"


class ArbolBinarioBusqueda:
    """Árbol binario de búsqueda para archivos"""
    def __init__(self):
        self.raiz = None
    
    def insertar(self, archivo):
        """Inserta un archivo en el árbol"""
        nuevo_nodo = NodoArbolBinario(archivo)
        
        if not self.raiz:
            self.raiz = nuevo_nodo
            return
        
        actual = self.raiz
        while True:
            if nuevo_nodo.nombre < actual.nombre:
                if actual.izquierda is None:
                    actual.izquierda = nuevo_nodo
                    break
                actual = actual.izquierda
            else:
                if actual.derecha is None:
                    actual.derecha = nuevo_nodo
                    break
                actual = actual.derecha
    
    def buscar(self, nombre):
        """Busca un archivo por nombre"""
        nombre = nombre.lower()
        actual = self.raiz
        
        while actual:
            if nombre == actual.nombre:
                return actual.archivo
            elif nombre < actual.nombre:
                actual = actual.izquierda
            else:
                actual = actual.derecha
        
        return None
    
    def eliminar(self, nombre):
        """Elimina un archivo por nombre del árbol"""
        nombre = nombre.lower()
        self.raiz, eliminado = self._eliminar_rec(self.raiz, nombre)
        return eliminado
    
    def _eliminar_rec(self, nodo, nombre):
        """Eliminación recursiva en el árbol binario"""
        if nodo is None:
            return None, False
        
        if nombre < nodo.nombre:
            nodo.izquierda, eliminado = self._eliminar_rec(nodo.izquierda, nombre)
            return nodo, eliminado
        elif nombre > nodo.nombre:
            nodo.derecha, eliminado = self._eliminar_rec(nodo.derecha, nombre)
            return nodo, eliminado
        else:
            # Nodo encontrado
            if nodo.izquierda is None:
                return nodo.derecha, True
            elif nodo.derecha is None:
                return nodo.izquierda, True
            else:
                # Nodo con dos hijos: obtener el sucesor inorden
                sucesor = self._minimo(nodo.derecha)
                nodo.nombre = sucesor.nombre
                nodo.archivo = sucesor.archivo
                nodo.tamanio_kb = sucesor.tamanio_kb
                nodo.derecha, _ = self._eliminar_rec(nodo.derecha, sucesor.nombre)
                return nodo, True
    
    def _minimo(self, nodo):
        """Encuentra el nodo mínimo en un subárbol"""
        actual = nodo
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual

    
    def buscar_parcial(self, texto):
        """Busca archivos que contengan texto en su nombre"""
        resultados = []
        self._buscar_parcial_rec(self.raiz, texto.lower(), resultados)
        return resultados
    
    def _buscar_parcial_rec(self, nodo, texto, resultados):
        """Recursivo para búsqueda parcial"""
        if nodo is None:
            return
        
        if texto in nodo.nombre:
            resultados.append(nodo.archivo)
        
        self._buscar_parcial_rec(nodo.izquierda, texto, resultados)
        self._buscar_parcial_rec(nodo.derecha, texto, resultados)
    
    def buscar_por_rango_tamanio(self, min_kb, max_kb):
        """Busca archivos por rango de tamaño (inorden)"""
        resultados = []
        self._buscar_rango_inorden(self.raiz, min_kb, max_kb, resultados)
        return resultados
    
    def _buscar_rango_inorden(self, nodo, min_kb, max_kb, resultados):
        """Recorrido inorden con filtro por rango"""
        if nodo is None:
            return
        
        self._buscar_rango_inorden(nodo.izquierda, min_kb, max_kb, resultados)
        
        if min_kb <= nodo.tamanio_kb <= max_kb:
            resultados.append(nodo.archivo)
        
        self._buscar_rango_inorden(nodo.derecha, min_kb, max_kb, resultados)
    
    def recorrer_inorden(self, nodo=None, es_llamada_inicial=True):
        """Recorrido inorden del árbol"""
        if es_llamada_inicial and nodo is None:
            nodo = self.raiz
            if nodo is None:
                return []
        
        resultado = []
        if nodo:
            resultado.extend(self.recorrer_inorden(nodo.izquierda, False))
            resultado.append(nodo.archivo)
            resultado.extend(self.recorrer_inorden(nodo.derecha, False))
        
        return resultado
    
    def recorrer_preorden(self, nodo=None, es_llamada_inicial=True):
        """Recorrido preorden del árbol"""
        if es_llamada_inicial and nodo is None:
            nodo = self.raiz
            if nodo is None:
                return []
        
        resultado = []
        if nodo:
            resultado.append(nodo.archivo)
            resultado.extend(self.recorrer_preorden(nodo.izquierda, False))
            resultado.extend(self.recorrer_preorden(nodo.derecha, False))
        
        return resultado
    
    def recorrer_postorden(self, nodo=None, es_llamada_inicial=True):
        """Recorrido postorden del árbol"""
        if es_llamada_inicial and nodo is None:
            nodo = self.raiz
            if nodo is None:
                return []
        
        resultado = []
        if nodo:
            resultado.extend(self.recorrer_postorden(nodo.izquierda, False))
            resultado.extend(self.recorrer_postorden(nodo.derecha, False))
            resultado.append(nodo.archivo)
        
        return resultado
