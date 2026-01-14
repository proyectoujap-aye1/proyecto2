"""
Módulo que implementa el comando INDEX para búsquedas en índice global
"""
from .base import Comando


class ComandoINDEX(Comando):
    """Nuevo comando para búsquedas en índice global (Árbol B)"""
    
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
            return False, "Los valores del rango deben ser positivos (>= 0)"
        
        if min_val > max_val:
            return False, f"Error: El valor mínimo ({min_val}) no puede ser mayor que el máximo ({max_val})"
        
        return True, (min_val, max_val)
    
    def ejecutar(self, sistema, logger, config, indice_global, argumentos=None):
        try:
            if not config.comando_habilitado('index'):
                return "Error: Comando INDEX deshabilitado"
            
            if not indice_global:
                return "Error: Índice global no inicializado"
            
            if not argumentos:
                return "Uso: index search <texto>\n" + \
                       "       index search -file <nombre>\n" + \
                       "       index search -range <min>-<max>\n" + \
                       "       index search -file <nombre> -range <min>-<max>"
            
            if not argumentos.lower().startswith('search'):
                return "Error: Comando INDEX solo soporta 'search'"
            
            return self._procesar_busqueda(argumentos, indice_global, logger)
            
        except Exception as e:
            logger.registrar_error(f"index {argumentos}", str(e))
            return f"Error en búsqueda de índice: {e}"
    
    def _procesar_busqueda(self, argumentos, indice, logger):
        """Procesa diferentes tipos de búsqueda en el índice"""
        partes = argumentos.split()
        
        # index search <texto>
        if len(partes) == 2:
            texto = partes[1]
            resultados = indice.buscar_parcial(texto)
            logger.registrar_operacion(f"index search {texto}", f"Búsqueda parcial: {len(resultados)} resultados")
            return indice.mostrar_resultados(resultados)
        
        # index search -file <nombre>
        if '-file' in partes and '-range' not in partes:
            idx_file = partes.index('-file')
            if len(partes) > idx_file + 1:
                nombre = partes[idx_file + 1]
                resultados = indice.buscar_parcial(nombre)
                logger.registrar_operacion(f"index search -file {nombre}", f"Búsqueda archivos: {len(resultados)} resultados")
                return indice.mostrar_resultados(resultados)
            else:
                return "Error: -file requiere un nombre de archivo"
        
        # index search -range <min>-<max>
        if '-range' in partes and '-file' not in partes:
            idx_range = partes.index('-range')
            if len(partes) > idx_range + 1:
                rango = partes[idx_range + 1]
                
                # Validar rango
                valido, resultado_validacion = self._validar_rango(rango)
                if not valido:
                    return f"Error en rango: {resultado_validacion}"
                
                min_kb, max_kb = resultado_validacion
                resultados = indice.buscar_por_rango_tamanio(min_kb, max_kb)
                logger.registrar_operacion(f"index search -range {rango}", f"Búsqueda rango: {len(resultados)} resultados")
                return indice.mostrar_resultados(resultados)
            else:
                return "Error: -range requiere un valor en formato min-max (ej: 0-100)"
        
        # index search -file <nombre> -range <min>-<max>
        if '-file' in partes and '-range' in partes:
            idx_file = partes.index('-file')
            idx_range = partes.index('-range')
            
            if len(partes) > idx_file + 1 and len(partes) > idx_range + 1:
                nombre = partes[idx_file + 1]
                rango = partes[idx_range + 1]
                
                # Validar rango
                valido, resultado_validacion = self._validar_rango(rango)
                if not valido:
                    return f"Error en rango: {resultado_validacion}"
                
                min_kb, max_kb = resultado_validacion
                resultados = indice.buscar_combinada(nombre, min_kb, max_kb)
                logger.registrar_operacion(f"index search -file {nombre} -range {rango}", 
                                         f"Búsqueda combinada: {len(resultados)} resultados")
                return indice.mostrar_resultados(resultados)
            else:
                if len(partes) <= idx_file + 1:
                    return "Error: -file requiere un nombre de archivo"
                else:
                    return "Error: -range requiere un valor en formato min-max (ej: 0-100)"
        
        return "Formato de búsqueda no válido. Use:\n" + \
               "index search texto\n" + \
               "index search -file nombre\n" + \
               "index search -range min-max\n" + \
               "index search -file nombre -range min-max"

