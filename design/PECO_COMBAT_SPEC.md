# Peco Peco — Combat Design Spec

Hero monster for MVP. Tuning numbers for UE5 Phase 4–5. **All values are starting points — adjust during playtest.**

---

## Stats

| Attribute | Value | Notes |
|---|---|---|
| Max HP | 500 | ~25 arrow hits at 20 damage each |
| Walk speed | 200 cm/s | Slow roam / idle |
| Run speed | 450 cm/s | Chasing player |
| Charge speed | 900 cm/s | Full-sprint charge attack |
| Height | ~300 cm (3 m) | Scale accordingly in UE5 |
| Body hitbox | Capsule: radius 120, height 280 | Attached to root bone |
| Aggro range | 1500 cm (15 m) | Line-of-sight check |
| Leash range | 3500 cm (35 m) | Returns to spawn if player escapes |

---

## Attacks

### Attack 1 — **Peck** (close-range bread-and-butter)

| Phase | Duration | Notes |
|---|---|---|
| **Wind-up** | 0.80 sec | Head rears back, neck curves (obvious tell) |
| **Strike** | 0.25 sec (frames 18–24 @ 30 fps) | Hitbox active |
| **Recovery** | 0.50 sec | Head returns, vulnerable |
| Total | 1.55 sec | |

- **Hitbox**: Capsule attached to beak socket. Radius 80, length 150. Activated via Animation Notify `HitboxOn` / `HitboxOff`.
- **Damage**: 15
- **Dodge direction**: Backward (sidestep works but tight)
- **Cooldown**: 1.5 sec after animation complete
- **AI trigger**: Player distance < 400 cm, cooldown ready

---

### Attack 2 — **Charge** (long-range gap-closer)

| Phase | Duration | Notes |
|---|---|---|
| **Wind-up** | 1.20 sec | Legs plant, body lowers, head forward (long tell) |
| **Charge** | 1.00 sec (up to 900 cm/s) | Body hitbox active entire duration |
| **Recovery** | 1.00 sec | Skids, pants, vulnerable window |
| Total | 3.20 sec | |

- **Hitbox**: Full body capsule during charge
- **Damage**: 25 (devastating if hit)
- **Dodge direction**: Sideways / perpendicular to charge line
- **Cooldown**: 3.0 sec
- **AI trigger**: Player distance 600–1200 cm, cooldown ready
- **Tracking**: Lock direction at end of wind-up — cannot turn during charge

---

### Attack 3 — **Feather Flurry** (AOE panic button)

| Phase | Duration | Notes |
|---|---|---|
| **Wind-up** | 1.00 sec | Puffs up, feathers ripple (tell) |
| **Burst** | 0.50 sec | AOE active |
| **Recovery** | 0.80 sec | Feathers settle |
| Total | 2.30 sec | |

- **Hitbox**: Sphere centered on monster, radius 300 cm
- **Damage**: 20 + 1 sec knockback stagger
- **Dodge direction**: Dodge OUT (distance > 300 cm) or through with iframe
- **Cooldown**: 5.0 sec
- **AI trigger**: Player distance < 300 cm AND other attacks on cooldown (panic move)

---

## Phase 2 — **Enraged** (triggers at HP ≤ 50%)

Transition:
- Play `anim_roar` (2.0 sec, invincible but can't move or attack — player window)
- Set `IsEnraged = true`
- Spawn red particle effect on feathers

Changes in Phase 2:
| Property | Phase 1 | Phase 2 |
|---|---|---|
| All wind-up timings | 100% | 80% (faster tells = harder to read) |
| All cooldowns | 100% | 75% |
| Charge tracking | Locks at wind-up end | Locks 0.3 sec later (slight tracking mid-charge) |
| Movement speed | 450 cm/s | 550 cm/s |

---

## Behavior Tree Structure

```
Root: Selector
├── [priority 1] IsDead? → Die
├── [priority 2] PhaseTransition? → EnrageSequence
├── [priority 3] PlayerInAggro?
│   └── Combat Sequence
│       ├── IsPlayerInRange("close", 400 cm) & Peck.Ready? → Peck
│       ├── IsPlayerInRange("close", 300 cm) & FeatherFlurry.Ready? → FeatherFlurry
│       ├── IsPlayerInRange("mid-long", 600-1200 cm) & Charge.Ready? → Charge
│       ├── All attacks on cooldown? → RunToPlayer
│       └── Else → IdleAggressive
└── [priority 4] Patrol / idle
```

**Blackboard keys**:
- `PlayerLocation` (Vector)
- `PlayerDistance` (Float)
- `IsEnraged` (Bool)
- `IsDead` (Bool)
- `HasLineOfSight` (Bool)

---

## Death Sequence

- HP reaches 0
- Freeze all behavior-tree processing
- Play `anim_death` (2.5 sec)
  - Frame 0–30: stumble
  - Frame 30–60: collapse, ground impact
  - Frame 60–75: final shudder
- Spawn feather particle cloud (cosmetic)
- At end: disable collision, trigger `OnMonsterDefeated` event → level win

---

## Hunter vs Peco Tuning Targets

After Phase 5 combat tuning, these playtests should feel:
- **First-time player kills Peco in Phase 1**: ~8–10 minutes with multiple deaths
- **Skilled player**: 3–5 minutes clean run
- **Getting hit** should feel *fair* — player should be able to watch replay and see the tell they missed
- **Dodge roll** should feel empowering (iframes 0.2–0.27 sec), not a guessing game

---

## Animation Notify Cheat Sheet

Per attack, set these notifies in the UE5 Animation Editor:

| Anim | Notify | Frame | Purpose |
|---|---|---|---|
| Peck | `SFX_PecoScreech` | 5 | play peck sound |
| Peck | `HitboxOn` | 18 | activate beak hitbox |
| Peck | `HitboxOff` | 24 | deactivate |
| Charge | `SFX_PecoChargeHuff` | 10 | audio tell |
| Charge | `HitboxOn` | 30 | activate body collision damage |
| Charge | `HitboxOff` | 60 | deactivate (after skid) |
| FeatherFlurry | `SFX_FeatherWhoosh` | 20 | audio |
| FeatherFlurry | `HitboxOn` | 30 | AOE active |
| FeatherFlurry | `HitboxOff` | 45 | AOE off |
| Death | `SFX_PecoDeathCall` | 10 | dying screech |
| Death | `ImpactParticles` | 30 | dust cloud when it hits ground |

---

## What to Tune First in Playtest

Order of tuning when combat feels off (Phase 5):

1. **Wind-up timings** — if too short, player can't dodge in time = unfair
2. **Dodge iframe window** — if too short, dodges feel unreliable
3. **HP values** — if fight is too fast (<3 min), Peco needs more HP; too slow (>15 min), damage needs buffing
4. **Camera distance / lock-on** — if you can't see tells clearly, pull camera back
5. **Audio cue timing** — if tells arrive silent, feel unfair

---

## Reference for Feel

When in doubt, watch these combat clips for reference:
- **Dark Souls — Ornstein & Smough** — tell timing clarity
- **Monster Hunter World — Jagras** — intro monster pace
- **Elden Ring — Tree Sentinel** — punishing but fair tells
- **Bloodborne — Cleric Beast** — phase 2 animation cues

---

**Last updated**: 2026-04-20
**Use**: reference during UE5 Phase 4 (Peco AI) + Phase 5 (combat tuning)
