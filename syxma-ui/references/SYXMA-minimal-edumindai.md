# SYXMA-minimal-edumindai Design System

基于 SYXMA-minimal 的设计哲学（边框卡片、药丸按钮、浮动胶囊切换），融合 EduMindAI 的品牌色与教育场景组件。

## Design Philosophy

> **Content First + Education Focused** — 保持 SYXMA-minimal 的克制与留白，用绿色品牌色传递教育场景的活力与信任感。

## Design Principles

1. **SYXMA-minimal 基因** — 边框卡片、药丸按钮、浮动胶囊、大圆角，UI 隐于内容之后
2. **绿色品牌体系** — `#00C06B` 为主色调，传递成长与积极的教育感
3. **教育场景增强** — 新增难度标签、知识点可选标签、深色面板、渐变面板等教育专属组件
4. **中文优化** — Inter + PingFang SC 字体栈，1.65 行高，500 默认字重

## Color System

### Brand Colors

```css
--color-primary: #00C06B;         /* 品牌绿 */
--color-primary-hover: #00A85A;   /* 深绿 hover */
--color-primary-light: #E8F8F0;   /* 浅绿背景 */
--color-primary-disabled: #B8EFD5; /* 禁用态 */
--color-primary-focus-ring: rgba(0, 192, 107, 0.1); /* 聚焦光环 */
```

### Neutral Colors

```css
--color-bg: #FFFFFF;              /* 纯白 */
--color-bg-page: #F7F8FA;        /* 页面底色（浅灰） */
--color-bg-muted: #F5F5F7;       /* 次级背景 */
--color-bg-hover: #F0F0F0;       /* Hover 态 */
--color-bg-active: #E5E7EB;      /* Active/选中 */
```

### Text Colors

```css
--color-text: #1A1A2E;           /* 主文本（深蓝黑） */
--color-text-secondary: #595959; /* 二级文本 */
--color-text-muted: #6B7280;     /* 辅助文本 */
--color-text-placeholder: #9CA3AF; /* 占位符 */
--color-text-tertiary: #BFBFBF;  /* 最淡文本 */
```

### Border Colors

```css
--color-border: #E5E7EB;         /* 默认边框 */
--color-border-strong: #D1D1CF;  /* 强调边框 */
```

### Semantic / Functional Colors

```css
--color-success: #00C06B;        /* 成功（与品牌色一致） */
--color-success-light: #E8F8F0;
--color-warning: #FAAD14;        /* 警告（Ant Design 橙） */
--color-warning-light: #FFF7E6;
--color-error: #FF4D4F;          /* 错误（Ant Design 红） */
--color-error-light: #FFF1F0;
--color-info: #1890FF;           /* 信息（Ant Design 蓝） */
--color-info-light: #E6F7FF;
```

### Dark Panel Colors

```css
--color-dark: #1A1A2E;           /* 深色面板背景 */
--color-dark-hover: #2D2D4A;     /* 深色面板 hover */
```

### Difficulty Colors (教育专属)

```css
--color-easy: #52C41A;           /* 基础 — 绿 */
--color-easy-bg: #F6FFED;
--color-medium: #FAAD14;         /* 中等 — 橙 */
--color-medium-bg: #FFFBE6;
--color-hard: #FF4D4F;           /* 困难 — 红 */
--color-hard-bg: #FFF1F0;
```

## Typography

### Font Stack

```css
font-family:
    'Inter', 'PingFang SC',
    'Microsoft YaHei',
    -apple-system, sans-serif;
```

### Type Scale

| Usage | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|------------|----------------|
| Page Title | 28px | 700 | 1.3 | 0em |
| H1 / Section Title | 18px | 700 | 1.4 | 0em |
| H2 | 16px | 600 | 1.45 | 0em |
| H3 / Card Title | 15px | 600 | 1.45 | 0em |
| Body | 14px | 500 | 1.65 | 0em |
| Small | 13px | 500 | 1.6 | 0em |
| Caption | 11px | 600 | 1.4 | 0.05em |
| Stat Value | 28px | 700 | 1.2 | 0em |

### Typography Rules

- **Default weight 500** — Medium weight for better readability
- **Line height 1.65** — Optimized for Chinese characters
- **System fonts + Inter** — Inter for Latin, PingFang SC for Chinese
- **No negative letter-spacing** — Always 0em or positive

## Spacing Scale (8px Grid)

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
--radius-xs: 4px;       /* 难度标签、题型标签 */
--radius-sm: 8px;       /* 小元素、侧边栏项 */
--radius-md: 12px;      /* 中等元素 */
--radius-lg: 16px;      /* 大卡片备用 */
--radius-pill: 26px;    /* EduMindAI Dark 按钮 */
--radius-full: 9999px;  /* 药丸按钮、知识点标签、切换组 */

/* 常用固定值 */
/* 卡片: 18px */
/* 输入框: 14px */
/* 提示信息: 14px */
```

## Shadows (仅用于特殊面板)

普通卡片使用边框而非阴影（SYXMA-minimal 哲学）。阴影仅用于 Toast、渐变面板等悬浮元素。

```css
--shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.04);
--shadow-md: 0 2px 12px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 4px 20px rgba(0, 0, 0, 0.1);
--shadow-toast: 0 4px 16px rgba(0, 0, 0, 0.12);
```

## Components

### Button (药丸形)

所有常规按钮为 `border-radius: 9999px` 药丸形。

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

/* Primary */
.btn-primary {
    background: #00C06B;
    color: white;
}
.btn-primary:hover { background: #00A85A; }

/* Outline */
.btn-outline {
    background: transparent;
    color: #00C06B;
    border: 1.5px solid #00C06B;
}
.btn-outline:hover { background: #E8F8F0; }

/* Secondary */
.btn-secondary {
    background: #F5F5F7;
    color: #1A1A2E;
}

/* Ghost */
.btn-ghost {
    background: transparent;
    color: #6B7280;
}
.btn-ghost:hover { background: #F5F5F7; }

/* Danger — 浅底，hover 变实底 */
.btn-danger {
    background: #FFF1F0;
    color: #FF4D4F;
}
.btn-danger:hover { background: #FF4D4F; color: white; }

/* Dark — 唯一非药丸，26px 胶囊 */
.btn-dark {
    background: #1A1A2E;
    color: white;
    border-radius: 9999px;
    padding: 14px 40px;
    font-size: 16px;
    font-weight: 600;
}

/* Loading */
.btn-loading {
    background: #B8EFD5;
    color: white;
    cursor: not-allowed;
}

/* Small */
.btn-sm { padding: 8px 14px; font-size: 13px; }
```

### Tag / Badge

#### 知识点标签（可选中，药丸形）

```css
.tag {
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 20px;
}

/* 默认 */
.tag-primary { background: #E8F8F0; color: #00C06B; }

/* 选中 */
.tag-primary-active { background: #00C06B; color: white; }
```

#### 难度标签（方形，小写）

```css
.tag-difficulty {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.tag-easy { background: #F6FFED; color: #52C41A; }    /* 基础 */
.tag-medium { background: #FFFBE6; color: #FAAD14; }  /* 中等 */
.tag-hard { background: #FFF1F0; color: #FF4D4F; }    /* 困难 */
```

#### 题型标签（灰底方形）

```css
.tag-gray {
    background: #F5F5F5;
    color: #595959;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 12px;
}
```

### Card (边框卡片)

普通卡片使用边框，不使用阴影。18px 大圆角。

```css
.card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 18px;
    padding: 20px;
    transition: border-color 0.12s, box-shadow 0.12s;
}

.card:hover {
    border-color: #D1D1CF;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
```

### Green Gradient Card (渐变面板)

用于教学进度、核心数据展示。

```css
.card-gradient {
    background: linear-gradient(135deg, #00C06B 0%, #00A85A 100%);
    border-radius: 18px;
    padding: 24px;
    color: white;
}
```

### Dark Card (深色面板)

用于考点覆盖看板等数据面板。

```css
.card-dark {
    background: #1A1A2E;
    border-radius: 18px;
    padding: 20px;
    color: white;
}
```

### Input

```css
.input {
    width: 100%;
    padding: 12px 16px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    font-size: 14px;
    font-weight: 500;
    color: #1A1A2E;
    transition: border-color 0.12s;
}

.input:focus {
    outline: none;
    border-color: #00C06B;
    box-shadow: 0 0 0 3px rgba(0, 192, 107, 0.1);
}

.input::placeholder { color: #9CA3AF; }
```

Textarea 额外设置：`resize: vertical; min-height: 120px; line-height: 1.6;`

### Toggle Group (浮动胶囊)

SYXMA-minimal 风格的浮动分段控制器。

```css
.toggle-group {
    display: inline-flex;
    background: #F5F5F7;
    border-radius: 9999px;
    padding: 3px;
}

.toggle-item {
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #6B7280;
    border-radius: 9999px;
    border: none;
    background: transparent;
    transition: all 0.12s;
}

.toggle-item.active {
    background: #FFFFFF;
    color: #1A1A2E;
    font-weight: 600;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
```

### Progress Bar

```css
.progress-bar {
    height: 4px;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 2px;
    overflow: hidden;
}

/* 深色面板内 */
.progress-bar-dark { background: rgba(255, 255, 255, 0.15); }

.progress-fill {
    height: 100%;
    background: #00C06B;
    border-radius: 2px;
    transition: width 0.6s ease;
}
```

### Notice / Alert

```css
.notice {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.65;
}

.notice-success { background: #E8F8F0; color: #00C06B; }
.notice-info    { background: #E6F7FF; color: #1890FF; }
.notice-warning { background: #FFF7E6; color: #D48806; }
.notice-error   { background: #FFF1F0; color: #FF4D4F; }
```

### Toast

固定在页面右下角，带左侧色条。

```css
.toast {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    font-size: 14px;
    background: #FFFFFF;
    animation: slideIn 0.3s ease;
}

.toast-success { border-left: 3px solid #00C06B; }
.toast-error   { border-left: 3px solid #FF4D4F; }
.toast-warning { border-left: 3px solid #FAAD14; }
```

自动消失：成功/信息 2 秒，错误/警告 4 秒。

### Skeleton (骨架屏)

```css
.skeleton {
    background: linear-gradient(90deg, #F0F0F0 25%, #E0E0E0 50%, #F0F0F0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### Sidebar

- **Width:** 260px fixed
- **Background:** `#FFFFFF` (白底，与 SYXMA-minimal 一致)
- **Border:** 1px right border
- **Active item:** `background: #E8F8F0; color: #00C06B;` (品牌浅绿)

### Top Navigation

- **Height:** 64px
- **Position:** Sticky, fixed to top
- **Background:** `rgba(255, 255, 255, 0.92)` with backdrop blur
- **Border:** 1px bottom border

## Layout Patterns

### Page Structure

```
┌─────────────────────────────────────────────┐
│  Sidebar (260px)  │  Main Content              │
│  - Search         │  - Topbar (64px, blur)     │
│  - Navigation     │  - Page Header             │
│  - User Info      │  - Content (max 1440px)    │
└─────────────────────────────────────────────┘
```

### Two-Column Layout (配置页/生成页)

```css
.layout-2col {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 32px;
    align-items: start;
}
```

### Grid System

```css
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
```

### Page Content

```css
max-width: 1440px;
margin: 0 auto;
padding: 40px 48px 80px;
```

## Icon Usage

- Use **Lucide** style SVG icons
- Size: 24x24px standard, 18px for sidebar, 16px for inline
- Stroke width: 1.5
- Linecap: round
- Linejoin: round
- Fill: none
- Stroke: currentColor

## Animation

- **Duration:** 0.12s for interactive transitions (hover, focus)
- **Duration:** 0.6s for progress bar fills
- **Duration:** 0.3s for Toast slide-in
- **Easing:** ease-out (default), ease (progress)
- **Skeleton:** 1.5s infinite shimmer

## Differences from SYXMA-minimal

| Aspect | SYXMA-minimal | SYXMA-minimal-edumindai |
|--------|--------------|------------------------|
| Brand Color | `#007AFF` (iOS Blue) | `#00C06B` (Green) |
| Font Stack | System fonts only | Inter + PingFang SC |
| Text Color | `#1A1A1A` | `#1A1A2E` (深蓝黑) |
| Page Background | `#FFFFFF` | `#F7F8FA` (浅灰) |
| Semantic Colors | iOS system colors | Ant Design colors |
| New Components | — | Gradient card, Dark card, Skeleton, Toast, Difficulty tags |
| Layout | Single column | Two-column (1fr + 320px) |
| Page Max Width | 900px | 1440px |

## Implementation Notes

1. 卡片始终使用边框而非阴影（SYXMA-minimal 哲学）
2. 药丸按钮 `border-radius: 9999px`，不使用方形按钮
3. 切换组使用浮动胶囊而非方形分段控件
4. 深色面板和渐变面板是例外，可使用实底无边框
5. Input focus 有绿色 box-shadow 光环（EduMindAI 特色）
6. 动画时长 0.12s，保持轻快
7. 知识点标签为药丸形可选中，难度标签为方形小标签
