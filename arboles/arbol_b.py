"""
Módulo que define el Árbol B (B-Tree) para índice global de archivos
"""

class NodoBTree:
    """Nodo para Árbol B (B-Tree)"""
    def __init__(self, t, hoja=True):
        self.t = t  # Grado mínimo
        self.hoja = hoja
        self.claves = []  # Lista de claves (nombres de archivos)
        self.valores = []  # Lista de valores (metadatos)
        self.hijos = []  # Lista de hijos
    
    def __str__(self):
        return f"NodoBTree(hoja={self.hoja}, claves={self.claves})"


class BTree:
    """Árbol B para índice global de archivos"""
    def __init__(self, t=3):
        self.raiz = None
        self.t = t  # Grado mínimo
    
    def insertar(self, clave, valor):
        """Inserta una clave-valor en el árbol B"""
        if not self.raiz:
            self.raiz = NodoBTree(self.t, True)
            self.raiz.claves.append(clave)
            self.raiz.valores.append(valor)
        else:
            if len(self.raiz.claves) == (2 * self.t - 1):
                nueva_raiz = NodoBTree(self.t, False)
                nueva_raiz.hijos.append(self.raiz)
                self._dividir_hijo(nueva_raiz, 0)
                self.raiz = nueva_raiz
            
            self._insertar_no_lleno(self.raiz, clave, valor)
    
    def _insertar_no_lleno(self, nodo, clave, valor):
        """Inserta en un nodo no lleno"""
        i = len(nodo.claves) - 1
        
        if nodo.hoja:
            while i >= 0 and clave < nodo.claves[i]:
                i -= 1
            
            nodo.claves.insert(i + 1, clave)
            nodo.valores.insert(i + 1, valor)
        else:
            while i >= 0 and clave < nodo.claves[i]:
                i -= 1
            
            i += 1
            
            if len(nodo.hijos[i].claves) == (2 * self.t - 1):
                self._dividir_hijo(nodo, i)
                if clave > nodo.claves[i]:
                    i += 1
            
            self._insertar_no_lleno(nodo.hijos[i], clave, valor)
    
    def _dividir_hijo(self, padre, i):
        """Divide un hijo lleno"""
        t = self.t
        hijo = padre.hijos[i]
        nuevo_hijo = NodoBTree(t, hijo.hoja)
        
        padre.claves.insert(i, hijo.claves[t - 1])
        padre.valores.insert(i, hijo.valores[t - 1])
        
        nuevo_hijo.claves = hijo.claves[t:(2 * t - 1)]
        nuevo_hijo.valores = hijo.valores[t:(2 * t - 1)]
        hijo.claves = hijo.claves[0:(t - 1)]
        hijo.valores = hijo.valores[0:(t - 1)]
        
        if not hijo.hoja:
            nuevo_hijo.hijos = hijo.hijos[t:(2 * t)]
            hijo.hijos = hijo.hijos[0:t]
        
        padre.hijos.insert(i + 1, nuevo_hijo)
    
    def buscar(self, clave):
        """Busca una clave en el árbol B"""
        return self._buscar_rec(self.raiz, clave) if self.raiz else None
    
    def _buscar_rec(self, nodo, clave):
        """Búsqueda recursiva en el árbol B"""
        if not nodo:
            return None
        
        i = 0
        while i < len(nodo.claves) and clave > nodo.claves[i]:
            i += 1
        
        if i < len(nodo.claves) and clave == nodo.claves[i]:
            return nodo.valores[i]
        
        if nodo.hoja:
            return None
        
        return self._buscar_rec(nodo.hijos[i], clave)
    
    def buscar_parcial(self, texto):
        """Busca claves que contengan texto"""
        resultados = []
        if self.raiz:
            self._buscar_parcial_rec(self.raiz, texto.lower(), resultados)
        return resultados
    
    def _buscar_parcial_rec(self, nodo, texto, resultados):
        """Búsqueda parcial recursiva"""
        for i, clave in enumerate(nodo.claves):
            if texto in clave.lower():
                resultados.append(nodo.valores[i])
        
        if not nodo.hoja:
            for hijo in nodo.hijos:
                self._buscar_parcial_rec(hijo, texto, resultados)
    
    def buscar_por_rango(self, min_valor, max_valor, campo='tamanio'):
        """Busca por rango de valores"""
        resultados = []
        if self.raiz:
            self._buscar_rango_rec(self.raiz, min_valor, max_valor, campo, resultados)
        return resultados
    
    def _buscar_rango_rec(self, nodo, min_valor, max_valor, campo, resultados):
        """Búsqueda por rango recursiva"""
        for i, valor in enumerate(nodo.valores):
            if campo == 'tamanio' and min_valor <= valor['tamanio_kb'] <= max_valor:
                resultados.append(valor)
            elif campo == 'fecha':
                pass
        
        if not nodo.hoja:
            for hijo in nodo.hijos:
                self._buscar_rango_rec(hijo, min_valor, max_valor, campo, resultados)
    
    def eliminar(self, clave):
        """Elimina una clave del árbol B"""
        if not self.raiz:
            return False
        
        self._eliminar_rec(self.raiz, clave)
        
        if len(self.raiz.claves) == 0:
            if self.raiz.hoja:
                self.raiz = None
            else:
                self.raiz = self.raiz.hijos[0]
        
        return True
    
    def _eliminar_rec(self, nodo, clave):
        """Eliminación recursiva"""
        idx = self._encontrar_clave(nodo, clave)
        
        if idx < len(nodo.claves) and nodo.claves[idx] == clave:
            if nodo.hoja:
                self._eliminar_de_hoja(nodo, idx)
            else:
                self._eliminar_de_no_hoja(nodo, idx)
        else:
            if nodo.hoja:
                return False
            
            ultimo = (idx == len(nodo.claves))
            
            if len(nodo.hijos[idx].claves) < self.t:
                self._llenar(nodo, idx)
            
            if ultimo and idx > len(nodo.claves):
                self._eliminar_rec(nodo.hijos[idx - 1], clave)
            else:
                self._eliminar_rec(nodo.hijos[idx], clave)
        
        return True
    
    def _encontrar_clave(self, nodo, clave):
        """Encuentra el índice de una clave"""
        idx = 0
        while idx < len(nodo.claves) and nodo.claves[idx] < clave:
            idx += 1
        return idx
    
    def _eliminar_de_hoja(self, nodo, idx):
        """Elimina clave de nodo hoja"""
        del nodo.claves[idx]
        del nodo.valores[idx]
    
    def _eliminar_de_no_hoja(self, nodo, idx):
        """Elimina clave de nodo no hoja"""
        clave = nodo.claves[idx]
        
        if len(nodo.hijos[idx].claves) >= self.t:
            predecesor = self._obtener_predecesor(nodo, idx)
            nodo.claves[idx] = predecesor['clave']
            nodo.valores[idx] = predecesor['valor']
            self._eliminar_rec(nodo.hijos[idx], predecesor['clave'])
        elif len(nodo.hijos[idx + 1].claves) >= self.t:
            sucesor = self._obtener_sucesor(nodo, idx)
            nodo.claves[idx] = sucesor['clave']
            nodo.valores[idx] = sucesor['valor']
            self._eliminar_rec(nodo.hijos[idx + 1], sucesor['clave'])
        else:
            self._fusionar(nodo, idx)
            self._eliminar_rec(nodo.hijos[idx], clave)
    
    def _obtener_predecesor(self, nodo, idx):
        """Obtiene el predecesor de una clave"""
        actual = nodo.hijos[idx]
        while not actual.hoja:
            actual = actual.hijos[-1]
        
        return {
            'clave': actual.claves[-1],
            'valor': actual.valores[-1]
        }
    
    def _obtener_sucesor(self, nodo, idx):
        """Obtiene el sucesor de una clave"""
        actual = nodo.hijos[idx + 1]
        while not actual.hoja:
            actual = actual.hijos[0]
        
        return {
            'clave': actual.claves[0],
            'valor': actual.valores[0]
        }
    
    def _llenar(self, nodo, idx):
        """Llena un hijo que tiene menos de t claves"""
        if idx != 0 and len(nodo.hijos[idx - 1].claves) >= self.t:
            self._pedir_prestado_izquierda(nodo, idx)
        elif idx != len(nodo.claves) and len(nodo.hijos[idx + 1].claves) >= self.t:
            self._pedir_prestado_derecha(nodo, idx)
        else:
            if idx != len(nodo.claves):
                self._fusionar(nodo, idx)
            else:
                self._fusionar(nodo, idx - 1)
    
    def _pedir_prestado_izquierda(self, nodo, idx):
        """Toma prestada una clave del hermano izquierdo"""
        hijo = nodo.hijos[idx]
        hermano = nodo.hijos[idx - 1]
        
        hijo.claves.insert(0, nodo.claves[idx - 1])
        hijo.valores.insert(0, nodo.valores[idx - 1])
        
        if not hijo.hoja:
            hijo.hijos.insert(0, hermano.hijos.pop())
        
        nodo.claves[idx - 1] = hermano.claves.pop()
        nodo.valores[idx - 1] = hermano.valores.pop()
    
    def _pedir_prestado_derecha(self, nodo, idx):
        """Toma prestada una clave del hermano derecho"""
        hijo = nodo.hijos[idx]
        hermano = nodo.hijos[idx + 1]
        
        hijo.claves.append(nodo.claves[idx])
        hijo.valores.append(nodo.valores[idx])
        
        if not hijo.hoja:
            hijo.hijos.append(hermano.hijos.pop(0))
        
        nodo.claves[idx] = hermano.claves.pop(0)
        nodo.valores[idx] = hermano.valores.pop(0)
    
    def _fusionar(self, nodo, idx):
        """Fusiona dos hijos"""
        hijo = nodo.hijos[idx]
        hermano = nodo.hijos[idx + 1]
        
        hijo.claves.append(nodo.claves[idx])
        hijo.valores.append(nodo.valores[idx])
        
        hijo.claves.extend(hermano.claves)
        hijo.valores.extend(hermano.valores)
        
        if not hijo.hoja:
            hijo.hijos.extend(hermano.hijos)
        
        del nodo.claves[idx]
        del nodo.valores[idx]
        del nodo.hijos[idx + 1]
    
    def to_dict(self):
        """Convierte el árbol B a diccionario para serialización"""
        if not self.raiz:
            return {}
        
        return self._nodo_to_dict(self.raiz)
    
    def _nodo_to_dict(self, nodo):
        """Convierte un nodo a diccionario"""
        return {
            't': self.t,
            'hoja': nodo.hoja,
            'claves': nodo.claves,
            'valores': nodo.valores,
            'hijos': [self._nodo_to_dict(h) for h in nodo.hijos] if not nodo.hoja else []
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un árbol B desde diccionario"""
        if not data:
            return cls()
        
        arbol = cls(t=data['t'])
        arbol.raiz = cls._dict_to_nodo(data)
        return arbol
    
    @classmethod
    def _dict_to_nodo(cls, data):
        """Crea un nodo desde diccionario"""
        nodo = NodoBTree(data['t'], data['hoja'])
        nodo.claves = data['claves']
        nodo.valores = data['valores']
        
        if not data['hoja']:
            for hijo_data in data['hijos']:
                nodo.hijos.append(cls._dict_to_nodo(hijo_data))
        
        return nodo
