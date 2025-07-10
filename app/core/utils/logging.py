import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
import functools

def setup_logging(app, log_level=logging.INFO, max_bytes=10485760, backup_count=10):
    """
    Configura el sistema de logging para la aplicación Flask
    
    Args:
        app: Instancia de la aplicación Flask
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Tamaño máximo del archivo de log antes de rotar (default 10MB)
        backup_count: Número de archivos de backup a mantener
    """
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar el formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configurar el logger de la aplicación
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Handler de errores separado
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_handler)