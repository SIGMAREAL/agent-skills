---
name: syxma-ui
description: Collection of custom UI design styles. Use when creating web interfaces, landing pages, dashboards, or any frontend design work. Each style has complete design system with colors, typography, components, and implementation patterns. Current styles: SYXMA-minimal (Notion-style, iOS colors, Chinese-optimized), SYXMA-minimal-edumindai (SYXMA-minimal base + green brand color, education-focused components).
---

# SYXMA-UI

A collection of custom UI design styles. Each style is a complete design system ready for implementation.

## Available Styles

### SYXMA-minimal
Notion-style layout with iOS system colors, optimized for Chinese reading. See [SYXMA-minimal.md](references/SYXMA-minimal.md) for complete design system.

**When to use:**
- Creating content-focused websites and applications
- Building documentation or knowledge base interfaces
- Designing dashboards with heavy Chinese text content
- Any project needing clean, distraction-free UI

**Key characteristics:**
- Content-first design, UI fades into background
- Large rounded corners, soft visual language
- iOS system colors (#007AFF blue, #34C759 green, etc.)
- System fonts, no external font loading
- Full 1:65 line height for Chinese readability

### SYXMA-minimal-edumindai
SYXMA-minimal base with green brand color and education-focused components. See [SYXMA-minimal-edumindai.md](references/SYXMA-minimal-edumindai.md) for complete design system.

**When to use:**
- Education platforms (teaching dashboards, question banks, exam generators)
- Learning management systems
- AI-assisted teaching tools
- Any education product needing clean, professional UI with green brand identity

**Key characteristics:**
- Inherits SYXMA-minimal: pill buttons, border cards, floating capsule toggles, 18px card radius
- Green brand color (#00C06B) replacing iOS blue
- Inter + PingFang SC font stack
- Extra components: gradient panel, dark panel, difficulty tags, skeleton loading, toast
- Two-column layout (1fr + 320px) for config/generation pages
- Page background #F7F8FA, max-width 1440px

## Quick Start

1. Choose a style that fits your project
2. Read the style guide in `references/[style-name].md`
3. Copy CSS variables from the style guide
4. Use the component patterns as starting point
5. Adapt as needed while maintaining design consistency

## Adding New Styles

To add a new style to SYXMA-UI:

1. Create a new reference file: `references/[style-name].md`
2. Document the complete design system:
   - Design philosophy and principles
   - Color system with hex values
   - Typography (fonts, sizes, weights, line-heights)
   - Spacing/spacing scale
   - Border radius values
   - Component patterns (buttons, cards, inputs, etc.)
3. Update this SKILL.md to list the new style

## Resources

### references/
Design system documentation for each style:
- `SYXMA-minimal.md` — Complete design system for the minimal style
- `SYXMA-minimal-edumindai.md` — Education-focused variant with green brand color

### assets/
HTML/CSS templates and boilerplate code for each style (coming soon).
