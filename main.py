"""
Archivo principal del Sistema de Consola Inteligente con Chatbot de IA
"""
import os
import json
from sistema_archivos import SistemaArchivos, Carpeta, Archivo
from logger import Logger
from configuracion import Configuracion
from chatbot import ChatbotIA
from comandos import FabricaComandos

class SistemaConsola:
    """Clase principal que orquesta todo el sistema"""
    
    def __init__(self):
        self.config = Configuracion()
        self.sistema_archivos = SistemaArchivos()
        self.logger = Logger()
        self.chatbot = ChatbotIA(self.config.config['api_key_cohere'])
        self.cargar_datos_iniciales()
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales o desde backup"""
        # Intentar cargar desde backup
        datos_backup = self.config.cargar_ultimo_backup()
        if datos_backup:
            try:
                self.sistema_archivos.cargar_estructura(datos_backup)
                self.logger.registrar_operacion("Sistema", "Datos cargados desde backup")
                print("Sistema: Datos cargados desde backup existente")
            except Exception as e:
                print(f"Error cargando backup: {e}. Iniciando con datos por defecto.")
                self._crear_datos_por_defecto()
        else:
            self._crear_datos_por_defecto()
    
    def _crear_datos_por_defecto(self):
        """Crea una estructura de datos por defecto para pruebas"""
        try:
            # Crear algunas carpetas y archivos de ejemplo
            documentos = self.sistema_archivos.crear_carpeta("Documentos")
            proyectos = self.sistema_archivos.crear_carpeta("Proyectos", documentos)
            fotos = self.sistema_archivos.crear_carpeta("Fotos", documentos)
            
            self.sistema_archivos.crear_archivo("Notas", "Notas importantes aquí", documentos)
            self.sistema_archivos.crear_archivo("Tareas", "Lista de tareas pendientes", documentos)
            self.sistema_archivos.crear_archivo("Idea", "Ideas para el proyecto", proyectos)
            self.sistema_archivos.crear_archivo("Plan", "Plan de desarrollo", proyectos)
            
            self.logger.registrar_operacion("Sistema", "Datos por defecto creados")
            print("Sistema: Estructura por defecto creada para pruebas")
            
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
                argumentos
            )
            
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
        directorio_actual = self.sistema_archivos.directorio_actual.ruta_completa
        return f"{directorio_actual}> "
    
    def ejecutar(self):
        """Bucle principal de ejecución del sistema"""
        print("=" * 60)
        print("SISTEMA DE CONSOLA INTELIGENTE CON CHATBOT DE IA")
        print("=" * 60)
        print("Comandos disponibles: cd, mkdir, rmdir, type, dir, log, clear log")
        print("También puedes usar lenguaje natural (español)")
        print("Escribe 'salir' para terminar\n")
        
        while True:
            try:
                entrada = input(self.mostrar_prompt()).strip()
                
                if entrada.lower() in ['salir', 'exit', 'quit']:
                    print("¡Hasta luego!")
                    break
                
                if not entrada:
                    continue
                
                # Determinar si es comando directo o lenguaje natural
                if any(entrada.lower().startswith(cmd) for cmd in 
                      ['cd ', 'mkdir ', 'rmdir ', 'type ', 'dir', 'log', 'clear']):
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