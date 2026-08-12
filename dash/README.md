# JasonTV DASH backend

GitHub Actions cross-compila il plugin ufficiale GStreamer
`adaptivedemux2`/`dashdemux2` per i profili ABI definiti in
`../native-profiles.json`. Consulta anche `../native/README.md`.

Artefatto iniziale:

`jasontv-dash-armv7hf-neon-gst128-soup2_1.0.0-r1_cortexa15hf-neon-vfpv4.ipk`

Dopo l'installazione verificare:

```sh
gst-inspect-1.0 dashdemux2
gst-inspect-1.0 adaptivedemux2
```

Il plugin richiede un contenitore streams-aware (`playbin3`/`decodebin3`).
