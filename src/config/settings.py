import os
import json
from typing import Dict, Any, Tuple
from pathlib import Path

class ConfigManager:
    """Gerenciador de configurações da aplicação"""
    
    def __init__(self, config_dir: str = 'data'):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Garante que o diretório de configuração existe"""
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(self, destination_folder: str, download_format: str, 
                   audio_quality: str, video_quality: str = '1080') -> None:
        """Salva as configurações no arquivo JSON"""
        config_data = {
            'destination_folder': destination_folder,
            'download_format': download_format,
            'audio_quality': audio_quality,
            'video_quality': video_quality,
            'last_updated': str(Path().cwd())
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def load_config(self) -> Tuple[str, str, str, str]:
        """Carrega as configurações do arquivo JSON"""
        defaults = ('', 'mp3', '192 kbps', '1080')
        
        if not self.config_file.exists():
            return defaults
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return (
                    config.get('destination_folder', defaults[0]),
                    config.get('download_format', defaults[1]),
                    config.get('audio_quality', defaults[2]),
                    config.get('video_quality', defaults[3])
                )
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return defaults
    
    def get_downloads_folder(self) -> str:
        """Retorna a pasta padrão de downloads do sistema"""
        home = Path.home()
        downloads_folder = home / "Downloads"
        return str(downloads_folder) if downloads_folder.exists() else str(home)

# Configurações da aplicação
APP_CONFIG = {
    'window_title': 'YT 4K Downloader v2',
    'window_size': (500, 550),
    'window_position': (100, 100),
    'icon_path': 'src/assets/4kicon.ico',
    'supported_formats': ['mp3', 'mp4'],
    'audio_qualities': ['128 kbps', '192 kbps', '256 kbps', '320 kbps'],
    'video_qualities': ['720', '1080', '1440', '2160'],
    'theme': {
        'bg_primary': '#1a1625',
        'bg_secondary': '#2f2b3a',
        'bg_accent': '#46424f',
        'accent_color': '#6200EE',
        'accent_hover': '#3700B3',
        'text_color': '#FFFFFF',
        'border_color': '#666'
    }
}