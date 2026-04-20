# Branches of Yggdrassil — Execution Plan

**Game**: Monster Hunter-style third-person bow combat, single-player, one hero monster.
**Engine**: Unreal Engine 5.6 (Third-Person Combat Variant template)
**Timeline**: 8-week MVP (Path B, aggressive scope)
**Current status**: MVP asset pack complete and pushed. All laptop work done except optional audio.

---

## Ship Definition (What "Done" Means)

A player can:
1. See a title screen with Prontera visible behind it
2. Press Start → load into Field 08 arena
3. Move + aim + draw + release arrows
4. Dodge-roll with iframes
5. Fight Peco Peco with 3 tell-based attacks, 2 phases
6. Take damage (HP bar depletes), die → "You Died" → back to title
7. Kill Peco Peco → "Hunt Complete" → back to title

**Out of scope for MVP**: Poring enemies, crafting, progression, multiplayer, Prontera walkable hub (title-screen only).

---

## Remaining Credit Budget (as of 2026-04-20)

| Service | Used | Remaining | USD value remaining |
|---|---|---|---|
| Marble (world generation) | 4,890 / 7,000 | ~2,110 | ~$1.70 |
| Tripo (3D characters) | 180 / 600 | ~420 | ~$4.20 |

**Total out-of-pocket spend so far: $0.** All within free signup tiers.

---

## Phase 0 — Audio Generation *(Laptop, optional, ~45 min)*

**Purpose**: Generate BGM + SFX before leaving laptop. Can be deferred but cheaper to do while the async-generation rhythm is fresh.

### Tools
- [Suno](https://suno.com/) — free tier ~10 songs/day
- [ElevenLabs Sound Effects](https://elevenlabs.io/sound-effects) — free tier with generous credits
- [freesound.org](https://freesound.org/) — CC-licensed backup

### Deliverables (save to `assets/audio/`)

| File | Source | Prompt |
|---|---|---|
| `bgm_title.mp3` | Suno | "Peaceful Norse fantasy lute + harp menu theme, calm, 90 bpm, looping" |
| `bgm_hunt.mp3` | Suno | "Tense orchestral hunt theme, strings + taiko drums, 110 bpm, looping, dramatic" |
| `bgm_victory.mp3` | Suno | "Triumphant fanfare, brief, ~15 sec orchestral victory sting" |
| `sfx_bow_draw.wav` | ElevenLabs | "Wooden bow being drawn slowly, creaking string tension, 1.5 seconds" |
| `sfx_bow_release.wav` | ElevenLabs | "Bowstring release, arrow whoosh, crisp, 0.5 seconds" |
| `sfx_arrow_hit.wav` | ElevenLabs | "Arrow impacting flesh, wet thud, 0.3 seconds" |
| `sfx_arrow_miss.wav` | ElevenLabs | "Arrow striking wood, clean thunk, 0.3 seconds" |
| `sfx_peco_roar.wav` | ElevenLabs | "Deep aggressive bird beast roar, 3 seconds" |
| `sfx_peco_peck.wav` | ElevenLabs | "Quick bird screech + peck attack, 0.5 seconds" |
| `sfx_peco_step.wav` | ElevenLabs | "Heavy bird footstep on grass, bass-heavy, 0.4 seconds" |
| `sfx_footstep_grass.wav` | freesound | Any CC0 footstep on grass |
| `sfx_dodge.wav` | ElevenLabs | "Cloak whoosh, quick dodge, 0.4 seconds" |
| `sfx_hurt.wav` | ElevenLabs | "Human pained grunt, short, 0.3 seconds" |
| `sfx_death.wav` | ElevenLabs | "Human death cry, dramatic, 1 second" |
| `sfx_ui_click.wav` | freesound | Any CC0 UI click |

**Commit command**: `git add assets/audio/ && git commit -m "Add audio assets (BGM + SFX)" && git push`

**Defer if**: you'd rather start UE5 work first — audio can be integrated in Phase 7.

---

## Phase 1 — UE5 Setup *(PC, ~2–3 hours)*

### Prerequisites
- [ ] Check PC specs meet UE5 minimum (RTX 2060 / 8 GB VRAM / 16 GB RAM / NVMe free 100 GB+)
- [ ] Install Epic Games Launcher
- [ ] Install Unreal Engine 5.6

### Project Creation
- [ ] Launcher → Library → Unreal Engine 5.6 → Launch
- [ ] New Project → **Games → Third Person → Combat Variant**
- [ ] Blueprint (not C++ for MVP), Starter Content OFF (we have assets), Raytracing OFF (perf)
- [ ] Name: `BranchesOfYggdrassil`, Location: `C:\Dev\` (or wherever)

### Repo Integration
- [ ] Clone the assets repo: `git clone https://github.com/johnnal12/branchesOfYggdrassil.git C:\Dev\yggdrassil-assets`
- [ ] Keep UE5 project and assets repo as separate folders for clarity
- [ ] OR: move the UE5 project into a `game/` subfolder of the cloned repo (single source of truth)

### Verify Template Works
- [ ] Press Play in editor → you control a mannequin
- [ ] Press attack button → combo swings
- [ ] Dodge works
- [ ] Enemy dummy takes damage

**Milestone**: Template game runs. You have the foundation ~70% of combat already written.

---

## Phase 2 — Asset Import *(PC, ~3–4 hours)*

### Content Browser Folder Structure

Create in UE5 Content Browser:
```
Content/
├── Game/
│   ├── Characters/
│   │   ├── Hunter/
│   │   ├── Peco/
│   │   └── Poring/   (optional, unused in MVP core)
│   ├── Environments/
│   │   ├── Prontera/
│   │   └── Field08/
│   ├── UI/
│   └── Audio/         (if Phase 0 done)
```

### Import 3D Characters (GLB files)

- [ ] Content Browser → right-click → Import → navigate to repo's `assets/models/hunter/pbr_model.glb`
- [ ] Import settings:
  - Skeletal Mesh: **Yes** (need it rigged for animations)
  - Import Materials: Yes
  - Import Textures: Yes
  - Auto Compute LOD Screen Size: Yes
- [ ] Repeat for `peco/pbr_model.glb` and `poring/pbr_model.glb`
- [ ] Verify scale: hunter should be ~1.8 m tall (UE's cm units: 180). Peco should be ~3 m tall (300 cm). Scale up/down in import if off.

### Import World Meshes (GLB files)

- [ ] Import `field_08_final/collider.glb` as **Static Mesh** (no rig needed)
- [ ] Import `prontera_final/collider.glb` — optional, might not need in-level for title screen
- [ ] Generate collision: right-click mesh → Asset Actions → Add Complex Collision (or Auto Convex)

### Import Panorama as UI Backdrop

- [ ] Import `prontera_final/panorama.jpg` as Texture2D
- [ ] Settings: sRGB on, Compression: UserInterface2D (so it stays sharp in UI)

### Import Audio (if Phase 0 done)

- [ ] Import all `assets/audio/*.mp3` and `*.wav` files
- [ ] Group into Audio folder, tag BGM files as looping

**Milestone**: All your AI-generated content is in UE5 and usable as assets.

---

## Phase 3 — Hunter + Bow Mechanics *(Weeks 1–2)*

### Character Setup

- [ ] Create BP_Hunter Blueprint from Character class
- [ ] Assign Hunter skeletal mesh
- [ ] Assign capsule collision (match size ~90 cm radius, 180 cm height)
- [ ] Set as Default Pawn Class in GameMode

### Animation Retargeting (crucial for Tripo output)

The Tripo-generated hunter has its own skeleton. You need to retarget UE5 template animations:

- [ ] Open Hunter skeletal mesh → IK Rig → auto-generate humanoid rig
- [ ] Create IK Retargeter from Manny (UE5 template) → Hunter
- [ ] Retarget base Animation Blueprint assets (idle, walk, run, jump)

### Bow-Specific Animations

Need 5 custom animations. Options:
- **Easy**: Download free archer anims from Mixamo (archer_idle, archer_draw, archer_aim, archer_release, archer_dodge), retarget to Hunter
- **Medium**: Generate custom via DeepMotion using video reference
- **Hard**: Hand-key in Blender

### Input Mapping

Create Input Actions:
- [ ] `IA_Move` (WASD) — existing
- [ ] `IA_Look` (mouse) — existing
- [ ] `IA_Aim` (right mouse, hold) — new
- [ ] `IA_Draw` (left mouse, hold) — new
- [ ] `IA_Release` (left mouse, release) — new
- [ ] `IA_Dodge` (space or shift) — existing, repurpose

### Arrow Projectile

- [ ] Create BP_Arrow (Projectile component)
- [ ] Velocity scales with draw time (0.3 sec = weak, 1.5 sec = max)
- [ ] Collision: blocks enemies, spawns hit particle/sound on hit
- [ ] Lifetime: 5 seconds

**Milestone**: You control an archer who can aim, draw, and shoot arrows into thin air.

---

## Phase 4 — Peco Peco + Behavior Tree *(Week 3)*

### Monster Setup

- [ ] Create BP_PecoPeco from Character class
- [ ] Assign Peco skeletal mesh
- [ ] Scale to game scale (~3 m tall)
- [ ] Capsule collision sized for biped

### Animations for Peco

- [ ] Retarget or hand-create: idle, walk, run, peck attack, charge attack, roar, hurt, death
- [ ] Add Animation Notifies:
  - `HitboxActive` (frame 18 on peck, frames 22-30 on charge)
  - `HitboxInactive` (frame 24 on peck, frame 32 on charge)
  - `RoarSoundTrigger` (for audio)

### Behavior Tree

Create `BT_PecoPeco`:
- [ ] Root → Selector
  - Priority 1: If HP = 0 → Die (play anim, destroy actor)
  - Priority 2: If player spotted → Combat sequence
    - If distance > 8m → Charge attack
    - If distance 3–8m → Peck attack
    - If distance < 3m → Feather flurry (cooldown)
  - Priority 3: Patrol (idle + random wander)

### Phase Transition

- [ ] Blackboard key: `IsEnraged` (bool)
- [ ] Trigger at HP ≤ 50%: set `IsEnraged` true, play roar animation, increase attack speed by 20%

### AI Controller

- [ ] `AIC_PecoPeco` extends AIController
- [ ] Runs the behavior tree
- [ ] Uses Perception component for sight (500 cm range)

**Milestone**: Peco Peco sees you, chases, picks an attack based on range, telegraphs, and dies at 0 HP.

---

## Phase 5 — Combat Loop *(Weeks 4–5)*

**This is where the game becomes a game. Expect 60% of total dev time.**

### Damage System

- [ ] `BP_HealthComponent` on both hunter and Peco
- [ ] Attach Gameplay Tags (optional, but clean): `Damage.Pierce`, `Damage.Blunt`
- [ ] `TakeDamage` function: reduce HP, play hit reaction, broadcast death if 0

### Arrow → Peco

- [ ] Arrow `OnComponentHit` → cast Other to BP_PecoPeco → call `TakeDamage(20)` → destroy arrow
- [ ] Spawn hit particle/sound at impact point
- [ ] Peco plays Flinch animation

### Peco → Hunter

- [ ] During `HitboxActive` notifies, spawn collision volume attached to beak/body
- [ ] Volume overlaps hunter → call `HunterTakeDamage(15)`, hit reaction
- [ ] Hunter's dodge roll → 0.5 sec iframe window where incoming damage is ignored

### Tuning Phase (the real work)

This will take *multiple days* of playtest sessions:

- [ ] Peck wind-up: start 0.8 sec, tune until "fair to dodge"
- [ ] Charge wind-up: start 1.2 sec
- [ ] Feather flurry radius: start 3 m, tune feel
- [ ] Dodge iframe window: 12–16 frames (0.2–0.27 sec)
- [ ] Hunter HP: start 100, monster damage 15 per hit → 7 mistakes = death
- [ ] Peco HP: start 500, arrow damage 20 → 25 hits = kill (fight lasts ~3 minutes)

### Screen Feel

- [ ] Camera shake on taking damage
- [ ] Hit pause (0.05 sec freeze on impact) for weighty feel
- [ ] Slight slow-mo on Peco death (0.5 sec at 0.3x speed)

**Milestone**: You can fight Peco from start to death, and it feels like a real fight.

---

## Phase 6 — Field 08 Arena *(Week 6)*

### Level Setup

- [ ] New Level → from the imported `field_08_final/collider.glb` static mesh
- [ ] Place mesh at origin, scale to appropriate size (likely 1x)
- [ ] Add Player Start actor (1 at center-south)
- [ ] Add Peco Peco spawn point (1 at center-north, ~20 m from player)

### Collision & Navigation

- [ ] Nav Mesh Bounds Volume covering the arena area
- [ ] Bake nav (one click in Build menu)
- [ ] Verify: drop a debug AI character, confirm it pathfinds

### Kill Plane

- [ ] Plane trigger 500 cm below arena floor → if anything falls through, teleport back or kill

### Ambient Props

- [ ] Scatter ~5-10 additional props from [Kenney Nature Kit](https://kenney.nl/assets/nature-kit) or Epic's free fab.com assets
- [ ] Optional: generate a few more in Marble if you want unique ones (cost: ~$0.20 each at draft quality)

### Lighting

- [ ] Directional Light (sun) positioned to match panorama's golden-hour orange sky
- [ ] Sky Atmosphere + Volumetric Cloud
- [ ] Optional: Exponential Height Fog for depth

### Skybox (optional)

- [ ] Use the existing `field_08_final/panorama.jpg` as sky sphere texture
- [ ] OR generate a new 4K skybox via Blockade Labs Skybox API if you want clean one

**Milestone**: Fight Peco Peco in a proper arena that looks like your concept, not a gray box.

---

## Phase 7 — UI + Game Flow *(Week 7)*

### Title Screen

- [ ] UMG Widget: `WBP_TitleScreen`
- [ ] Background: `prontera_final/panorama.jpg` stretched to fill
- [ ] Title text: "Branches of Yggdrassil"
- [ ] "Press Any Key" prompt
- [ ] On input → Open Level: Field08_Hunt

### In-Game HUD

- [ ] `WBP_HUD` (added to viewport on level begin)
- [ ] Hunter HP bar (top-left, progress bar bound to `HealthComponent::CurrentHP`)
- [ ] Stamina bar (if you add dodge cost later)
- [ ] Monster HP bar (top-center, hidden until first damage dealt)
- [ ] Aim reticle (center, only visible while aiming)
- [ ] Ammo counter (optional — infinite arrows simplest)

### Victory / Death Screens

- [ ] `WBP_VictoryScreen`: "Hunt Complete" + play bgm_victory + "Return to Title" button
- [ ] `WBP_DeathScreen`: "You Died" + "Try Again" (reload level) + "Return to Title"
- [ ] Triggered by events in the main game BP

### Game Flow

```
Title Screen
   ↓ (Press Start)
Loading → Field08_Hunt level
   ↓
Hunt (fight Peco)
   ↓
   ├─ Peco dies → Victory Screen → Title
   └─ Hunter dies → Death Screen → Title or Retry
```

**Milestone**: You can play a full game session from title through fight through result and back.

---

## Phase 8 — Polish + Ship *(Week 8)*

### Bug Fix Pass

- [ ] Record a full playthrough, note every jank
- [ ] Fix top 5–10 most annoying issues
- [ ] Don't fix everything — accept MVP quality

### Packaging

- [ ] Project Settings → Project → set Name, Description, Company, Version 0.1.0
- [ ] Set Game Default Map (title screen level)
- [ ] Build → Package Project → Windows (64-bit) → Shipping configuration
- [ ] Output: `BranchesOfYggdrassil-Win64.zip` (~200–500 MB expected)
- [ ] Test the packaged build on the same PC first

### itch.io Page

- [ ] Create account at [itch.io](https://itch.io)
- [ ] New Project → Game → paid or free (free recommended for MVP)
- [ ] Upload the zip
- [ ] Screenshots: from panorama backdrops + in-engine combat shots
- [ ] Description: "Monster Hunter-style boss fight. Bow combat. ~10 minutes."
- [ ] Tags: action, souls-like, bow, hunter, indie, solo-dev, mvp

### Launch

- [ ] Share link with friends for playtesting first
- [ ] Publish page publicly
- [ ] Tweet / share with short gameplay clip (15–30 sec)

**Milestone: YOU SHIPPED A GAME.** 95th-percentile solo-dev accomplishment.

---

## What Can Be Revisited on Laptop (After PC Phase Starts)

Things that don't require the PC:

| Task | Free? | Notes |
|---|---|---|
| Generate extra props (Meshy API) | Yes (free tier) | Add variety to Field 08 |
| Generate ambient Poring variants (Tripo API) | Yes | For optional swarm enemies post-MVP |
| Generate alternate skyboxes (Blockade Labs) | Low cost | Different time-of-day for arena |
| Generate more music/SFX (Suno, ElevenLabs) | Free tier | Add variety |
| Re-generate maps (Marble API, ~2110 credits left) | Already paid | Fix anything broken or add new areas |
| Iterate on concept art (Grok) | Free | If you want a boss #2 or new creature |
| Edit design docs in the repo | Free | Pure git work |
| Write the game's lore, item descriptions, story | Free + Claude | Fills out content |

**Rule**: If it's asset generation or design, laptop. If it's wiring things into the engine, PC.

---

## What's Locked to PC

- UE5 editor (visuals need the GPU)
- Blueprint work
- Animation retargeting
- Game builds/packaging
- Gameplay playtesting / combat feel tuning

---

## Stretch Goals (Post-MVP, in priority order)

1. **Add Poring as ambient enemies** — swarm around Field 08, die in 1 shot, just flavor
2. **Second monster (boss #2)** — generate new concept + Tripo 3D + behavior tree
3. **Prontera as walkable hub** — replace title-screen with actual walkable town
4. **Weapon variety** — add great sword melee weapon (Mixamo animations available)
5. **Difficulty modes** — easy (longer tells), hard (shorter tells, more damage)
6. **Speedrun timer** — cheap social hook
7. **Steam release** — $100 developer fee, real distribution, but commercial rights concern with "Prontera" name (rename to avoid)

---

## Red Flags to Watch For

- **Combat feels off after 4 weeks** → Step back, review references (Dark Souls, Monster Hunter, Bloodborne boss fights on YouTube), specifically note wind-up timings
- **Performance <30 FPS in Field 08** → Disable Nanite/Lumen on lower-end PCs, use traditional lighting
- **Tripo Peco skeleton doesn't animate cleanly** → Regenerate with `--quality detailed --quad` for cleaner topology (~60-70 credits)
- **Scope creep tempts you** → Re-read this plan. 8-week MVP. One monster. One weapon. Ship it, THEN extend.

---

## Tracking

Per-phase tasks live in the Claude Code task list (run `/tasks` or `TaskList` to see current state). Mark phases complete as you finish. Each phase has ~1–15 sub-items implicit in this doc.

---

## When You're Stuck

- UE5 questions: [forums.unrealengine.com](https://forums.unrealengine.com) + Epic's tutorial ecosystem
- Blueprint questions: [Mathew Wadstein's YouTube channel](https://www.youtube.com/@MathewWadstein) covers 90% of node-level UE5 questions
- Combat design: watch GMTK's ["Why Do Monster Hunter's Monsters Feel So Good?"](https://www.youtube.com/c/MarkBrownGMTK) videos
- Call back to this conversation: future sessions have context via memory system — just describe what you hit

---

**Last updated**: 2026-04-20
**Repo**: https://github.com/johnnal12/branchesOfYggdrassil
**Project**: Branches of Yggdrassil
**You're here**: End of laptop work, ready for PC phase.

Good hunting.
