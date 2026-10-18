# android21 Umbrel app store

A community app store for umbrelOS. Add it in **Settings -> App Store -> Add** with
`https://github.com/cyb3rw0lf-3D/android21-umbrel-apps`.

| app | what |
|---|---|
| `android21-klipper-printer` | Klipper + Moonraker + Fluidd for a USB-serial 3D printer, run from your own config |

This repo contains **no printer config, no Klipper/Moonraker source and no secrets**. The app mounts those from its
data folder on the device; the helper that copies them there lives in the private `android21-services` repo
(`scripts/stage-printer-app.sh`).

`images/` holds the two pip-layer images (Python deps only); `.github/workflows/images.yml` builds and pushes them to
`ghcr.io/cyb3rw0lf-3d/android21-{klipper,moonraker}`.
