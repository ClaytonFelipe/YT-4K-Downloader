from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFileDialog, QComboBox, 
                               QProgressBar, QMessageBox, QGridLayout, QTextEdit,
                               QGroupBox, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path

from config.settings import ConfigManager, APP_CONFIG
from gui.components.download_thread import DownloadThread

class MainWindow(QWidget):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.download_thread = None
        self.init_ui()
        self.load_saved_config()
    
    def init_ui(self) -> None:
        """Inicializa a interface do usuário"""
        self.setup_window()
        self.setup_layout()
        self.apply_styles()
        self.connect_signals()
    
    def setup_window(self) -> None:
        """Configura propriedades da janela"""
        config = APP_CONFIG
        self.setWindowTitle(config['window_title'])
        self.setGeometry(*config['window_position'], *config['window_size'])
        self.setMinimumSize(480, 400)
        
        # Define ícone se existir
        icon_path = Path(config['icon_path'])
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def setup_layout(self) -> None:
        """Configura o layout da interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Seção de entrada de URL
        url_group = self.create_url_section()
        main_layout.addWidget(url_group)
        
        # Seção de configurações
        config_group = self.create_config_section()
        main_layout.addWidget(config_group)
        
        # Seção de progresso
        progress_group = self.create_progress_section()
        main_layout.addWidget(progress_group)
        
        # Botões de ação
        buttons_layout = self.create_action_buttons()
        main_layout.addLayout(buttons_layout)
        
        # Área de informações do vídeo
        info_group = self.create_info_section()
        main_layout.addWidget(info_group)
        
        self.setLayout(main_layout)
    
    def create_url_section(self) -> QGroupBox:
        """Cria seção de entrada de URL"""
        group = QGroupBox("Vídeo")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("URL do YouTube:"))
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Cole aqui o link do vídeo do YouTube...")
        layout.addWidget(self.url_entry)
        
        group.setLayout(layout)
        return group
    
    def create_config_section(self) -> QGroupBox:
        """Cria seção de configurações"""
        group = QGroupBox("Configurações")
        layout = QGridLayout()
        
        # Pasta de destino
        layout.addWidget(QLabel("Pasta de Destino:"), 0, 0)
        self.destination_folder_var = QLineEdit()
        layout.addWidget(self.destination_folder_var, 0, 1)
        
        select_button = QPushButton("📁 Selecionar")
        select_button.clicked.connect(self.select_destination_folder)
        layout.addWidget(select_button, 0, 2)
        
        # Formato
        layout.addWidget(QLabel("Formato:"), 1, 0)
        self.format_var = QComboBox()
        self.format_var.addItems(APP_CONFIG['supported_formats'])
        layout.addWidget(self.format_var, 1, 1, 1, 2)
        
        # Qualidade do áudio
        self.audio_quality_label = QLabel("Qualidade do Áudio:")
        layout.addWidget(self.audio_quality_label, 2, 0)
        self.audio_quality_var = QComboBox()
        self.audio_quality_var.addItems(APP_CONFIG['audio_qualities'])
        layout.addWidget(self.audio_quality_var, 2, 1, 1, 2)
        
        # Qualidade do vídeo
        self.video_quality_label = QLabel("Qualidade do Vídeo:")
        layout.addWidget(self.video_quality_label, 3, 0)
        self.video_quality_var = QComboBox()
        self.video_quality_var.addItems(APP_CONFIG['video_qualities'])
        layout.addWidget(self.video_quality_var, 3, 1, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_progress_section(self) -> QGroupBox:
        """Cria seção de progresso"""
        group = QGroupBox("Progresso")
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Pronto para download")
        layout.addWidget(self.status_label)
        
        group.setLayout(layout)
        return group
    
    def create_action_buttons(self) -> QHBoxLayout:
        """Cria botões de ação"""
        layout = QHBoxLayout()
        
        self.download_button = QPushButton("⬇️ Baixar")
        self.download_button.setMinimumHeight(35)
        layout.addWidget(self.download_button)
        
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)
        
        return layout
    
    def create_info_section(self) -> QGroupBox:
        """Cria seção de informações do vídeo"""
        group = QGroupBox("Informações do Vídeo")
        layout = QVBoxLayout()
        
        self.video_info_text = QTextEdit()
        self.video_info_text.setMaximumHeight(100)
        self.video_info_text.setReadOnly(True)
        self.video_info_text.setVisible(False)
        layout.addWidget(self.video_info_text)
        
        group.setLayout(layout)
        return group
    
    def connect_signals(self) -> None:
        """Conecta sinais dos componentes"""
        self.format_var.currentTextChanged.connect(self.on_format_change)
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.cancel_download)
        
        # Auto-completar pasta de destino
        if not self.destination_folder_var.text():
            self.destination_folder_var.setText(
                self.config_manager.get_downloads_folder()
            )
    
    def apply_styles(self) -> None:
        """Aplica estilos da aplicação"""
        theme = APP_CONFIG['theme']
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['bg_primary']};
                color: {theme['text_color']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme['border_color']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            QLineEdit {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border_color']};
                padding: 8px;
                border-radius: 6px;
                font-size: 11px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {theme['accent_color']};
            }}
            
            QPushButton {{
                background-color: {theme['accent_color']};
                color: {theme['text_color']};
                font-weight: bold;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 11px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: #2A0080;
            }}
            
            QPushButton:disabled {{
                background-color: {theme['bg_accent']};
                color: #888;
            }}
            
            QComboBox {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border_color']};
                padding: 8px;
                border-radius: 6px;
                font-size: 11px;
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            
            QProgressBar {{
                background-color: {theme['bg_accent']};
                border: none;
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['accent_color']};
                border-radius: 6px;
            }}
            
            QTextEdit {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border_color']};
                border-radius: 6px;
                padding: 5px;
                font-size: 10px;
            }}
            
            QLabel {{
                font-weight: 500;
                font-size: 11px;
            }}
        """)
    
    def load_saved_config(self) -> None:
        """Carrega configurações salvas"""
        destination, format_type, audio_quality, video_quality = self.config_manager.load_config()
        
        if destination:
            self.destination_folder_var.setText(destination)
        
        self.format_var.setCurrentText(format_type)
        self.audio_quality_var.setCurrentText(audio_quality)
        self.video_quality_var.setCurrentText(video_quality)
        self.on_format_change(format_type)
    
    def on_format_change(self, format_type: str) -> None:
        """Atualiza interface baseado no formato selecionado"""
        is_audio = format_type == 'mp3'
        
        self.audio_quality_label.setVisible(is_audio)
        self.audio_quality_var.setVisible(is_audio)
        self.video_quality_label.setVisible(not is_audio)
        self.video_quality_var.setVisible(not is_audio)
    
    def select_destination_folder(self) -> None:
        """Abre diálogo para seleção de pasta"""
        current_folder = self.destination_folder_var.text()
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Destino", current_folder
        )
        if folder:
            self.destination_folder_var.setText(folder)
    
    def start_download(self) -> None:
        """Inicia o processo de download"""
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Aviso", "Por favor, insira a URL do vídeo.")
            return
        
        destination = self.destination_folder_var.text().strip()
        if not destination:
            QMessageBox.warning(self, "Aviso", "Por favor, escolha a pasta de destino.")
            return
        
        # Salva configurações
        self.config_manager.save_config(
            destination,
            self.format_var.currentText(),
            self.audio_quality_var.currentText(),
            self.video_quality_var.currentText()
        )
        
        # Configura UI para download
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Inicia thread de download
        self.download_thread = DownloadThread(
            url, destination,
            self.format_var.currentText(),
            self.audio_quality_var.currentText(),
            self.video_quality_var.currentText()
        )
        
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.status.connect(self.update_status)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.video_info.connect(self.display_video_info)
        
        self.download_thread.start()
    
    def cancel_download(self) -> None:
        """Cancela o download atual"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.download_finished(False, "Download cancelado pelo usuário")
    
    def update_progress(self, percent: int) -> None:
        """Atualiza barra de progresso"""
        self.progress_bar.setValue(percent)
    
    def update_status(self, status: str) -> None:
        """Atualiza label de status"""
        self.status_label.setText(status)
    
    def display_video_info(self, info: dict) -> None:
        """Exibe informações do vídeo"""
        info_text = f"""
Título: {info.get('title', 'N/A')}
Canal: {info.get('uploader', 'N/A')}
Duração: {self.format_duration(info.get('duration', 0))}
Visualizações: {info.get('view_count', 0):,}
        """.strip()
        
        self.video_info_text.setText(info_text)
        self.video_info_text.setVisible(True)
    
    def format_duration(self, seconds: int) -> str:
        """Formata duração em segundos para formato legível"""
        if seconds <= 0:
            return "N/A"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def download_finished(self, success: bool, message: str) -> None:
        """Finaliza processo de download"""
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "Sucesso", message)
            self.progress_bar.setValue(100)
        else:
            QMessageBox.critical(self, "Erro", message)
            self.progress_bar.setValue(0)
        
        # Esconde barra de progresso
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))
        
        self.update_status("Pronto para novo download")