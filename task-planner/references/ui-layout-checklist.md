# UI Layout Task Checklist

For any task involving page layout or sidebar/panel placement.

## Before Writing task.json Steps

**Read these files first** (do not guess from memory):
1. Target route's `layout.tsx` — establishes what's already fixed-positioned outside `{children}`
2. Target route's `page.tsx` — establishes what renders inside `{children}`

Then answer:
- Which elements already exist in `layout.tsx`? (sidebars, navbars, shells)
- What renders as `{children}`? (everything in page.tsx)
- Where should the new element live? (layout = global/fixed; page = content-specific)

## Next.js App Router Rule

```
layout.tsx  → fixed/global shell (sidebars, navbars, toolbars)
page.tsx    → renders as {children} INSIDE layout's white card
```

**Common mistake**: Adding a sidebar inside `page.tsx` when it should be a `fixed aside` in `layout.tsx`.

## ASCII Layout Verification

Before writing steps, draw the final DOM structure:
```
layout.tsx:
  <aside fixed left>   ← left sidebar
  <aside fixed right>  ← right panel (if needed)
  <div pl-64 pr-72>
    <div white-card>
      {children}       ← page.tsx renders here
    </div>
  </div>

page.tsx (renders as {children}):
  <div flex-1 flex-col>
    TOP HEADER
    MIDDLE CONTENT (flex-1 overflow-y-auto)
    BOTTOM NAV
  </div>
```

Confirm: is the target element in the right file?

## Lesson Learned

A multi-session layout failure was caused by skipping this read-first step. The fix only became clear when the user said: "look at how the existing sidebar in layout.tsx works, mirror that pattern." Reading layout.tsx before planning would have avoided all iterations.
