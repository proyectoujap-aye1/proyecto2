"""
Módulo que implementa el comando DIR para listar contenido y búsquedas
"""
from .base import Comando


class ComandoDIR(Comando):
    """Implementación del comando DIR con búsquedas avanzadas"""
    
    def validar(self, argumentos=None):
        return True, "OK"
    
    def _validar_rango(self, rango_str):
        """Valida el formato del rango y que los valores sean correctos"""
        if '-' not in rango_str:
            return False, "El rango debe tener formato min-max (ej: 0-100)"
        
        partes = rango_str.split('-')
        if len(partes) != 2:
            return False, "El rango debe tener exactamente un guión: min-max"
        
        try:
            min_val = float(partes[0])
            max_val = float(partes[1])
        except ValueError:
            return False, "Los valores del rango deben ser números válidos"
        
        if min_val < 0 or max_val < 0:
            return False, "Los valores del rango deben ser positivos"
        
        if min_val > max_val:
            return False, f"Error: El valor mínimo ({min_val}) no puede ser mayor que el máximo ({max_val})"
        
        return True, (min_val, max_val)
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('dir'):
                return "Error: Comando DIR deshabilitado"
            
            unidad_actual = sistema.obtener_unidad_actual()
            directorio_actual = unidad_actual.directorio_actual
            
            # Procesar argumentos
            if not argumentos:
                contenido = unidad_actual.listar_contenido()
                return self._formatear_simple(contenido, directorio_actual.ruta_completa)
            
            argumentos_lower = argumentos.lower()
            
            # DIR SEARCH
            if argumentos_lower.startswith('search'):
                return self._procesar_search(argumentos, unidad_actual, directorio_actual)
            
            # DIR con ruta específica
            if '/' in argumentos or '\\' in argumentos:
                destino = unidad_actual.navegar_a_ruta(argumentos)
                if destino is None or destino == directorio_actual:
                    # La ruta no existe
                    return f"Error: La ruta '{argumentos}' no existe en la unidad actual"
                contenido = unidad_actual.listar_contenido(destino)
                return self._formatear_simple(contenido, destino.ruta_completa)
            
            # DIR con nombre de carpeta
            carpeta_destino = directorio_actual.buscar_carpeta(argumentos)
            if carpeta_destino:
                contenido = unidad_actual.listar_contenido(carpeta_destino)
                return self._formatear_simple(contenido, carpeta_destino.ruta_completa)
            
            # DIR normal (si no coincide con nada)
            contenido = unidad_actual.listar_contenido()
            return self._formatear_simple(contenido, directorio_actual.ruta_completa)
            
        except Exception as e:
            logger.registrar_error(f"dir {argumentos}", str(e))
            return f"Error listando directorio: {e}"
    
    def _formatear_simple(self, contenido, ruta):
        """Formatea salida simple de DIR"""
        resultado = f"Directorio de {ruta}\n"
        resultado += "-" * 50 + "\n"
        
        carpetas = []
        archivos = []
        
        for elemento in contenido:
            if "CARPETA" in str(elemento):
                carpetas.append(elemento)
            else:
                archivos.append(elemento)
        
        for carpeta in carpetas:
            resultado += f"{carpeta}\n"
        
        for archivo in archivos:
            resultado += f"{archivo}\n"
        
        resultado += f"\nTotal: {len(carpetas)} carpetas, {len(archivos)} archivos\n"
        
        return resultado
    
    def _procesar_search(self, argumentos, unidad, directorio):
        """Procesa búsquedas con DIR SEARCH"""
        partes = argumentos.split()
        
        # DIR SEARCH parcial
        if len(partes) == 2:
            texto = partes[1]
            resultados = unidad.buscar_directorio_postorden(texto)
            
            if not resultados:
                return f"No se encontraron directorios que contengan '{texto}'"
            
            salida = f"Resultados de búsqueda postorden para '{texto}':\n"
            salida += "-" * 50 + "\n"
            
            for i, resultado in enumerate(resultados, 1):
                salida += f"{i}. {resultado.ruta_completa}\n"
                contenido = unidad.listar_contenido(resultado, modo='postorden')
                for elemento in contenido:
                    salida += f"   - {elemento}\n"
            
            return salida
        
        # DIR SEARCH -file
        if '-file' in partes:
            idx_file = partes.index('-file')
            
            if len(partes) > idx_file + 1:
                nombre_archivo = partes[idx_file + 1]
                
                # DIR SEARCH -file -range
                if '-range' in partes:
                    idx_range = partes.index('-range')
                    
                    if len(partes) > idx_range + 1:
                        rango = partes[idx_range + 1]
                        
                        # Validar rango
                        valido, resultado_validacion = self._validar_rango(rango)
                        if not valido:
                            return f"Error en rango: {resultado_validacion}"
                        
                        min_kb, max_kb = resultado_validacion
                        
                        resultados = directorio.buscar_archivos_parcial(nombre_archivo)
                        resultados_filtrados = []
                        
                        for archivo in resultados:
                            if min_kb <= archivo.tamanio_kb <= max_kb:
                                resultados_filtrados.append(archivo)
                        
                        return self._formatear_busqueda_combinada(resultados_filtrados, nombre_archivo, min_kb, max_kb)
                    else:
                        return "Error: -range requiere un valor en formato min-max (ej: 0-100)"
                
                # DIR SEARCH -file simple (preorden)
                resultados = directorio.buscar_archivos_parcial(nombre_archivo)
                return self._formatear_busqueda_archivos(resultados, nombre_archivo, 'preorden')
            else:
                return "Error: -file requiere un nombre de archivo"
        
        return "Formato de búsqueda no válido. Use: dir search texto\n" + \
               "dir search -file nombre\n" + \
               "dir search -file nombre -range min-max"
    
    def _formatear_busqueda_archivos(self, archivos, criterio, modo):
        """Formatea resultados de búsqueda de archivos"""
        if not archivos:
            return f"No se encontraron archivos que contengan '{criterio}' (búsqueda {modo})"
        
        salida = f"Resultados de búsqueda {modo} para '{criterio}':\n"
        salida += "-" * 50 + "\n"
        
        for i, archivo in enumerate(archivos, 1):
            salida += f"{i}. {archivo.nombre}.{archivo.extension} ({archivo.tamanio_kb:.2f} KB)\n"
            salida += f"   Ruta: {archivo.tamanio_kb:.2f} KB, Creado: {archivo.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        salida += f"\nTotal encontrados: {len(archivos)} archivos\n"
        return salida
    
    def _formatear_busqueda_combinada(self, archivos, nombre, min_kb, max_kb):
        """Formatea resultados de búsqueda combinada"""
        if not archivos:
            return f"No se encontraron archivos que contengan '{nombre}' con tamaño entre {min_kb} y {max_kb} KB"
        
        salida = f"Resultados de búsqueda inorden para '{nombre}' (tamaño {min_kb}-{max_kb} KB):\n"
        salida += "-" * 50 + "\n"
        
        for i, archivo in enumerate(archivos, 1):
            salida += f"{i}. {archivo.nombre}.{archivo.extension} ({archivo.tamanio_kb:.2f} KB)\n"
        
        salida += f"\nTotal encontrados: {len(archivos)} archivos\n"
        return salida

