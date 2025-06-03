
import logging
import os
import sys

def setup_logging(dir_path, file_name_log):
    log_dir = os.path.join(dir_path, 'log')
    log_filename = os.path.join(log_dir, file_name_log)
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Cria um handler para o arquivo de log
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)

    # Cria um handler para o console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR) # Apenas erros para o console

    # Define o formato das mensagens de log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
    