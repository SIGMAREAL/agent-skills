# SYXMA-minimal Design System

Notion-style layout, iOS system colors, optimized for Chinese reading experience.

## Design Philosophy

> **Content First** — UI should be invisible, letting users focus on content itself

## Design Principles

1. **Content Priority** — UI fades into background, content is the hero
2. **Consistency** — Unified spacing, typography, and color across all elements
3. **Efficiency** — Reduce clicks and thinking, help users achieve goals quickly
4. **Chinese Optimized** — System fonts, 1.65 line-height, proper character spacing

## Color System

### Base Colors

```css
--color-bg: #FFFFFF;          /* Pure white */
--color-bg-muted: #F5F5F7;    /* Light gray background */
--color-bg-hover: #EAEAEA;    /* Hover state */
--color-bg-active: #E5E5E7;   /* Active/selected */
```

### Text Colors

```css
--color-text: #1A1A1A;        /* Primary text */
--color-text-muted: #6E6E73;  /* Secondary text */
--color-text-secondary: #AEAEB2; /* Tertiary text */
--color-text-tertiary: #D1D1D6; /* Placeholder */
```

### Border Colors

```css
--color-border: #E8E8E6;      /* Subtle borders */
--color-border-strong: #D1D1CF; /* Stronger borders */
```

### Semantic Colors (iOS System)

```css
--color-primary: #007AFF;      /* Blue */
--color-primary-hover: #0056CC;
--color-primary-light: rgba(0, 122, 255, 0.1);

--color-success: #34C759;      /* Green */
--color-success-light: rgba(52, 199, 89, 0.1);

--color-warning: #FF9500;      /* Orange */
--color-warning-light: rgba(255, 149, 0, 0.1);

--color-error: #FF3B30;        /* Red */
--color-error-light: rgba(255, 59, 48, 0.1);

--color-info: #AF52DE;         /* Purple */
--color-info-light: rgba(175, 82, 222, 0.1);
```

## Typography

### Font Stack

```css
font-family:
    -apple-system, BlinkMacSystemFont,
    "SF Pro Text", "PingFang SC",
    "Microsoft YaHei",
    "Noto Sans SC", "Source Han Sans SC",
    system-ui, sans-serif;
```

### Type Scale

| Usage | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|------------|----------------|
| Page Title | 42px | 600 | 1.2 | 0em |
| H1 | 24px | 600 | 1.35 | 0em |
| H2 | 18px | 600 | 1.4 | 0em |
| H3 | 15px | 600 | 1.45 | 0em |
| Body | 15px | 500 | 1.65 | 0em |
| Small | 13px | 500 | 1.6 | 0em |
| Caption | 11px | 600 | 1.4 | 0.05em |

### Typography Rules

- **No negative letter-spacing** — Always 0em or positive
- **Default weight 500** — Medium weight for better readability
- **Line height 1.65** — Optimized for Chinese characters
- **System fonts only** — No external font loading

## Spacing Scale

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
```

## Border Radius

```css
--radius-sm: 8px;     /* Small elements */
--radius-md: 10px;    /* Medium elements */
--radius-lg: 14px;    /* Cards, inputs */
--radius-xl: 18px;    /* Large cards */
--radius-full: 9999px; /* Pills (buttons, tags) */
```

## Components

### Button

```css
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 9999px;
    border: none;
    cursor: pointer;
    transition: all 0.12s;
}

.btn-primary {
    background: var(--color-primary);
    color: white;
}

.btn-secondary {
    background: var(--color-bg-muted);
    color: var(--color-text);
}

.btn-ghost {
    background: transparent;
    color: var(--color-text-muted);
}
```

### Tag (Label)

```css
.tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
    border-radius: 9999px;
}
```

### Card

```css
.card {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 18px;
    padding: 20px;
    transition: border-color 0.12s, box-shadow 0.12s;
}

.card:hover {
    border-color: var(--color-border-strong);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
```

### Input

```css
.input {
    width: 100%;
    padding: 12px 16px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 14px;
    font-size: 14px;
    font-family: inherit;
    font-weight: 500;
    color: var(--color-text);
}

.input:focus {
    outline: none;
    border-color: var(--color-primary);
}
```

### Sidebar

- **Width:** 260px fixed
- **Background:** `#F5F5F7` (muted)
- **Border:** 1px right border

### Top Navigation

- **Position:** Sticky, fixed to top
- **Background:** `rgba(255, 255, 255, 0.9)` with backdrop blur
- **Border:** 1px bottom border

## Layout Patterns

### Page Structure

```
┌─────────────────────────────────────────┐
│  Sidebar (260px)  │  Main Content          │
│  - Search         │  - Topbar (breadcrumb)  │
│  - Navigation     │  - Page Header          │
│                   │  - Content Area         │
└─────────────────────────────────────────┘
```

### Grid System

```css
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-6 { grid-template-columns: repeat(6, 1fr); }
```

## Icon Usage

- Use **Lucide** style SVG icons
- Stroke width: 1.75
- Linecap: round
- Linejoin: round
- Fill: none
- Stroke: currentColor

## Animation

- **Duration:** 0.12s for fast transitions
- **Easing:** Ease-out
- **Purpose:** Hover states, focus states, dropdowns

## Accessibility

- Focus indicators on all interactive elements
- Keyboard navigation support
- ARIA labels where needed
- Color contrast ratio 4.5:1 minimum

## Implementation Notes

1. Always use system fonts — no external font files
2. Letter-spacing is always 0em — never negative
3. All text elements have minimum 500 font weight
4. Round numbers (9999px) for pill-shaped elements
5. Backdrop blur for sticky headers
6. Subtle borders (#E8E8E6) for separation
