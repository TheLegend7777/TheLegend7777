# Motion OralSin Itapetininga: Dentadura x Protocolo (30s, 1080×1920)

Vídeo vertical para Reels, Stories e TikTok. Não tem música, só efeitos sonoros leves. A narração entra depois.

## Arquivos

| Arquivo | O que é |
|---|---|
| `oralsin_protocolo_30s.mp4` | Vídeo final com efeitos sonoros |
| `oralsin_protocolo_30s_sem_som.mp4` | Mesmo vídeo sem som, para quem prefere mixar do zero |
| `sfx.wav` | Trilha de efeitos separada, para baixar o volume ao pôr a narração |
| `logo.svg` | **Logo provisório (recriado).** Substitua pelo logo oficial |
| `motion.html` / `render.js` / `sfx.py` | Fonte da animação, render e efeitos |

## Tempos para a narração (sugestão de texto)

| Tempo | Na tela | Sugestão de fala |
|---|---|---|
| 0:00 – 0:03 | "Você ainda usa DENTADURA?" → "Existe uma opção FIXA" | "Você ainda usa dentadura? Existe uma opção fixa." |
| 0:03 – 0:07 | Antes x Depois (dentadura solta × protocolo fixo) | "Veja a diferença entre a dentadura e o protocolo sobre implantes." |
| 0:07 – 0:10 | Na hora de comer | "Com a dentadura é difícil mastigar. Com o protocolo, você come de tudo." |
| 0:10 – 0:12 | Firmeza | "Ela solta e escorrega. O protocolo fica fixo." |
| 0:12 – 0:15 | No dia a dia | "Nada de cola, nada de tirar para dormir." |
| 0:15 – 0:17 | Seu sorriso | "E você volta a sorrir com confiança." |
| 0:17 – 0:23 | Como funciona: implantes no osso → dentes fixos por cima | "Os implantes são fixados no osso, e os dentes ficam presos por cima, firmes." |
| 0:23 – 0:30 | CTA: logo, "Agende sua AVALIAÇÃO", (15) 99659-9212, @oralsinitapetininga | "Agende sua avaliação na Oral Sin Itapetininga. Ligue ou chame no (15) 99659-9212." |

Dica de mixagem: deixe os efeitos uns 8 a 10 dB abaixo da voz.

## Trocar o logo e renderizar de novo

1. Salve o logo oficial como `logo.svg` nesta pasta (ou troque `logo.svg` por `logo.png` nas duas tags `<img>` de `motion.html`).
2. Rode:
   ```bash
   node render.js video_sem_audio.mp4 30
   python3 sfx.py sfx.wav
   ffmpeg -i video_sem_audio.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest oralsin_protocolo_30s.mp4
   ```
