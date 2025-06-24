import os
import re
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import yt_dlp

class DownloadError(Exception):
    """Exceção customizada para erros de download"""
    pass

class VideoDownloader:
    """Classe responsável pelo download de vídeos/áudios"""
    
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
    
    def set_callbacks(self, progress_callback: Callable = None, 
                     status_callback: Callable = None) -> None:
        """Define callbacks para progresso e status"""
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def validate_url(self, url: str) -> bool:
        """Valida se a URL é do YouTube ou outros sites suportados"""
        youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return bool(re.match(youtube_pattern, url))
    
    def clean_url(self, url: str) -> str:
        """Remove parâmetros de playlist e outros parâmetros desnecessários da URL"""
        # Remove parâmetros de playlist e outros que podem causar problemas
        import urllib.parse as urlparse
        
        parsed = urlparse.urlparse(url)
        query_params = urlparse.parse_qs(parsed.query)
        
        # Mantém apenas parâmetros essenciais
        essential_params = {}
        if 'v' in query_params:  # ID do vídeo
            essential_params['v'] = query_params['v']
        if 't' in query_params:  # Timestamp
            essential_params['t'] = query_params['t']
        
        # Reconstrói a URL sem parâmetros de playlist
        new_query = urlparse.urlencode(essential_params, doseq=True)
        clean_url = urlparse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return clean_url
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove caracteres inválidos do nome do arquivo"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limita o tamanho do nome
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Obtém informações do vídeo sem fazer download"""
        # Limpa a URL antes de processar
        clean_url = self.clean_url(url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            # Configurações para evitar processamento de playlist
            'noplaylist': True,  #  IMPORTANTE: Ignora playlist
            'playlistend': 1,    # Limita a 1 item
            'socket_timeout': 30,  # Timeout para evitar travamentos
            'retries': 3,          # Número de tentativas
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': info.get('formats', [])
                }
        except Exception as e:
            raise DownloadError(f"Erro ao obter informações do vídeo: {str(e)}")
    
    def download(self, url: str, destination_folder: str, 
                download_format: str, audio_quality: str, 
                video_quality: str) -> None:
        """Executa o download do vídeo/áudio"""
        
        if not self.validate_url(url):
            raise DownloadError("URL inválida. Use apenas URLs do YouTube.")
        
        # Limpa a URL para evitar problemas com playlists
        clean_url = self.clean_url(url)
        
        # Garante que a pasta de destino existe
        Path(destination_folder).mkdir(parents=True, exist_ok=True)
        
        # Notifica que está iniciando
        if self.status_callback:
            self.status_callback("Preparando download...")
        
        # Configurações base do yt-dlp
        ydl_opts = self._build_ydl_options(
            destination_folder, download_format, 
            audio_quality, video_quality
        )
        
        try:
            if self.status_callback:
                self.status_callback("Conectando ao YouTube...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.status_callback:
                    self.status_callback("Iniciando download...")
                
                ydl.download([clean_url])  # Usar a URL limpa
            
            if self.status_callback:
                self.status_callback("Download concluído com sucesso!")
                
        except Exception as e:
            error_msg = f"Erro durante o download: {str(e)}"
            if self.status_callback:
                self.status_callback(error_msg)
            raise DownloadError(error_msg)
    
    def _build_ydl_options(self, destination_folder: str, 
                          download_format: str, audio_quality: str, 
                          video_quality: str) -> Dict[str, Any]:
        """Constrói as opções do yt-dlp baseado nos parâmetros"""
        
        # Template de saída com sanitização
        outtmpl = os.path.join(destination_folder, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': outtmpl,
            'progress_hooks': [self._progress_hook],
            'postprocessors': [],
            'writeinfojson': False,
            'writesubtitles': False,
            'extract_flat': True, 
            'no_warnings': True,
            'quiet': False,
            'noprogress': False,
            
            # CONFIGURAÇÕES ANTI-PLAYLIST
            'noplaylist': True,      # Ignora completamente playlists
            'playlistend': 1,        # Limita a 1 item mesmo que seja playlist
            'playliststart': 1,      # Começa do primeiro item
            #'max_downloads': 1,     # Máximo de 1 download
            
            # Otimizações para performance
            'lazy_playlist': True,
            'socket_timeout': 30,    # Timeout para conexões
            'fragment_retries': 3,   # Tentativas para fragmentos
            'retries': 3,            # Tentativas gerais
        }
        
        if download_format == 'mp4':
            # Download de vídeo
            ydl_opts['format'] = f'best[height<={video_quality}][ext=mp4]/best[height<={video_quality}]/best'
            if video_quality in ['720', '1080']:
                ydl_opts['format'] = f'best[height<={video_quality}][ext=mp4]'
        else:
            # Download apenas de áudio
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best'
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality.split()[0],
            })
        
        return ydl_opts
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Hook para capturar progresso do download"""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                percent = int(downloaded_bytes / total_bytes * 100)
                speed = d.get('speed', 0) or 0
                
                if self.progress_callback:
                    self.progress_callback(percent)
                
                if self.status_callback:
                    size_mb = total_bytes / 1024 / 1024
                    speed_mb = speed / 1024 / 1024 if speed > 0 else 0
                    status_msg = f"Baixando: {percent}% - {speed_mb:.1f} MB/s - {size_mb:.1f} MB"
                    self.status_callback(status_msg)
        
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100)
            if self.status_callback:
                self.status_callback("Processando arquivo...")
    
    def is_playlist_url(self, url: str) -> bool:
        """Verifica se a URL contém parâmetros de playlist"""
        return '&list=' in url or '?list=' in url
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID do vídeo da URL do YouTube"""
        import urllib.parse as urlparse
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None