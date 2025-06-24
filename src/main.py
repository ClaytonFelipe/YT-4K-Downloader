"""
YT 4K Downloader v2
Aplicação para download de vídeos e áudios do YouTube
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow

def setup_application():
    """Configura a aplicação"""
    app = QApplication(sys.argv)
    app.setApplicationName("YT Downloader 4K")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YT Downloader")
    
    return app

def main():
    """Função principal da aplicação"""
    try:
        app = setup_application()
        
        # Cria e exibe a janela principal
        window = MainWindow()
        window.show()
        
        # Executa a aplicação
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Certifique-se de que todas as dependências estão instaladas:")
        print("pip install PySide6 yt-dlp")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()