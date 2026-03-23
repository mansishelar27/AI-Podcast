# Finance AI Podcast — Design System
### Enterprise UI · Fluent 2 Inspired · v1.0

> **Purpose:** This document is the single source of truth for the upcoming frontend redesign.
> Review and approve this before any code changes begin.

---

## 1. Design Philosophy

| Principle | Description |
|---|---|
| **Clean over clever** | White space is a design element, not empty space |
| **Hierarchy first** | Every element should have a clear visual weight |
| **Subtle motion** | Transitions inform, they don't entertain |
| **Enterprise trust** | The UI should feel reliable, structured, and professional |

The current UI uses a **dark amber/gold theme**. The redesign shifts to a **light, white-first theme** — similar to Microsoft 365, Notion, or Linear — where color is used for accent and status only.

---

## 2. Color Tokens

### Primary Palette

```
--color-bg-base:        #FFFFFF      /* Page background */
--color-bg-surface:     #F5F5F5      /* Cards, sidebars, panels */
--color-bg-elevated:    #FAFAFA      /* Floating elements, modals */
--color-bg-overlay:     rgba(0,0,0,0.04)  /* Hover states */
```

### Brand Accent (Blue — Fluent 2 standard)

```
--color-accent:         #0F6CBD      /* Primary buttons, links, active states */
--color-accent-hover:   #115EA3      /* Button hover */
--color-accent-light:   #EFF6FC      /* Accent backgrounds, tags, badges */
--color-accent-border:  #B4D6F0      /* Accent-tinted borders */
```

### Neutral (Text & Borders)

```
--color-text-primary:   #1A1A1A      /* Headings, key labels */
--color-text-secondary: #424242      /* Body text, descriptions */
--color-text-muted:     #707070      /* Captions, placeholders */
--color-text-disabled:  #ABABAB      /* Disabled states */

--color-border:         #E0E0E0      /* Default borders, dividers */
--color-border-focus:   #0F6CBD      /* Focus rings */
```

### Semantic

```
--color-success:        #107C10      /* Publish success, online status */
--color-success-bg:     #F1FAF1
--color-warning:        #BC4B09      /* Warnings, caution */
--color-warning-bg:     #FEF7F3
--color-error:          #C50F1F      /* Errors, failures */
--color-error-bg:       #FEF0F1
--color-info:           #0F6CBD      /* Info banners */
--color-info-bg:        #EFF6FC
```

---

## 3. Typography

### Font Stack

```css
--font-base: 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
```

> Import `Inter` from Google Fonts as the cross-platform fallback when Segoe UI is unavailable.

### Type Scale

| Token | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| `--text-xs` | 11px | 400 | 16px | Labels, tags, captions |
| `--text-sm` | 12px | 400 | 16px | Secondary body, metadata |
| `--text-body` | 14px | 400 | 20px | Primary body text |
| `--text-body-strong` | 14px | 600 | 20px | Emphasized body |
| `--text-subtitle` | 16px | 600 | 22px | Card titles, section labels |
| `--text-title` | 20px | 600 | 28px | Page section headers |
| `--text-hero` | 28px | 700 | 36px | Main page title |
| `--text-display` | 36px | 700 | 44px | Hero, landing headers |

---

## 4. Spacing System

Based on a **4px base grid** (Fluent 2 standard).

```
--space-2:    2px
--space-4:    4px
--space-8:    8px
--space-12:   12px
--space-16:   16px
--space-20:   20px
--space-24:   24px
--space-32:   32px
--space-40:   40px
--space-48:   48px
--space-64:   64px
```

### Layout Rules
- **Component internal padding:** `16px` or `20px`
- **Section separation:** `32px` or `40px` — use whitespace, NOT heavy dividers
- **Card gap in grid:** `16px`
- **Sidebar width:** `280px` (news column)
- **Max content width:** `1280px` centered

---

## 5. Elevation & Shadow

Fluent 2 uses **soft, layered shadows** — never harsh drop shadows.

```
--shadow-2:   0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
--shadow-4:   0 2px 4px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
--shadow-8:   0 4px 8px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.05);
--shadow-16:  0 8px 16px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06);
--shadow-28:  0 14px 28px rgba(0,0,0,0.14), 0 6px 12px rgba(0,0,0,0.07);
--shadow-64:  0 32px 64px rgba(0,0,0,0.18), 0 12px 24px rgba(0,0,0,0.08);
```

| Component | Shadow level |
|---|---|
| Cards (rest) | `shadow-2` |
| Cards (hover) | `shadow-8` |
| Dropdowns, tooltips | `shadow-16` |
| Modals | `shadow-28` |
| Command palette | `shadow-64` |

---

## 6. Border Radius

```
--radius-2:    2px   /* Tags, chips */
--radius-4:    4px   /* Inputs, small buttons */
--radius-6:    6px   /* Buttons, form fields */
--radius-8:    8px   /* Cards, panels */
--radius-12:   12px  /* Large cards, modals */
--radius-16:   16px  /* Floating containers */
--radius-full:  9999px  /* Pills, toggles, avatars */
```

---

## 7. Motion & Transitions

All transitions: **200–300ms, ease-in-out** (Fluent 2 guideline).

```
--motion-fast:    100ms ease-in-out   /* Micro (hover color change) */
--motion-normal:  200ms ease-in-out   /* Default (scale, shadow, bg) */
--motion-slow:    300ms ease-in-out   /* Modal open, drawer, page section */
--motion-spring:  400ms cubic-bezier(0.34, 1.56, 0.64, 1)  /* Pop-in for cards/modals */
```

### Rules
- No transitions longer than 400ms
- Never animate layout properties (width, height) — use opacity + transform
- Prefer `transform: translateY(-2px)` on hover over scale for enterprise feel
- Modal: fade-in + subtle scale from `0.96 → 1.0`

---

## 8. Component Specs

### 8.1 Buttons

```
Primary:    bg #0F6CBD  · text #FFF   · hover #115EA3  · radius 6px · pad 8px 20px
Secondary:  bg #FFFFFF  · text #1A1A1A · border 1px #E0E0E0 · hover bg #F5F5F5
Ghost:      bg transparent · text #0F6CBD · hover bg #EFF6FC
Danger:     bg #C50F1F  · text #FFF   · hover #A30E1A
Disabled:   bg #F5F5F5  · text #ABABAB · cursor not-allowed
```

All buttons: `font-size 14px`, `font-weight 600`, `height 32px` (compact) or `36px` (default).

### 8.2 Cards

```
background:    var(--color-bg-surface)
border:        1px solid var(--color-border)
border-radius: var(--radius-8)
padding:       20px 24px
box-shadow:    var(--shadow-2)
transition:    box-shadow 200ms ease-in-out, transform 200ms ease-in-out

on hover:
  box-shadow:  var(--shadow-8)
  transform:   translateY(-1px)
```

### 8.3 Form Inputs

```
height:         32px (single-line) | auto (textarea)
padding:        6px 12px
border:         1px solid var(--color-border)
border-radius:  var(--radius-4)
font-size:      14px
background:     #FFFFFF

on focus:
  border-color: var(--color-border-focus)
  box-shadow:   0 0 0 2px rgba(15,108,189,0.15)
  outline:      none
```

### 8.4 Navigation / Tabs

```
Tab bar:        bottom border 2px #E0E0E0 (track)
Active tab:     bottom border 2px #0F6CBD · color #0F6CBD · font-weight 600
Inactive tab:   color #707070 · font-weight 400
Hover tab:      color #1A1A1A · bg rgba(0,0,0,0.03)
Tab padding:    12px 20px
```

### 8.5 Modals

```
Overlay:        rgba(0,0,0,0.40) backdrop
Container:      bg #FFFFFF · radius 12px · shadow var(--shadow-28)
Max width:      520px
Padding:        32px
Animation:      fade + scale 0.96→1.0 over 300ms spring
```

### 8.6 News Sidebar

```
Width:          280px  (fixed)
Background:     var(--color-bg-surface)
Border-left:    1px solid var(--color-border)
Padding:        20px 16px
Item separator: subtle bottom border or 12px gap
```

### 8.7 Audio Player

```
Background:     var(--color-bg-surface)
Border:         1px solid var(--color-border)
Border-radius:  var(--radius-8)
Progress bar:   accent color fill on neutral track
Waveform bars:  accent color, subtle animation
```

### 8.8 Status / Badge Chips

```
Padding:    4px 10px
Radius:     var(--radius-full)
Font-size:  12px
Font-weight: 600
Variants:   use semantic bg/text colors from Section 2
```

---

## 9. Page Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER  (64px height, white bg, bottom border)             │
│  Logo  ·  App Name  ·  [Nav items if needed]                │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│   MAIN CONTENT AREA             │   NEWS SIDEBAR  (280px)   │
│   (flex-grow, max 1280px)       │   Market & Financial News │
│                                 │                           │
│   ┌─────────────────────────┐   │   • Headline 1            │
│   │ TABS: Search | Create   │   │   • Headline 2            │
│   └─────────────────────────┘   │   • Headline 3            │
│                                 │   ...                     │
│   [Tab content below]           │                           │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

- Header is **sticky**
- Layout is `display: flex` — sidebar stays fixed, content scrolls
- Mobile: sidebar collapses below content

---

## 10. What Changes vs Current UI

| Current (Dark Gold) | New (Enterprise White) |
|---|---|
| Dark background `#070b14` | White base `#FFFFFF` |
| Gold accent `#eab308` | Blue accent `#0F6CBD` |
| DM Serif Display + DM Sans fonts | Segoe UI / Inter |
| Inline CSS string in App.js | CSS custom properties in `index.css` |
| No hover effects on cards | Soft lift on hover |
| Heavy decorative header gradient | Clean flat header with subtle border |
| Emoji-heavy buttons (`🚀 Publish`) | Icon-light, text-first buttons |
| Hardcoded hex values throughout | Design token variables |

---

## 11. Implementation Plan (Phases)

| Phase | Scope | Files Touched |
|---|---|---|
| **1 — Tokens** | Extract all CSS variables into `index.css` `:root` | `index.css` |
| **2 — Base** | Body, header, layout, sidebar | `App.js` (CSS block) |
| **3 — Cards** | Podcast cards, news items | `App.js` |
| **4 — Forms** | Create tab, inputs, selects, buttons | `App.js` |
| **5 — Modal** | All 3 modal stages redesigned | `App.js` |
| **6 — Audio Player** | CustomAudioPlayer styled | `App.js` |
| **7 — Polish** | Transitions, focus states, accessibility | All |

---

## 12. Accessibility Requirements

- All interactive elements must have `:focus-visible` ring (`2px solid #0F6CBD, offset 2px`)
- Minimum contrast ratio: **4.5:1** for body text, **3:1** for large text
- No color-only status indicators — pair color with icon or text
- Keyboard navigable tabs and modals

---

> **Next Step:** Review and approve this document, then we begin Phase 1 (Tokens).
> Any changes to colors, fonts, or component specs should be made here first.
