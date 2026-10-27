# Motion OralSin Itapetininga: Dentadura x Protocolo (45s, 1080×1920)

Vídeo vertical para Reels, Stories e TikTok. Não tem música, só efeitos sonoros leves. A narração entra depois.
Usa a paleta verde e o logo da OralSin, com títulos em 3D no estilo dos stories do perfil.

## Arquivos

| Arquivo | O que é |
|---|---|
| `oralsin_protocolo_45s.mp4` | Vídeo final com efeitos sonoros |
| `oralsin_protocolo_45s_sem_som.mp4` | Mesmo vídeo sem som |
| `sfx.wav` | Trilha de efeitos separada, para mixar com a narração |
| `logo.svg` | Logo OralSin vetorizado a partir de `assets/logo_original.jpg` |
| `motion.html` / `render.js` / `sfx.py` | Fonte da animação, render e efeitos |

## Tempos para a narração (sugestão de texto)

| Tempo | Na tela | Sugestão de fala |
|---|---|---|
| 0:00 – 0:04 | "Você ainda usa DENTADURA?" → "Existe uma solução FIXA" | "Você ainda usa dentadura? Saiba que existe uma solução fixa." |
| 0:04 – 0:08 | Nº 1 em implantes do Brasil | "A Oral Sin é a número 1 em implantes do Brasil." |
| 0:08 – 0:14 | Antes x Depois (dentadura solta × protocolo preso nos pinos) | "Veja a diferença entre a dentadura comum e o protocolo sobre implantes." |
| 0:14 – 0:17 | Na hora de comer | "Com a dentadura é difícil mastigar. Com o protocolo, você come de tudo." |
| 0:17 – 0:21 | Firmeza | "A dentadura solta e escorrega. O protocolo fica fixo." |
| 0:21 – 0:24 | No dia a dia | "Nada de cola, nada de tirar para dormir." |
| 0:24 – 0:28 | Seu sorriso | "E você volta a sorrir com confiança." |
| 0:28 – 0:35 | Como funciona: implantes no osso → prótese presa nos pinos | "Primeiro, os implantes são fixados no osso. Depois, a prótese é presa nos pinos. Não sai e não mexe." |
| 0:35 – 0:39 | Implante unitário | "Perdeu só um dente? O implante unitário devolve um dente fixo, como o natural." |
| 0:39 – 0:45 | CTA: logo, "Agende sua AVALIAÇÃO", (15) 99659-9212, @oralsinitapetininga | "Agende sua avaliação na Oral Sin Itapetininga. Chame agora no (15) 99659-9212." |

Dica de mixagem: deixe os efeitos uns 8 a 10 dB abaixo da voz.

## Renderizar de novo

```bash
node render.js video_sem_audio.mp4 30
python3 sfx.py sfx.wav
ffmpeg -i video_sem_audio.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest oralsin_protocolo_45s.mp4
```
