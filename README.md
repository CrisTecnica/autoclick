# AutoClick — Gravador de Macro para Linux & Windows

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Platform: Linux & Windows](https://img.shields.io/badge/Platform-Linux%20|%20Windows-lightgrey)

**AutoClick** é um aplicativo desktop nativo para gravação e reprodução de macros de mouse e teclado. Desenvolvido com Python e PySide6 (Qt), oferece uma interface moderna em tema escuro, atalhos globais e suporte a loop.

> Design original para Pop!_OS, compatível com qualquer distribuição Linux (X11) e Windows.

---

## Funcionalidades

| Recurso | Descrição |
|---|---|
| **Gravação** | Captura movimento do mouse, cliques (esq/dir/meio), scroll, teclas e combinações (Ctrl, Alt, Shift, Super) |
| **Reprodução** | Executa eventos na sequência original com velocidade ajustável (0.1x a 10x) |
| **Loop** | Reprodução contínua com um clique — pare quando quiser |
| **Atalhos globais** | F9 (gravar), F10 (parar), F11 (reproduzir), F12 / Esc (parar tudo) |
| **Editor de eventos** | Visualize, exclua, duplique, reordene e ajuste atrasos de cada evento |
| **Persistência** | Salve e abra macros em formato JSON |
| **Slider de velocidade** | Ajuste a velocidade da reprodução em tempo real |
| **Tema escuro** | Interface limpa com cores para cada ação |
| **Bandeja do sistema** | Minimize para a bandeja e continue usando os atalhos globais |

---

## Captura de Tela

```
┌────────────────────────────────────────────────────┐
│  AutoClick — Gravador de Macro    [Pop!_OS / Linux] │
├────────────────────────────────────────────────────┤
│                                                    │
│   [🔴 Gravar]   [▶ Reproduzir]   [🔄 Loop]        │
│                                                    │
│   Velocidade de reprodução                         │
│   ──────────────●──────────────                    │
│   0.1x           1.0x           10x                 │
│                                                    │
│   Status: ✅ Pronto  |  Eventos: 0  |  ⏱ 00:00    │
│                                                    │
├────────────────────────────────────────────────────┤
│  F9 → Gravar  F10 → Parar  F11 → Reproduzir       │
│  F12 → Tudo Parar  Esc → Emergência               │
└────────────────────────────────────────────────────┘
```

---

## Instalação

### Linux

#### Método 1: Instalação automática

```bash
git clone https://github.com/CrisTecnica/autoclick.git
cd autoclick
chmod +x install.sh
./install.sh
```

#### Método 2: Manual (pip + venv)

```bash
git clone https://github.com/CrisTecnica/autoclick.git
cd autoclick
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

#### Método 3: A partir do código fonte

```bash
pip install -r requirements.txt
python3 main.py
```

### Windows

#### Método 1: Executável portátil (recomendado)

Baixe o arquivo `AutoClick.exe` na [página de releases](https://github.com/CrisTecnica/autoclick/releases).

#### Método 2: Manual (Python)

```powershell
git clone https://github.com/CrisTecnica/autoclick.git
cd autoclick
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Requisitos

- **Python** 3.10 ou superior
- **PySide6** >= 6.6
- **pynput** >= 1.8

### Linux

- Sistema X11 (funcionalidade limitada em Wayland)
- `python3-venv` (para ambiente virtual)

### Windows

- Windows 10 ou superior
- Nenhuma dependência adicional além do Python

---

## Como Usar

### Gravação

1. Pressione **F9** ou clique em **Gravar**
2. Execute as ações que deseja capturar (movimentos, cliques, teclas)
3. Pressione **F10** ou clique em **Parar Gravação**
4. O editor de eventos será aberto automaticamente

### Reprodução

1. Após gravar ou abrir uma macro, clique em **Reproduzir** ou pressione **F11**
2. Ajuste a velocidade com o slider (0.1x a 10x)
3. Para interromper, pressione **F12** ou **Esc**

### Loop

1. Grave ou carregue uma macro
2. Clique em **Loop** — a reprodução se repetirá infinitamente
3. Clique em **Loop** novamente ou pressione **F12** / **Esc** para parar

### Editor de Eventos

- Abra pelo menu **Editar > Editor de Eventos**
- Exclua, duplique, reordene eventos
- Ajuste atrasos entre eventos selecionados

---

## Estrutura do Projeto

```
autoclick/
├── main.py                        # Ponto de entrada
├── requirements.txt               # Dependências Python
├── LICENSE                        # MIT License
├── README.md                      # Esta documentação
├── install.sh                     # Instalador Linux
├── build_exe.bat                  # Script de build para Windows
├── autoclick.spec                 # PyInstaller spec (Windows)
├── autoclick.desktop              # Lançador .desktop (Linux)
├── autoclick/
│   ├── __init__.py
│   ├── models.py                  # Modelos de dados
│   ├── capture.py                 # Captura global de entrada
│   ├── playback.py                # Reprodução em thread
│   ├── persistence.py             # JSON save/load
│   ├── hotkeys.py                 # Atalhos globais
│   ├── config.py                  # Configurações
│   └── ui/
│       ├── main_window.py         # Janela principal
│       ├── editor_dialog.py       # Editor de eventos
│       └── settings_dialog.py     # Configurações
└── venv/                          # Ambiente virtual (opcional)
```

---

## Compatibilidade

| Sistema | Display Server | Status |
|---|---|---|
| Pop!_OS 22.04+ | X11 | ✅ Completo |
| Ubuntu 22.04+ | X11 | ✅ Completo |
| Fedora 40+ | X11 | ✅ Completo |
| Arch Linux | X11 | ✅ Completo |
| Qualquer Linux | Wayland | ⚠️ Parcial (atalhos globais limitados) |
| Windows 10+ | — | ✅ Completo |

> **Nota Wayland:** A captura global de teclado pode não funcionar em todas as distribuições com Wayland. Recomendamos usar X11 para funcionalidade completa.

---

## Desenvolvimento

### Build do executável (Windows)

```powershell
pip install pyinstaller
pyinstaller autoclick.spec
```

O executável será gerado em `dist/AutoClick.exe`.

### Empacotamento Linux (.deb)

```bash
# O install.sh também pode gerar um pacote .deb
sudo apt install debhelper
dpkg-deb --build autoclick
```

---

## Licença

Distribuído sob a licença **MIT**. Veja [LICENSE](LICENSE) para mais informações.

---

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
