"""
Archivo principal del Sistema de Consola Inteligente con Chatbot de IA
modificado para múltiples unidades y árboles
"""
import os
import json
from sistema import SistemaArchivos, UnidadAlmacenamiento, ListaUnidades
from logger import Logger
from configuracion import Configuracion
from chatbot import ChatbotIA
from comandos import FabricaComandos
from indice_global import IndiceGlobal
from arboles import BTree


class SistemaConsola:
    """Clase principal que orquesta todo el sistema"""
    
    def __init__(self):
        self.config = Configuracion()
        self.sistema_archivos = SistemaArchivos()
        self.logger = Logger()
        self.chatbot = ChatbotIA(self.config.config['api_key_cohere'])
        self.indice_global = IndiceGlobal()
        self._inicializar_indice_global()
        self.sistema_archivos.actualizar_indice_global(self.indice_global)
        self.cargar_datos_iniciales()
    
    def _inicializar_indice_global(self):
        """Inicializa y carga el índice global"""
        if not self.indice_global.cargar_indice():
            print("Índice global: Creando nuevo índice...")
            # Construir índice inicial con archivos existentes
            self._construir_indice_inicial()
    
    def _construir_indice_inicial(self):
        """Construye índice inicial con archivos del sistema"""
        todos_archivos = self.sistema_archivos.obtener_todos_archivos()
        
        for archivo in todos_archivos:
            # Necesitamos obtener la ruta completa del archivo
            # Esto sería más complejo en implementación real
            pass
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales o desde backup"""
        # Intentar cargar desde backup
        datos_backup = self.config.cargar_ultimo_backup()
        if datos_backup:
            try:
                self.sistema_archivos.cargar_estructura(datos_backup)
                self.logger.registrar_operacion("Sistema", "Datos cargados desde backup")
                print("Sistema: Datos cargados desde backup existente")
                
                # Reconstruir índice global después de cargar datos
                self._reconstruir_indice_global()
                
            except Exception as e:
                print(f"Error cargando backup: {e}. Iniciando con datos por defecto.")
                self._crear_datos_por_defecto()
        else:
            self._crear_datos_por_defecto()
    
    def _reconstruir_indice_global(self):
        """Reconstruye el índice global con todos los archivos"""
        print("Índice global: Reconstruyendo índice...")
        self.indice_global = IndiceGlobal()
        
        # Obtener todos los archivos del sistema
        todos_archivos = self.sistema_archivos.obtener_todos_archivos()
        
        # Esto es simplificado - en realidad necesitaríamos las rutas completas
        print(f"Índice global: {len(todos_archivos)} archivos para indexar")
        
        # Guardar índice vacío por ahora
        self.indice_global.guardar_indice()
    
    def _crear_datos_por_defecto(self):
        """Crea una estructura de datos por defecto para pruebas"""
        try:
            unidad_actual = self.sistema_archivos.obtener_unidad_actual()
            
            # Crear algunas carpetas y archivos de ejemplo en C:
            documentos = unidad_actual.crear_carpeta("Documentos")
            proyectos = unidad_actual.crear_carpeta("Proyectos", documentos)
            fotos = unidad_actual.crear_carpeta("Fotos", documentos)
            
            # Navegar a Documentos
            unidad_actual.directorio_actual = documentos
            
            # Crear archivos
            unidad_actual.crear_archivo("Notas", "Notas importantes aquí", documentos)
            unidad_actual.crear_archivo("Tareas", "Lista de tareas pendientes", documentos)
            unidad_actual.crear_archivo("Idea", "Ideas para el proyecto", proyectos)
            unidad_actual.crear_archivo("Plan", "Plan de desarrollo", proyectos)
            unidad_actual.crear_archivo("test1", "Archivo de prueba 1", documentos)
            unidad_actual.crear_archivo("test2", "Archivo de prueba 2 más grande", documentos)
            unidad_actual.crear_archivo("notas_clase", "Notas de clase importantes", documentos)
            
            # Volver a raíz
            unidad_actual.directorio_actual = unidad_actual.arbol_directorios.raiz.dato
            
            # Crear algunas carpetas en D:
            self.sistema_archivos.cambiar_unidad("D:")
            unidad_d = self.sistema_archivos.obtener_unidad_actual()
            backup_d = unidad_d.crear_carpeta("Backup")
            unidad_d.crear_archivo("respaldo1", "Respaldo antiguo", backup_d)
            
            # Volver a C:
            self.sistema_archivos.cambiar_unidad("C:")
            
            self.logger.registrar_operacion("Sistema", "Datos por defecto creados")
            print("Sistema: Estructura por defecto creada para pruebas")
            print("Unidades disponibles: C:, D:, F:")
            
            # Hacer backup inicial
            estructura = self.sistema_archivos.obtener_estructura_completa()
            self.config.hacer_backup(estructura)
            
        except Exception as e:
            print(f"Error creando datos por defecto: {e}")
    
    def procesar_comando_directo(self, comando):
        """Procesa un comando directo de consola"""
        try:
            partes = comando.split(' ', 1)
            comando_base = partes[0].lower()
            argumentos = partes[1] if len(partes) > 1 else None
            
            comando_obj = FabricaComandos.crear_comando(comando_base)
            resultado = comando_obj.ejecutar(
                self.sistema_archivos, 
                self.logger, 
                self.config, 
                self.indice_global,
                argumentos
            )
            
            # Guardar índice global si se modificó
            if comando_base in ['type', 'rmdir']:
                self.indice_global.guardar_indice()
            
            return resultado
            
        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            self.logger.registrar_error(comando, str(e))
            return f"Error ejecutando comando: {e}"
    
    def procesar_lenguaje_natural(self, texto):
        """Procesa lenguaje natural usando el chatbot IA"""
        print(f"Usuario: {texto}")
        
        # Primero intentar interpretar como comando
        comando_generado = self.chatbot.interpretar_comando(texto)
        
        if comando_generado:
            print(f"Chatbot IA: Comando generado: {comando_generado}")
            resultado = self.procesar_comando_directo(comando_generado)
            respuesta_amigable = self.chatbot.generar_respuesta_amigable(comando_generado, resultado)
            print(f"Chatbot IA: {respuesta_amigable}")
            return resultado
        else:
            # Si no es comando, conversación normal
            return "No entendí tu solicitud. ¿Podrías reformularla como un comando de sistema de archivos?"
    
    def mostrar_prompt(self):
        """Muestra el prompt del sistema"""
        unidad_actual = self.sistema_archivos.obtener_unidad_actual()
        if unidad_actual and unidad_actual.directorio_actual:
            directorio_actual = unidad_actual.directorio_actual.ruta_completa
        else:
            directorio_actual = "Desconocido"
        return f"{directorio_actual}> "
    
    def ejecutar(self):
        """Bucle principal de ejecución del sistema"""
        print("=" * 70)
        print("SISTEMA DE CONSOLA INTELIGENTE CON CHATBOT DE IA")
        print("Estructuras: Lista enlazada (unidades), Árbol N-ario (directorios),")
        print("             Árbol Binario (archivos), Árbol B (índice global)")
        print("=" * 70)
        print("Comandos disponibles: cd, mkdir, rmdir, type, dir, log, clear log, index")
        print("Argumentos especiales:")
        print("  dir search <texto> - Buscar directorios (postorden)")
        print("  dir search -file <nombre> - Buscar archivos (preorden)")
        print("  dir search -file <nombre> -range <min-max> - Buscar con rango (inorden)")
        print("  index search <texto> - Buscar en índice global")
        print("  index search -range <min-max> - Buscar por tamaño")
        print("  index search -file <nombre> -range <min-max> - Búsqueda combinada")
        print("También puedes usar lenguaje natural (español)")
        print("Escribe 'salir' para terminar\n")
        
        # Mostrar estadísticas iniciales
        stats = self.indice_global.obtener_estadisticas()
        print(f"Índice global: {stats['total_archivos']} archivos indexados\n")
        
        while True:
            try:
                entrada = input(self.mostrar_prompt()).strip()
                
                if entrada.lower() in ['salir', 'exit', 'quit']:
                    # Guardar índice global antes de salir
                    self.indice_global.guardar_indice()
                    print("¡Hasta luego!")
                    break
                
                if not entrada:
                    continue
                
                # Determinar si es comando directo o lenguaje natural
                if any(entrada.lower().startswith(cmd) for cmd in 
                      ['cd ', 'mkdir ', 'rmdir ', 'type ', 'dir', 'log', 'clear', 'index']):
                    # Es un comando directo
                    resultado = self.procesar_comando_directo(entrada)
                    print(resultado)
                else:
                    # Es lenguaje natural
                    resultado = self.procesar_lenguaje_natural(entrada)
                    if "No entendí" in resultado:
                        print(resultado)
                
                print()  # Línea en blanco para separar
                
            except KeyboardInterrupt:
                print("\n\nInterrupción del usuario. Saliendo...")
                # Guardar índice global antes de salir
                self.indice_global.guardar_indice()
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                self.logger.registrar_error("Sistema", f"Error inesperado: {e}")

def main():
    """Función principal"""
    try:
        sistema = SistemaConsola()
        sistema.ejecutar()
    except Exception as e:
        print(f"Error iniciando el sistema: {e}")

if __name__ == "__main__":
    main()