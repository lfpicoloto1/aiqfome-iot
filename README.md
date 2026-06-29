# Aiqfome Eyes

Animação de olhos piscando do fantasminha aiqfome para Raspberry Pi 4 com display LCD 3.5" SPI em orientação **horizontal** (480×320).

A tela é montada dentro de uma moldura 3D roxa (formato do logo). O software renderiza fundo roxo + dois olhos brancos ovalados que piscam aleatoriamente — alinhados ao recorte da moldura.

## Requisitos

- Raspberry Pi 4
- Display 3.5" SPI 480×320 horizontal (ex.: Waveshare ST7796S)
- Python 3.11+

## Desenvolvimento local (PC)

```bash
cd aiqfome-iot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main --backend window
```

Pressione **ESC** ou feche a janela para sair. Clique/toque na tela para o fantasminha piscar e olhar na direção do toque.

## Animações

O espaçamento e tamanho dos olhos são calculados **automaticamente a partir do logo oficial** (`eyes.from_logo: true`). Proporções medidas no PNG do aiqfome:

- Largura do olho ≈ **12,2%** da largura da tela
- Espaço entre olhos ≈ **2,29×** a largura de um olho
- Altura do olho ≈ **1,79×** a largura

Para alinhar verticalmente na moldura física, ajuste só `center_y_offset`:

```yaml
eyes:
  from_logo: true
  center_y_offset: 0   # negativo = sobe, positivo = desce
```

| Estado | Comportamento |
|--------|---------------|
| **Idle** | Piscadas normais, posição central |
| **Curioso** | Olha suavemente para esquerda/direita/cima/baixo e volta ao centro |
| **Sonolento** | Olhos semi-fechados, cor levemente mais escura, piscadas mais lentas |
| **Alerta** | Olhos levemente maiores, piscadas menos frequentes |
| **Toque** | Piscada imediata + olhar breve na direção do toque |

Parâmetros de timing e intensidade em `config.yaml` → seção `animation`.

## Setup no Raspberry Pi

### 1. Habilitar SPI

```bash
sudo raspi-config
# Interface Options → SPI → Yes
```

### 2. Instalar driver do display

O display vendido no Mercado Livre costuma ser compatível com Waveshare. Identifique o modelo na placa (B, F, G, etc.) e siga a wiki correspondente:

- [3.5" RPi LCD (B)](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(B))
- [3.5" RPi LCD (F)](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(F))
- [3.5" RPi LCD (G)](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(G))

Instalação típica via repositório LCD-show:

```bash
git clone https://github.com/waveshare/LCD-show
cd LCD-show
sudo ./LCD35-show   # ou o script correspondente ao seu modelo
sudo reboot
```

Após reboot, o LCD deve aparecer como `/dev/fb0`.

### 3. Instalar o projeto

```bash
cd ~
git clone git@github.com:lfpicoloto1/aiqfome-iot.git
cd aiqfome-iot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Testar no LCD

```bash
python -m src.main --backend fbdev
```

Se o display usar outro framebuffer:

```bash
python -m src.main --backend fbdev --fbdev /dev/fb1
```

### 5. Iniciar no boot (systemd)

Ajuste o caminho `User` e `WorkingDirectory` em `deploy/aiqfome-eyes.service` se necessário, depois:

```bash
sudo cp deploy/aiqfome-eyes.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now aiqfome-eyes
```

Verificar status:

```bash
sudo systemctl status aiqfome-eyes
```

## Calibração com a moldura

Edite [`config.yaml`](config.yaml) para alinhar os olhos ao recorte da moldura 3D:

```yaml
eyes:
  from_logo: true
  center_y_offset: 0   # fine-tune vertical na moldura
```

Desative `from_logo` e defina `width`, `height`, `center_y`, `gap_ratio` manualmente se preferir.

Ajuste também a cor de fundo se o roxo da moldura for diferente:

```yaml
colors:
  background: "#7B2CBF"
```

### Orientação horizontal

A tela fica montada na horizontal (480×320). No driver Waveshare, use rotação de 90° no overlay, por exemplo:

```
dtoverlay=Waveshare35g,fps=60,speed=48000000,rotate=90
```

Os valores `display.width` e `display.height` em `config.yaml` devem corresponder à resolução final do framebuffer (`480` × `320`). Se a imagem aparecer rotacionada ou espelhada, ajuste o parâmetro `rotate` no driver (0, 90, 180 ou 270).

## Estrutura

```
aiqfome-iot/
├── config.yaml          # cores, posição dos olhos, timing do piscar
├── requirements.txt
├── src/
│   ├── main.py          # loop principal
│   ├── config.py        # carrega YAML
│   ├── animation/
│   │   ├── animator.py  # combina blink + mood + toque
│   │   ├── blink.py     # máquina de estados
│   │   ├── mood.py      # idle / curioso / sonolento / alerta
│   │   └── eyes.py      # desenho dos olhos
│   └── display/
│       ├── pygame_window.py   # backend dev
│       └── pygame_fbdev.py    # backend Pi
└── deploy/
    └── aiqfome-eyes.service
```

## Opções da CLI

```
python -m src.main --help

  --config PATH     Caminho do config.yaml (default: ./config.yaml)
  --backend NAME    window (dev) ou fbdev (Raspberry Pi)
  --fbdev PATH      Dispositivo framebuffer (default: /dev/fb0)
```
