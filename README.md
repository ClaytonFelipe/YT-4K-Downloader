
<p align="center">
  <img src="screenshots/YT4kicon.png" alt="icone" width="300"/>
</p>

<h1 align="center">YT 4K Downloader v2</h1>

![version](https://badge.ttsalpha.com/api?label=version&status=2.0&color=4BB543)
![made_by](https://badge.ttsalpha.com/api?label=made_by&status=Clayton_Felipe&color=42ba96)
![Python](https://badge.ttsalpha.com/api?icon=python&label=Python&status=3.10.6&color=3776AB)



<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
</p>

## 📝  Estrutura de Pastas 
```
yt-downloader-4k/
├── src/
│   ├── main.py                     # Ponto de entrada da aplicação
│   │
│   ├── gui/                        # Interface gráfica
│   │   ├── main_window.py          # Janela principal
│   │   └── components/             # Componentes da GUI
│   │       └── download_thread.py  # Thread de download
│   │
│   ├── core/                       # Lógica principal
│   │   └── downloader.py           # Motor de download
│   │
│   │
│   ├── config/                     # Configurações
│   │   └── settings.py             # Gerenciamento de configurações
│   │
│   └── assets/                     # Recursos estáticos
│       └── 4kicon.ico              # Ícone da aplicação
│
├── data/                           # Dados da aplicação
│   └── config.json                 # Configurações salvas
│
├── requirements.txt                # Dependências
├── README.md                       # Documentação
└── 
```

![screenshot](screenshots/window_screenshot.png)

## 🔧 Implementações

###  **Arquitetura Modular**
- **Separação de responsabilidades**: Cada módulo tem uma função específica
- **Baixo acoplamento**: Módulos independentes e reutilizáveis
- **Alta coesão**: Funcionalidades relacionadas agrupadas

### **Interface**
- **Organização visual**: Agrupamento lógico de elementos
- **Responsividade**: Interface adaptável a diferentes tamanhos
- **Feedback visual**: Indicadores de progresso e status

### **Funcionalidades**
- **Validação de URL**: Verifica se a URL é válida antes do download
- **Informações do vídeo**: Exibe dados como título, canal e duração
- **Cancelamento de download**: Possibilidade de interromper downloads
- **Pasta padrão inteligente**: Auto-seleciona pasta Downloads do sistema
- **Tratamento de erros robusto**: Captura e exibe erros de forma amigável

### **Implementações Técnicas**
- **Threading aprimorado**: Download não bloqueia a interface
- **Gestão de memória**: Melhor uso de recursos do sistema
- **Configurações persistentes**: Salva todas as preferências do usuário
- **Sanitização de nomes**: Remove caracteres inválidos dos arquivos
- **Logs estruturados**: Sistema de logging para debugging

### **Experiência do Usuário UX**
- **Interface intuitiva**: Layout claro e funcional
- **Feedback em tempo real**: Progresso detalhado com velocidade e tamanho
- **Configurações lembradas**: Mantém últimas configurações usadas
- **Mensagens informativas**: Avisos e confirmações claras

## Como utilizar

### Instalação
```bash
# Clone o projeto
git clone <repo-url>
cd yt-4k-downloader

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python src/main.py
```

### 👷 Adicionando Novas Funcionalidades

#### Para adicionar um novo serviço:
1. Crie arquivo em `src/services/`
2. Implemente a lógica do serviço
3. Importe onde necessário

#### Para modificar a interface:
1. Edite `src/gui/main_window.py`
2. Adicione componentes em `src/gui/components/`
3. Mantenha estilos em `config/settings.py`

#### Para alterar configurações:
1. Modifique `src/config/settings.py`
2. Atualize `APP_CONFIG` para novas opções
3. Adicione validações no `ConfigManager`


