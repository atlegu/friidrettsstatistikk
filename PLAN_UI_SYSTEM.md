# UI Typography & Density System Implementation Plan

## Overview
Transform the current UI to a dense, statistics-first design that prioritizes scanability over decoration.

---

## Phase 1: Global Typography System

### 1.1 Update `globals.css`

Add typography utilities and base styles:

```css
/* Typography utilities */
.tabular-nums {
  font-feature-settings: "tnum" 1, "lnum" 1;
  font-variant-numeric: tabular-nums lining-nums;
}

/* Base text adjustments */
html {
  font-size: 14px; /* Base size for desktop */
}

@media (max-width: 640px) {
  html {
    font-size: 14px; /* Keep same on mobile - don't increase */
  }
}
```

### 1.2 Update `layout.tsx`

Configure Inter with proper settings:
- Add `font-feature-settings` for tabular numbers globally
- Remove any Geist font references

### 1.3 Create Typography CSS Variables

```css
:root {
  /* Typography scale */
  --text-xs: 0.75rem;      /* 10.5px - ultra small */
  --text-sm: 0.8125rem;    /* 11.4px - secondary info */
  --text-base: 0.875rem;   /* 12.25px - table cells (scaled from 14px base) */
  --text-md: 1rem;         /* 14px - body text */
  --text-lg: 1.125rem;     /* ~16px - subsection h3 */
  --text-xl: 1.286rem;     /* 18px - section h2 */
  --text-2xl: 1.571rem;    /* 22px - page h1 */

  /* Line heights */
  --leading-tight: 1.4;
  --leading-normal: 1.5;
}
```

---

## Phase 2: Spacing & Density System

### 2.1 Create Spacing Variables

```css
:root {
  /* Spacing scale (4px base) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */

  /* Component-specific */
  --table-row-height-compact: 30px;
  --table-row-height-comfortable: 36px;
  --card-padding: var(--space-3);  /* 12px default */
  --section-gap: var(--space-6);   /* 24px between sections */
}
```

### 2.2 Create Density Toggle Utility

Add a data attribute system for density:
```css
[data-density="compact"] {
  --table-row-height: 30px;
  --card-padding: 8px;
}

[data-density="comfortable"] {
  --table-row-height: 36px;
  --card-padding: 12px;
}
```

---

## Phase 3: Update UI Components

### 3.1 Update Table Component (`table.tsx`)

**Changes:**
- TableHead: `h-10` → `h-8` (32px), font-size 12-13px, text-muted-foreground
- TableCell: padding `p-2` → `px-3 py-1.5`, font-size 13-14px
- TableRow: reduce hover background intensity
- Add `.tabular-nums` utility class for numeric columns

```tsx
// TableHead changes
className={cn(
  "h-8 px-3 text-left align-middle text-xs font-semibold text-muted-foreground whitespace-nowrap",
  className
)}

// TableCell changes
className={cn(
  "px-3 py-1.5 align-middle text-[13px] whitespace-nowrap",
  className
)}
```

### 3.2 Update Card Component (`card.tsx`)

**Changes:**
- Reduce default padding from 24px to 12-16px
- Remove shadow or reduce to minimal
- Tighten gap between header and content

```tsx
// Card: reduce gap
className={cn(
  "bg-card text-card-foreground flex flex-col gap-3 rounded-lg border py-3",
  className
)}

// CardHeader: reduce padding
className={cn(
  "px-4 pb-2",
  className
)}

// CardContent
className={cn("px-4", className)}
```

### 3.3 Update Badge Component (`badge.tsx`)

**Changes:**
- Font-size: 11px
- Font-weight: 500-600
- Only uppercase for status labels (PB, SB, NR, DQ)

```tsx
const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-1.5 py-0.5 text-[11px] font-semibold ...",
  ...
)
```

---

## Phase 4: Update Page Components

### 4.1 AthleteHeader.tsx

**Changes:**
- h1: `text-3xl sm:text-4xl` → `text-[22px] sm:text-[24px] font-semibold`
- Reduce avatar size: `h-32 w-32` → `h-20 w-20`
- Tighten spacing: `mb-8` → `mb-6`, `gap-6` → `gap-4`
- Stats text: `text-sm` → `text-[13px]`

### 4.2 PersonalBestsSection.tsx

**Changes:**
- Remove `font-mono` from performance values
- Add `tabular-nums` class instead
- Table header: `py-2` → `py-1.5`, add `text-xs text-muted-foreground`
- Table cells: `py-2` → `py-1.5`
- Card title: `text-lg` → `text-base font-semibold`

### 4.3 ResultsSection.tsx

**Changes:**
- Same table density updates
- Filter bar: ensure 40-44px height, sticky positioning
- Reduce padding in expandable sections

### 4.4 ProgressionChart.tsx

**Changes:**
- Chart height: Consider reducing from 300px
- Table below: Apply same compact styling

### 4.5 TopPerformancesCard.tsx

**Changes:**
- Apply compact table styling
- Reduce card header size

---

## Phase 5: Performance Numbers (Critical)

**Remove `font-mono` entirely from athletic performances.**

Create a utility class for numeric data display:

```css
.perf-value {
  font-feature-settings: "tnum" 1, "lnum" 1;
  font-variant-numeric: tabular-nums lining-nums;
  /* Keep proportional spacing for letters in times like "1:45.32" */
}
```

Apply to all performance displays via a shared component or class.

---

## Phase 6: Link Styling

**Changes:**
- Links: No underline by default
- Hover: Add underline
- Color: Use primary accent color only

```css
a {
  color: hsl(var(--primary));
  text-decoration: none;
}

a:hover,
a:focus {
  text-decoration: underline;
}
```

Or via Tailwind: Remove `hover:underline` and make underline default behavior via base styles.

---

## Files to Modify

1. **`globals.css`** - Typography scale, spacing variables, utilities
2. **`layout.tsx`** - Font configuration
3. **`table.tsx`** - Compact table styling
4. **`card.tsx`** - Reduced padding/gaps
5. **`badge.tsx`** - Smaller, uppercase for status
6. **`AthleteHeader.tsx`** - Heading sizes, spacing
7. **`PersonalBestsSection.tsx`** - Table density, remove font-mono
8. **`ResultsSection.tsx`** - Table density, sticky filters
9. **`ProgressionChart.tsx`** - Compact table
10. **`TopPerformancesCard.tsx`** - Compact styling

---

## Anti-Pattern Checklist

Before completion, verify:
- [ ] No excessive whitespace between table rows
- [ ] No giant headers (max h1 = 24px)
- [ ] No large card shadows/padding for data tables
- [ ] No hidden critical info behind tabs (overview shows key data)
- [ ] No font-mono on performance values
- [ ] No increased font sizes on mobile "to fill space"

---

## Testing

After implementation:
1. Visual comparison with Tilastopaja/World Athletics for density
2. Test on 1920x1080 desktop - should show lots of data
3. Test table scrolling on mobile
4. Verify tabular numbers align correctly in columns
5. Check filter bar stickiness on scroll

---

## Questions for You

1. **Density toggle**: Should I implement a UI toggle for compact/comfortable, or just default to compact?

2. **Color accent**: The current primary is grayscale. Do you want to introduce a color accent (e.g., blue) for links and interactive elements?

3. **Dark mode**: Should the density/typography changes also apply to dark mode, or is that lower priority?
