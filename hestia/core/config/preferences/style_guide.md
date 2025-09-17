# Style guide

This clean, actionable style kit merges the references below into Home Assistant dashboard decisions (theme, layout, and card patterns).

## References

1. synthwave / vaporwave neon
2. modern dark console
3. glasmorphic polish

**Mood:** neon dusk / retro-futurism. Dark canvas, saturated **magenta–violet–cyan** accents, with selective **hot yellow** highlights.
**Surfaces:** *glasmorphism* (subtle blur + translucency) on primary cards; flat dark panels for info-dense  areas.
**Shapes:** rounded 12–18px corners, pill chips, circular dials; thin neon strokes and soft outer glows.
**Motion:** micro glows on hover/press; progress rings/bars with smooth easing.
**Hierarchy:** big, image-led “Now Playing”; bold primary actions; de-emphasized utilities in collapsible/secondary rows.

---

## 1. Theme snippet (neon dusk)

Drop in `themes.yaml`, select it in your profile

```yaml
Retro Dusk:
  modes:
    dark:
      primary-color: "#E91E63"                  # neon pink
      accent-color: "#00E5FF"                   # cyan
      warning-color: "#FFD54F"                  # warm yellow
      success-color: "#26C6DA"
      error-color: "#FF5370"
      card-background-color: "rgba(15,17,26,0.65)"
      ha-card-border-radius: "16px"
      ha-card-box-shadow: "0 6px 24px rgba(0,0,0,0.45)"
      primary-background-color: "#0A0C13"       # canvas
      secondary-background-color: "#0F1220"
      text-color: "#ECEFF1"
      secondary-text-color: "#AAB2C0"
      paper-item-icon-color: "#AAB2C0"
      paper-item-icon-active-color: "#FF2BD6"
      # Optional backdrop gradient
      background-image: "linear-gradient(135deg,#1b0d2a 0%,#0d1231 60%,#071d27 100%)"
```

> Want the frosted look? Add **card-mod** (HACS) and use the blur style below.

---

## 2. Card surface styles (card-mod)

Apply globally or per-card.

```yaml
card_mod:
  theme: Retro Dusk
  style: |
    ha-card {
      backdrop-filter: blur(10px) saturate(120%);
      border: 1px solid rgba(255,255,255,0.06);
    }
```

---

## 3. Layout architecture (grid blueprint)

Use **custom\:layout-card (grid-layout)** for responsive columns; section with headers → content.

```yaml
type: custom:layout-card
layout_type: custom:grid-layout
layout:
  grid-template-columns: repeat(12, 1fr)
  grid-gap: 16px
  mediaquery:
    "(max-width: 600px)":
      grid-template-columns: 1fr
    "(min-width: 601px) and (max-width: 1100px)":
      grid-template-columns: repeat(6, 1fr)
cards:
  # Now Playing (hero)
  - type: grid
    view_layout: { grid-area: "1 / 1 / 2 / 9" }    # spans 8/12
    cards: [ ... ]
  # Primary Actions (sources)
  - type: grid
    view_layout: { grid-area: "1 / 9 / 2 / 13" }   # spans 4/12
    cards: [ ... ]
  # Matrix Advanced
  - type: grid
    view_layout: { grid-area: "2 / 1 / 3 / 6" }
    cards: [ ... ]
  # Plex & Library
  - type: grid
    view_layout: { grid-area: "2 / 6 / 3 / 13" }
    cards: [ ... ]
  # Consoles & Power
  - type: grid
    view_layout: { grid-area: "3 / 1 / 4 / 13" }
    cards: [ ... ]
```

---

## 4. Bubble-card patterns (primary UI)

Use **custom\:bubble-card** for tappable, glowy actions.

```yaml
# Primary source bubble (tap aligns A+B via your modular script)
type: custom:bubble-card
card_type: button
name: Apple TV
icon: mdi:apple
button_action:
  tap_action:
    action: perform-action
    perform_action: script.matrix_control
    data:
      source: "Apple TV"
      remote: remote.bedroom_broadlink_rm3_alpha
      device: bedroom_hdmi_matrix
      tv: media_player.bedroom_tv_alpha
styles:
  card:
    - background: "linear-gradient(180deg, rgba(255,43,214,0.18), rgba(0,229,255,0.12))"
    - box-shadow: 0 0 24px rgba(255,43,214,0.35)
```

**Switch/Wii with hold/double-tap (power):**

```yaml
button_action:
  tap_action:
    action: perform-action
    perform_action: script.matrix_control
    data: { source: "Nintendo Switch", remote: remote.bedroom_broadlink_rm3_alpha, device: bedroom_hdmi_matrix, tv: media_player.bedroom_tv_alpha }
  hold_action:
    action: perform-action
    perform_action: switch.turn_on
    data: { entity_id: switch.bedroom_tv_nintendo_switch_tplink_power }
  double_tap_action:
    action: perform-action
    perform_action: switch.turn_off
    data: { entity_id: switch.bedroom_tv_nintendo_switch_tplink_power }
```

**Neon gauges / stats (vaporwave palette):**

```yaml
type: custom:apexcharts-card
chart_type: radialBar
series:
  - entity: sensor.plex_media_server_dsm220plus_viewers_watching
    name: Watching
apex_config:
  plotOptions:
    radialBar:
      hollow: { size: "64%" }
      track: { background: "rgba(255,255,255,0.08)" }
  fill: { type: gradient, gradient: { shade: "dark", gradientToColors: ["#00E5FF"], stops: [0,100], colorStops: [] } }
  colors: ["#FF2BD6"]
```

---

## 5. Section headers with micro-copy

Short, friendly blurbs from your media view:

```yaml
- type: markdown
  content: >
    ### Watch / Listen
    **Tap** routes **Video (A)** + **Audio (B)** to the source (TV turns on if off).
    **Hold** Switch/Wii = power ON • **Double-tap** = power OFF.
```

---

## 6. Visual accents (retro lines, scanlines, neon borders)

Optional flourishes inspired by the refs:

```yaml
# Neon section border
type: markdown
card_mod:
  style: |
    ha-card {
      border-radius: 18px;
      border: 1px solid rgba(255,43,214,0.5);
      box-shadow: 0 0 18px rgba(255,43,214,0.35), inset 0 0 8px rgba(0,229,255,0.12);
    }

# Subtle scanline overlay (put once at top of view)
type: markdown
card_mod:
  style: |
    ha-card {
      background: repeating-linear-gradient(
        180deg,
        rgba(255,255,255,0.02) 0,
        rgba(255,255,255,0.02) 1px,
        transparent 2px,
        transparent 4px
      );
    }
```

---

## 7. Information architecture (what goes where)

### 1. **Row 1**

- **Now Playing (hero, wide):** artwork/video preview, transport, SONOS volume sliders (bubble sliders), quick source indicator chip.
- **Primary Sources (narrow stack):** Apple TV / PS4 / Switch / Wii bubbles with micro-copy.

### 2. **Row 2**

- **Matrix & Advanced Routing (left):** Power + ARC bubbles, collapsible grid of A1–A4 / B1–B4.
- **Plex & Library (right):** “Watching now” radial gauge, Shows/Movies counters, last-added in small chips, optional dropdowns + “Route & Open Plex”.

### 3. **Row 3**

- **Consoles & Power (full):** Switch/Wii status bubbles with “on since …”; optional mini-timeline or usage bars.

---

## 8. Color tokens (consistent neon palette)

- colors: ["#FF2BD6", "#7C4DFF", "#00E5FF", "#FFD54F"]
- Use muted versions at 10–20% alpha for fills; 35–45% alpha for glows.

---

## 9. Accessibility & rhythm

- Maintain **≥ 4.5:1** contrast for text on frosted cards (adjust text to near-white).
- Grid spacing: **16px gutters**, 24–32px around hero areas.
- Limit simultaneous glows; reserve the brightest glow for active/playing states.

---

## Tailwind Template vs Card-mod — When to use which

### card-mod (HACS: card-mod)

- *Best for*: restyling core/custom cards you already like (media-control, mushroom/bubble, entities, history graph).
- *Pros*: tiny footprint; keeps all built-in behaviors; integrates with themes/HA variables; quickest path to “make it pretty”.
- *Cons*: fragile if you target deep internal selectors; you can’t change the card’s structure—only its styles.

### TailwindCSS Template Card (or any HTML/Template card using Tailwind utilities)

- *Best for*: bespoke, pixel-perfect sections (hero headers, composite tiles, neon dividers, custom stat rows) that don’t exist as stock cards.
- *Pros*: total control over layout/markup; utility classes make consistent styling fast; easier to encode your vaporwave/glass aesthetic exactly.
- *Cons*: heavier (extra CSS + larger DOM); you must wire entity states and actions yourself; you don’t get built-in card logic for free.

### Decision guide

- Need to repaint existing UI (e.g., frosted cards, neon borders, pill buttons)? → card-mod.
- Need a custom hero (artwork, headline, ghosted gradient, custom chips) or a composite (image + text + buttons in one block)? → Tailwind template.
- Want resilience across HA updates? → prefer theme variables + light card-mod; avoid deep selectors.
- Building a control that must mirror complex stock logic (e.g., media-control transport)? → don’t rebuild; skin with card-mod and surround with Tailwind sections if needed.

### Maintainability & performance

#### *card-mod*

- Prefer CSS vars over deep DOM queries (--ha-card-border-radius, --mdc-theme-primary, etc.).
- Avoid heavy selectors and :host ::part(*) shotgun styling; keep rules scoped to ha-card.
- Great for global polish: radii, shadows, blur, borders, fonts.

#### *Tailwind template*

- Keep the utility set tight (avoid enabling the full Tailwind preflight if possible).
- Limit reactivity to a few key entities; use state bindings and actions (HA 2024.8: service calls are “actions”) for taps/holds.
- Use it surgically: hero, section headers, stat ribbons, not for every single entity row.

### Practical patterns (ready-to-drop)

#### **1. card-mod: glass + neon outline on any card**

```yaml
type: media-control
entity: media_player.bedroom_tv_alpha
card_mod:
  style: |
    ha-card {
      backdrop-filter: blur(10px) saturate(120%);
      border-radius: 16px;
      border: 1px solid rgba(255,43,214,0.35);
      box-shadow: 0 8px 28px rgba(0,0,0,0.45), 0 0 18px rgba(0,229,255,0.25) inset;
    }
```

#### **2. Tailwind template: custom hero with action buttons**

```yaml
type: custom:tailwindcss-template-card
template: |
  <div class="p-4 rounded-2xl bg-gradient-to-br from-fuchsia-600/25 to-cyan-500/20 shadow-xl">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-semibold text-white/90">Bedroom Media</h3>
        <p class="text-white/60 text-sm">Tap to route video+audio via HDMI matrix</p>
      </div>
      <div class="flex gap-2">
        <button class="px-3 py-2 rounded-full bg-fuchsia-500/70 hover:bg-fuchsia-500 text-white"
          @click=${() => hass.callAction({action: 'perform-action', perform_action:'script.matrix_control', data:{source:'Apple TV', remote:'remote.bedroom_broadlink_rm3_alpha', device:'bedroom_hdmi_matrix', tv:'media_player.bedroom_tv_alpha'}})}>
          Apple TV
        </button>
        <button class="px-3 py-2 rounded-full bg-cyan-500/70 hover:bg-cyan-500 text-white"
          @click=${() => hass.callAction({action:'perform-action', perform_action:'script.matrix_control', data:{source:'Playstation 4', remote:'remote.bedroom_broadlink_rm3_alpha', device:'bedroom_hdmi_matrix', tv:'media_player.bedroom_tv_alpha'}})}>
          PS4
        </button>
      </div>
    </div>
  </div>
```

*(Note the 2024.8 **perform-action** usage.)*

### Recommendation

- Use a **hybrid**: theme + card-mod for global polish and for skinning stock/bubble cards; Tailwind templates only for the **few** areas where you need custom composition (hero header, neon section separators, stat chips).
- Keep Tailwind islands small and self-contained so updates don’t hurt you, and so mobile performance stays snappy.
