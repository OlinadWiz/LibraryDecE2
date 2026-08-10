# JasonTV DASH backend

GitHub Actions cross-compila il plugin ufficiale GStreamer
`adaptivedemux2`/`dashdemux2` per Zgemma H7 ARMHF. Il sorgente e fissato alla
release GStreamer 1.28.5, uguale al runtime del decoder.

Artefatto iniziale:

`jasontv-dash-zgemmah7_1.0.0-r0_cortexa15hf-neon-vfpv4.ipk`

Dopo l'installazione verificare:

```sh
gst-inspect-1.0 dashdemux2
gst-inspect-1.0 adaptivedemux2
```

Il plugin richiede un contenitore streams-aware (`playbin3`/`decodebin3`).
