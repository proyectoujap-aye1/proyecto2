"""
Módulo del chatbot IA usando Cohere para interpretar comandos naturales
"""
try:
    import cohere
    _HAS_COHERE = True
except Exception:
    cohere = None
    _HAS_COHERE = False


class ChatbotIA:
    """Chatbot que interpreta lenguaje natural y genera comandos"""
    def __init__(self, api_key):
        # Crear cliente Cohere solo si está disponible
        if _HAS_COHERE and api_key:
            try:
                self.co = cohere.Client(api_key)
            except Exception:
                self.co = None
        else:
            self.co = None
        self.prompt_base = """
        Eres un asistente de sistema de archivos. Analiza el texto del usuario y genera el comando apropiado.
        
        Comandos disponibles:
        - cd [ruta] : Cambiar directorio
        - mkdir [nombre] : Crear carpeta
        - rmdir [nombre] : Eliminar carpeta
        - type [nombre] "[contenido]" : Crear archivo
        - dir [ruta] : Listar contenido
        - log : Mostrar historial
        - clear log : Limpiar historial
        
        Responde SOLO con el comando en el formato exacto requerido.
        Si no es un comando del sistema, responde con "NINGUNO".
        
        Ejemplos:
        Usuario: "Abre la carpeta Documentos" -> cd Documentos
        Usuario: "Crea una carpeta llamada Fotos" -> mkdir Fotos
        Usuario: "Elimina la carpeta Temporal" -> rmdir Temporal
        Usuario: "Lista los archivos" -> dir
        Usuario: "Hola cómo estás?" -> NINGUNO
        """
    
    def interpretar_comando(self, texto_usuario):
        """Interpreta el texto natural y genera comando"""
        try:
            # Si no hay cliente de Cohere disponible, no intentamos llamar a la API
            if not self.co:
                return None

            response = self.co.chat(
                model="command-a-03-2025",
                message=f"Texto: \"{texto_usuario}\"",
                preamble=self.prompt_base,
                temperature=0.1,
            )

            comando = response.text.strip()
            
            # Validar que sea un comando válido
            comandos_validos = ['cd', 'mkdir', 'rmdir', 'type', 'dir', 'log', 'clear log']
            
            if comando.upper() == "NINGUNO":
                return None
            
            # Verificar si el comando generado es válido
            for cmd_valido in comandos_validos:
                if comando.lower().startswith(cmd_valido.lower()):
                    return comando
            
            return None
            
        except Exception as e:
            print(f"Error con Cohere: {e}")
            return None
    
    def generar_respuesta_amigable(self, comando, resultado):
        """Genera una respuesta amigable para el usuario"""
        respuestas = {
            'cd': f"He cambiado al directorio: {resultado}",
            'mkdir': f"Carpeta '{resultado}' creada exitosamente",
            'rmdir': f"Carpeta '{resultado}' eliminada exitosamente",
            'type': f"Archivo '{resultado}' creado correctamente",
            'dir': f"Contenido listado: {len(resultado)} elementos",
            'log': "Historial mostrado",
            'clear log': "Historial limpiado"
        }
        
        comando_base = comando.split()[0] if comando else ''
        return respuestas.get(comando_base, f"Operación completada: {resultado}")