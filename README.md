# Branches of Yggdrassil

A Monster Hunter-style third-person action game set in Ragnarok Online's Prontera. Solo hunter + bow, hunting iconic RO monsters reimagined at MH scale.

## Status

**MVP asset pack complete — ready for Unreal Engine integration.**

## What's In Here

### Generated 3D Assets

Worlds (via [World Labs Marble API](https://platform.worldlabs.ai)):

- `assets/maps/prontera_final/` — Prontera town square, menu backdrop
- `assets/maps/field_08_final/` — open hunt arena with cliffs, ruins, sparse trees

Characters (via [Tripo 3D API](https://platform.tripo3d.ai)):

- `assets/models/poring/` — ambient small creature (pink jelly slime)
- `assets/models/peco/` — Peco Peco, hero monster (dark-feathered bird wyvern)
- `assets/models/hunter/` — player character, archer with bow

### Reference Material

- `assets/concepts/` — reference images used as Tripo inputs

### Scripts

- `scripts/world_gen.py` — Marble API driver (text-to-world)
- `scripts/asset_gen.py` — Tripo API driver (image-to-3D)

## Generation Pipeline (reproducible)

### World generation (Marble)

```bash
export WLT_API_KEY="..."   # from platform.worldlabs.ai
python3 scripts/world_gen.py --name <name> --prompt "..." --model standard
```

Outputs: `collider.glb`, `panorama.jpg`, `splat_100k.spz`

### 3D asset generation (Tripo)

```bash
export TRIPO_API_KEY="..."   # from platform.tripo3d.ai (Secrets)
python3 scripts/asset_gen.py --name <name> --ref <path> --model-version P1-20260311
```

Outputs: `pbr_model.glb`, `preview.png`

## Credits Used (Free Tier)

- Marble: 4,890 / 7,000 signup credits
- Tripo: 180 / 600 signup credits
- Out of pocket: **$0**

## Next Steps

- [ ] Audio: BGM (Suno), SFX (ElevenLabs / freesound)
- [ ] Unreal Engine 5.6 project setup
- [ ] Import all assets
- [ ] Combat code: aim/draw/release, dodge roll, monster AI
- [ ] UI: HP bars, title screen, win/lose

## Tech Stack

- Unreal Engine 5.6 (Third-Person Combat Variant template)
- AI-generated assets: Marble (maps), Tripo P1 (characters)
- Concept art: Grok
