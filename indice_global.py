"""
Módulo para el índice global usando Árbol B
"""
import json
from datetime import datetime
from arboles import BTree

class IndiceGlobal:
    """Índice global de archivos usando Árbol B"""
    
    def __init__(self, t=3):
        self.arbol_b = BTree(t)
        self.archivo_indice = "indice_global.json"
    
    def insertar_archivo(self, archivo, ruta_completa):
        """Inserta un archivo en el índice global"""
        clave = f"{ruta_completa}/{archivo.nombre}.{archivo.extension}"
        valor = {
            'nombre': archivo.nombre,
            'extension': archivo.extension,
            'ruta_completa': f"{ruta_completa}/{archivo.nombre}.{archivo.extension}",
            'tamanio_kb': archivo.tamanio_kb,
            'fecha_creacion': archivo.fecha_creacion.isoformat(),
            'fecha_modificacion': archivo.fecha_modificacion.isoformat(),
            'contenido_preview': archivo.contenido[:100] if archivo.contenido else ""  # Preview de contenido
        }
        
        self.arbol_b.insertar(clave, valor)
    
    def eliminar_archivo(self, ruta_completa):
        """Elimina un archivo del índice global"""
        return self.arbol_b.eliminar(ruta_completa)
    
    def buscar_por_nombre(self, nombre):
        """Busca archivos por nombre exacto"""
        # Buscar en todas las claves que terminen con el nombre
        resultados = []
        self._buscar_por_nombre_rec(self.arbol_b.raiz, nombre, resultados)
        return resultados
    
    def _buscar_por_nombre_rec(self, nodo, nombre, resultados):
        """Búsqueda recursiva por nombre"""
        if not nodo:
            return
        
        for i, clave in enumerate(nodo.claves):
            if clave.endswith(f"/{nombre}"):
                resultados.append(nodo.valores[i])
        
        if not nodo.hoja:
            for hijo in nodo.hijos:
                self._buscar_por_nombre_rec(hijo, nombre, resultados)
    
    def buscar_parcial(self, texto):
        """Busca archivos que contengan texto en nombre o ruta"""
        return self.arbol_b.buscar_parcial(texto)
    
    def buscar_por_rango_tamanio(self, min_kb, max_kb):
        """Busca archivos por rango de tamaño"""
        return self.arbol_b.buscar_por_rango(min_kb, max_kb, 'tamanio')
    
    def buscar_combinada(self, texto, min_kb=None, max_kb=None):
        """Búsqueda combinada por texto y rango de tamaño"""
        resultados_texto = self.buscar_parcial(texto)
        
        if min_kb is None and max_kb is None:
            return resultados_texto
        
        resultados_filtrados = []
        for resultado in resultados_texto:
            tamanio = resultado['tamanio_kb']
            if (min_kb is None or tamanio >= min_kb) and (max_kb is None or tamanio <= max_kb):
                resultados_filtrados.append(resultado)
        
        return resultados_filtrados
    
    def mostrar_resultados(self, resultados):
        """Muestra resultados de búsqueda de forma formateada"""
        if not resultados:
            return "No se encontraron resultados."
        
        salida = f"Resultados encontrados en índice global ({len(resultados)}):\n"
        for i, resultado in enumerate(resultados, 1):
            salida += f"{i}. {resultado['ruta_completa']} ({resultado['tamanio_kb']:.2f} KB)\n"
        
        return salida
    
    def guardar_indice(self, archivo=None):
        """Guarda el índice en un archivo"""
        archivo = archivo or self.archivo_indice
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(self.arbol_b.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando índice: {e}")
            return False
    
    def cargar_indice(self, archivo=None):
        """Carga el índice desde un archivo"""
        archivo = archivo or self.archivo_indice
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data:
                self.arbol_b = BTree.from_dict(data)
                return True
        except FileNotFoundError:
            print(f"Archivo de índice no encontrado, se creará uno nuevo.")
        except Exception as e:
            print(f"Error cargando índice: {e}")
        
        return False
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del índice"""
        if not self.arbol_b.raiz:
            return {"total_archivos": 0}
        
        total = self._contar_archivos(self.arbol_b.raiz)
        return {"total_archivos": total}
    
    def _contar_archivos(self, nodo):
        """Cuenta archivos en el árbol B"""
        if not nodo:
            return 0
        
        total = len(nodo.claves)
        
        if not nodo.hoja:
            for hijo in nodo.hijos:
                total += self._contar_archivos(hijo)
        
        return total
    
    def actualizar_archivo(self, ruta_vieja, archivo_nuevo, ruta_nueva):
        """Actualiza un archivo en el índice (para renombrado)"""
        # Eliminar la entrada vieja
        eliminado = self.eliminar_archivo(ruta_vieja)
        
        if eliminado:
            # Insertar la nueva entrada
            self.insertar_archivo(archivo_nuevo, ruta_nueva)
            return True
        
        return False