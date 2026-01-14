"""
Módulo de configuración del sistema
"""
import json
import os
from datetime import datetime

API_KEY = "HLzNt2nUV9UCHPp8IM30awSBIkbDi9WNuv88xLZQ"

class Configuracion:
    """Maneja la configuración del sistema y backups"""
    def __init__(self, archivo_config="config.json"):
        self.archivo_config = archivo_config
        self.config = self._cargar_configuracion()
        self._crear_directorio_backups()
    
    def _cargar_configuracion(self):
        """Carga la configuración desde archivo o crea una por defecto"""
        config_default = {
            "backup_dir": "backups",
            "backup_automatico": True,
            "formato_backup": "json",
            "comandos_habilitados": {
                "cd": True,
                "mkdir": True,
                "rmdir": True,
                "type": True,
                "dir": True,
                "log": True,
                "clear": True
            },
            "api_key_cohere": API_KEY # "RsR6jdXJrR6xkRHuUcxOO9MieuYnKVbUQDOh2San"
        }
        
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self._guardar_configuracion(config_default)
                return config_default
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return config_default
    
    def _guardar_configuracion(self, config):
        """Guarda la configuración en archivo"""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def _crear_directorio_backups(self):
        """Crea el directorio de backups si no existe"""
        backup_dir = self.config['backup_dir']
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def generar_nombre_backup(self):
        """Genera un nombre único para el backup"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        formato = self.config['formato_backup']
        return f"{self.config['backup_dir']}/backup_{timestamp}.{formato}"
    
    def hacer_backup(self, datos):
        """Realiza un backup de los datos"""
        if not self.config['backup_automatico']:
            return None
        
        archivo_backup = self.generar_nombre_backup()
        
        try:
            with open(archivo_backup, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return archivo_backup
        except Exception as e:
            print(f"Error haciendo backup: {e}")
            return None
    
    def cargar_ultimo_backup(self):
        """Carga el último backup disponible"""
        backup_dir = self.config['backup_dir']
        if not os.path.exists(backup_dir):
            return None
        
        archivos = [f for f in os.listdir(backup_dir) if f.startswith('backup_')]
        if not archivos:
            return None
        
        archivos.sort(reverse=True)
        ultimo_backup = os.path.join(backup_dir, archivos[0])
        
        try:
            with open(ultimo_backup, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando backup: {e}")
            return None
    
    def comando_habilitado(self, comando):
        """Verifica si un comando está habilitado"""
        return self.config['comandos_habilitados'].get(comando, False)
    
    def actualizar_configuracion(self, nueva_config):
        """Actualiza la configuración"""
        self.config.update(nueva_config)
        self._guardar_configuracion(self.config)