from PySide6.QtCore import QThread, Signal, QTimer
from core.downloader import VideoDownloader, DownloadError

class DownloadThread(QThread):
    """Thread responsável por executar downloads sem bloquear a UI"""
    
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)  # success, message
    video_info = Signal(dict)
    playlist_detected = Signal(str)  # Novo sinal para avisar sobre playlist
    
    def __init__(self, url: str, destination_folder: str, 
                 download_format: str, audio_quality: str, 
                 video_quality: str):
        super().__init__()
        self.url = url
        self.destination_folder = destination_folder
        self.download_format = download_format
        self.audio_quality = audio_quality
        self.video_quality = video_quality
        self.downloader = VideoDownloader()
        self._is_cancelled = False
        
        # Timer para timeout de operações longas
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._handle_timeout)
        self.timeout_timer.setSingleShot(True)
    
    def cancel(self) -> None:
        """Cancela o download atual"""
        self._is_cancelled = True
        self.timeout_timer.stop()
        self.terminate()
        self.wait(3000)  # Espera até 3 segundos para terminar graciosamente
    
    def _handle_timeout(self) -> None:
        """Lida com timeout de operações"""
        self.status.emit("Operação demorou muito, tentando continuar...")
        # Não cancela completamente, apenas avisa
    
    def run(self) -> None:
        """Executa o download em thread separada"""
        try:
            # Configura callbacks
            self.downloader.set_callbacks(
                progress_callback=self.progress.emit,
                status_callback=self.status.emit
            )
            
            if self._is_cancelled:
                return
            
            # Verifica se é URL de playlist e avisa o usuário
            if self.downloader.is_playlist_url(self.url):
                clean_url = self.downloader.clean_url(self.url)
                video_id = self.downloader.extract_video_id(self.url)
                
                if video_id:
                    playlist_msg = (f"Playlist detectada! Baixando apenas o vídeo selecionado.\n"
                                  f"URL original: {self.url}\n"
                                  f"URL limpa: {clean_url}")
                    self.playlist_detected.emit(playlist_msg)
                    self.status.emit("Playlist detectada - baixando apenas vídeo selecionado...")
            
            if self._is_cancelled:
                return
            
            # Obtém informações do vídeo com timeout
            try:
                self.status.emit("Obtendo informações do vídeo...")
                self.timeout_timer.start(15000)  # 15 segundos timeout
                
                info = self.downloader.get_video_info(self.url)
                self.timeout_timer.stop()
                
                if not self._is_cancelled:
                    self.video_info.emit(info)
                    # Mostra informações básicas
                    duration_str = self._format_duration(info.get('duration', 0))
                    info_msg = f"Vídeo: {info.get('title', 'Unknown')} ({duration_str})"
                    self.status.emit(info_msg)
                    
            except DownloadError as e:
                self.timeout_timer.stop()
                # Se falhar ao obter info, continua com o download
                self.status.emit("Prosseguindo com download...")
            
            if self._is_cancelled:
                return
            
            # Executa o download com timeout maior
            self.timeout_timer.start(300000)  # 5 minutos timeout para download
            
            self.downloader.download(
                self.url,
                self.destination_folder,
                self.download_format,
                self.audio_quality,
                self.video_quality
            )
            
            self.timeout_timer.stop()
            
            if not self._is_cancelled:
                self.finished.emit(True, "Download concluído com sucesso!")
            
        except DownloadError as e:
            self.timeout_timer.stop()
            self.finished.emit(False, str(e))
        except Exception as e:
            self.timeout_timer.stop()
            self.finished.emit(False, f"Erro inesperado: {str(e)}")
    
    def _format_duration(self, seconds: int) -> str:
        """Formata duração em segundos para formato legível"""
        if seconds <= 0:
            return "Duração desconhecida"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"