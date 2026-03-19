# Pirate's Sea 🏴‍☠️

A complete feature-rich 2D top-down pirate game built with **Pygame**.

Sail the open ocean, raid enemy ships, collect treasure chests scattered across
the world, repair at island docks, and survive dynamic weather — all rendered
with procedurally-generated art and a living, animated ocean.

---

## Features

- **Procedural world** — 15-20 unique islands (towns, forts, wilderness), 30-50 sea rocks,
  20-30 treasure chests and 15-20 enemy ships placed across an 8,000 × 8,000 pixel world
- **Realistic sailing** — wind direction affects your speed; raise/lower sails;
  angle yourself into the wind for maximum speed
- **Naval combat** — broadside cannon salvos (3 cannonballs per side), enemy AI that
  patrols, chases, attacks and retreats
- **Day / night cycle** — 4-minute full day cycle with colour-graded lighting
- **Dynamic weather** — Clear → Cloudy → Rain → Storm cycle with rain particles,
  lightning flashes, fog overlay and wind/wave modifiers
- **Particle effects** — splashes, explosions, smoke, sparkles, ship wake
- **HUD** — health bar, gold counter, compass rose, wind arrow, speed, day indicator,
  contextual interaction hints, low-health vignette
- **Minimap** — press **M** to toggle full-screen world map
- **Island docks** — sail close to repair your hull for free

---

## Requirements

- Python 3.9+
- pygame ≥ 2.0
- numpy ≥ 1.21 (optional, used by no critical path but listed for future use)

```
pip install -r requirements.txt
```

---

## How to Run

```bash
cd /path/to/pirate-game
pip install -r requirements.txt
python main.py
```

---

## Controls

| Key | Action |
|-----|--------|
| **W** / **↑** | Raise sails (accelerate) |
| **S** / **↓** | Lower sails (decelerate) |
| **A** / **←** | Turn left |
| **D** / **→** | Turn right |
| **SPACE** | Fire cannons (both broadsides) |
| **E** | Pick up nearby treasure / Repair at dock |
| **M** | Toggle minimap / full world map |
| **ESC** | Pause |

---

## Victory Condition

Collect **5,000 gold** by picking up treasure chests (press **E** when close).

- Bronze chest — 50 g
- Silver chest — 150 g
- Gold chest — 400 g
- Legendary chest — 1 000 g

Enemy ships also drop loot when sunk.

---

## Project Structure

```
pirate-game/
├── main.py                  # Entry point
├── requirements.txt
├── engine/
│   ├── settings.py          # All constants & colour palette
│   ├── camera.py            # Smooth-follow camera with screen shake
│   ├── utils.py             # Math helpers (lerp, noise, vec2, …)
│   └── game.py              # Main Game class & game-loop coordinator
├── world/
│   ├── ocean.py             # Multi-layer animated ocean renderer
│   ├── island.py            # Procedural island generation & rendering
│   ├── world_gen.py         # World layout generator
│   ├── minimap.py           # Minimap & full-screen map
│   └── weather.py           # Weather state machine
├── entities/
│   ├── player_ship.py       # Player ship: movement, wind physics, firing
│   ├── enemy_ship.py        # Enemy AI (patrol/chase/attack/retreat)
│   ├── cannonball.py        # Projectile physics & collision
│   ├── treasure.py          # Treasure chests with bobbing animation
│   └── particles.py         # Particle system (splash/explosion/smoke/…)
├── ui/
│   ├── hud.py               # In-game HUD overlay
│   ├── menu.py              # Main menu / pause / game-over / victory screens
│   └── inventory.py         # Inventory panel (gold display)
└── assets/
    └── generator.py         # Procedural sprite generation (no image files)
```
