---
name: Tristan Scholz-Brennan
description: A career site built as an analyst's workbook, with ruled cells, row numbers, a formula bar, and sheet tabs.
colors:
  ground: "#f6f7f5"
  cell: "#ffffff"
  head: "#eceeeb"
  ink: "#111412"
  muted: "#4a524c"
  grid: "#d5dad5"
  select: "#c8f23a"
  select-gutter: "#b3d92f"
  deep: "#0d5c3d"
  titlebar-rule: "#3a413c"
  error-ref: "#b3261e"
typography:
  display:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(2.75rem, 7.6vw, 6rem)"
    fontWeight: 850
    lineHeight: 0.92
    letterSpacing: "-0.04em"
    fontVariation: "'wdth' 112"
  headline:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(2rem, 4.5vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 750
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  title-sm:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.1
  figure:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.01em"
    fontFeature: "'tnum' 1"
  lede:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
  prose:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.7
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "'tnum' 1"
  table:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "'tnum' 1"
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.5
  label-sm:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.5
    fontFeature: "'tnum' 1"
rounded:
  none: "0px"
spacing:
  hair: "0.35rem"
  xs: "0.5rem"
  sm: "0.75rem"
  md: "1rem"
  cell-y: "0.85rem"
  gutter: "3rem"
  gutter-narrow: "2.25rem"
  tabs-h: "2.75rem"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.cell}"
    rounded: "{rounded.none}"
    padding: "0.6rem 1rem"
    height: "2.75rem"
  button-primary-hover:
    backgroundColor: "{colors.deep}"
    textColor: "{colors.cell}"
  button-secondary:
    backgroundColor: "{colors.cell}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.6rem 1rem"
    height: "2.75rem"
  button-secondary-hover:
    backgroundColor: "{colors.select}"
    textColor: "{colors.ink}"
  tool:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.cell}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.35rem 0.7rem"
  tool-hover:
    backgroundColor: "{colors.select}"
    textColor: "{colors.ink}"
  cell:
    backgroundColor: "{colors.cell}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "0.85rem 1rem"
  cell-head:
    backgroundColor: "{colors.head}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "0.85rem 1rem"
  cell-selected:
    backgroundColor: "{colors.select}"
    textColor: "{colors.ink}"
    padding: "0.85rem 1rem"
  row-gutter:
    backgroundColor: "{colors.head}"
    textColor: "{colors.muted}"
    typography: "{typography.label-sm}"
    width: "3rem"
  table-head:
    backgroundColor: "{colors.head}"
    textColor: "{colors.ink}"
    padding: "0.6rem 1rem"
  tab:
    backgroundColor: "{colors.head}"
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    padding: "0 1.1rem"
    height: "2.75rem"
  tab-hover:
    backgroundColor: "{colors.cell}"
    textColor: "{colors.ink}"
  tab-active:
    backgroundColor: "{colors.cell}"
    textColor: "{colors.deep}"
  tag:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.15rem 0.5rem"
---

# Design System: Tristan Scholz-Brennan

## Overview

**Creative North Star: "The Workbook"**

The site is an analyst's workbook, built as a designed object. Every page is a sheet. A near-black title bar holds the name and the contact tools. A formula bar under it shows the active cell's reference and formula. Below that is a column-letter strip (A to L), a numbered row gutter, and rows of white cells separated by 1px grey hairlines. Sheet tabs stay fixed at the bottom of the viewport. The spreadsheet is the grammar, not a decoration: cells carry content, row numbers count real rows, and the formula bar reports real sources and computed values.

The density is moderate and even. Cells are generously padded, but nothing floats. All content sits inside a ruled cell. The palette is almost entirely cool neutrals. One lime selection fill is the loud colour, and it always means "selected". Deep green does the quieter work of links, the active tab, and comment markers. Archivo is the only typeface. It runs heavy and slightly widened at poster scale for the name, and plain at body sizes, with tabular numerals wherever figures appear.

The world rejects the usual portfolio of a hero with rounded cards. There are no soft corners anywhere and no floating surfaces.

**Key Characteristics:**
- Square corners everywhere (0 radius, enforced globally).
- 1px grey hairlines are the only dividers; there are no gaps between cells.
- One lime selection band per sheet; lime also marks hover on controls.
- Deep green for links, the active tab, and sourced-cell triangles.
- One authored motion: the selection outline gliding to the active cell.
- Archivo variable font, self-hosted, with tabular numerals on by default.

## Colors

Cool, faintly green-tinted neutrals, one acid-lime selection fill, and one deep forest green.

### Primary
- **Selection Lime** (#c8f23a): the selection fill. It fills the one full-width selected row (the "seeking" line on Home), the hover state of secondary buttons and title-bar tools, text `::selection`, and the 5px halo of the focus ring. It always means "this is selected or about to be acted on".
- **Selection Lime, Gutter** (#b3d92f): a slightly darker lime used only for the row number beside a selected row, so the gutter reads as part of the selection.

### Secondary
- **Ledger Green** (#0d5c3d): links (underlined, 1px, thickening to 2px on hover), the active sheet tab's text and 3px underline, the comment-marker triangle on sourced cells, the hover state of the primary button, and the text caret.

### Tertiary
- **#REF! Red** (#b3261e): spreadsheet error text, used only for the `#REF!` token on the 404 sheet.

### Neutral
- **Workbook Ink** (#111412): body text, the title bar ground, primary button fill, selection outline, focus outline, and the 2px rule over table totals.
- **Gridline Muted** (#4a524c): secondary text such as role lines, fact notes, row and column labels, status bar, inactive tabs, and the `fx` mark. It reaches 6.9:1 on the header grey.
- **Sheet Ground** (#f6f7f5): the page background behind the sheet, the status bar, and tag fills.
- **Cell White** (#ffffff): every content cell and the formula bar.
- **Header Grey** (#eceeeb): column-letter strip, row-number gutter, section header cells, table heads, the formula bar's leading slot, and the tab bar.
- **Hairline Grey** (#d5dad5): every 1px cell, row, table, and tab divider, plus the scrollbar thumb.
- **Title-bar Rule** (#3a413c): the 1px outline of the tools on the ink title bar.

### Named Rules
**The One Selection Rule.** Lime means selection. A sheet carries at most one selected row, and lime appears nowhere else at rest. It shows up on hover and focus, but never as decoration, as a background tint, or as a text colour.

**The Green Is Reference Rule.** Ledger green marks things that point somewhere else: links, the current tab, and sourced cells. Don't use it for headings or as a resting fill. Its only fill is the primary button's hover state.

## Typography

**Display Font:** Archivo (with system-ui, sans-serif)
**Body Font:** Archivo (with system-ui, sans-serif)

**Character:** A single grotesque at two widths and many weights. At the top of the scale it is a heavy, widened poster face (weight 850, width 112%). At body sizes it is a neutral, spreadsheet-like workhorse. The font is self-hosted as a variable woff2 file (weight 100 to 900, width 62% to 125%), preloaded, with `font-display: swap`.

### Hierarchy
- **Display** (850, clamp(2.75rem, 7.6vw, 6rem), 0.92, width 112%, -0.04em): the person's name on Home only, spanning all 12 columns.
- **Headline** (800, clamp(2rem, 4.5vw, 3.5rem), 1.1, -0.03em): the page title in the first row of every other sheet.
- **Title** (750, 1.375rem, 1.1, -0.01em): section names in header cells, and project names on the Projects sheet.
- **Title Small** (700, 1.0625rem): project names inside Home's featured cells.
- **Figure** (800, 1.25rem, 1.2): the headline value in a fact cell, with its note beneath at 0.875rem muted.
- **Lede** (400, 1.125rem, 1.6, max 62ch): the summary paragraph on Home.
- **Prose** (400, 1.0625rem, 1.7, max 66ch): long-form paragraphs on About, Contact, and Project detail.
- **Body** (400, 1rem, 1.5): default cell text. Bulleted lists cap at 60ch.
- **Table** (400, 0.9375rem): data table cells. Table heads are 700 at 0.8125rem.
- **Label** (600, 0.875rem): tools, tabs, status bar, formula bar, and secondary lines.
- **Label Small** (600, 0.75rem): column letters and row numbers.

### Named Rules
**The Tabular Everywhere Rule.** `font-variant-numeric: tabular-nums` is set on the body, so every figure (dates, months, GPA, row numbers) lines up in columns. Don't turn it off locally.

**The Wide Means Identity Rule.** Archivo's 112% width is reserved for the name (the display name and the title-bar brand) and the `#REF!` error token. All other text stays at normal width.

## Layout

The sheet is a stack of rows. Each row is a CSS grid of a row-number gutter (3rem) plus 12 equal columns (`minmax(0, 1fr)`). Cells span 2, 3, 4, 6, 8, 9, or 12 columns. Rows are full-bleed with no max-width container: the sheet runs edge to edge, the way a spreadsheet does. The 12 column hairlines are painted on every row as a background gradient. That way empty spans (blank cells) still show the grid, and a half-filled row reads as unfilled cells rather than empty space.

A CSS counter numbers the rows in the gutter. The column-letter strip above the first row labels A to L. The formula bar is sticky at the top. Its slots are a gutter-width blank, a 3rem name box, a 2.5rem `fx` mark, and the formula, which truncates with an ellipsis. The tab bar is fixed at the bottom (2.75rem tall), and the body reserves matching bottom padding.

Spacing rhythm: cells pad 0.85rem by 1rem. Inside a cell, gaps step through 0.35rem (list items, tags, fact notes), 0.5rem (button stacks, tool groups), 0.75rem (paragraph spacing), and 1rem (header cell gaps). The title bar and status bar indent their content by the gutter plus 0.75rem, so text lines up with the first column.

At 760px and below, the gutter narrows to 2.25rem and every row collapses to gutter plus one column. Cells stack inside the row, separated by a top hairline. Blank cells, column letters after A, and the `fx` mark are hidden. Tables marked to stack become label-value lists, each value prefixed with its column name in muted 600. The tabs stretch to fill the width at 0.75rem.

**The No Gaps Rule.** Cells touch. Separation comes from 1px hairlines, never from margins, gaps, or whitespace between boxes.

## Elevation & Depth

The system is flat. Depth comes from tone (white cells on header grey and the off-white ground) and from hairlines, never from drop shadows. `box-shadow` appears in only two places, both as flat marks with no blur and no offset: the lime focus halo (`0 0 0 5px`) and the active tab's inset 3px green underline. Layering is literal: the sticky formula bar (z 10), the fixed tab bar (z 10), and the selection outline (z 5) sit above the sheet without any shadow.

### Shadow Vocabulary
- **Focus halo** (`box-shadow: 0 0 0 5px #c8f23a`, with `outline: 2px solid #111412; outline-offset: 2px`): every keyboard focus. Inside fact cells the halo is dropped and the outline is inset (`outline-offset: -4px`).
- **Active-tab rule** (`box-shadow: inset 0 -3px 0 #0d5c3d`): the current sheet tab only.

### Named Rules
**The Flat Sheet Rule.** Nothing floats above the sheet. Don't add blurred or offset shadows. The only box-shadows are the focus halo and the tab underline.

## Shapes

Every corner is square. The global reset sets `border-radius: 0` on all elements and pseudo-elements. Borders are 1px hairline grey for structure, 1px ink for button outlines, and 2px ink for the selection outline and the rule above totals. Two small spreadsheet geometries recur. A sourced cell gets a 9px green right triangle in its top-right corner (a comment marker). The selection outline gets an 8px ink fill-handle square at its bottom-right corner, outlined in white.

## Components

### Buttons
Square ink blocks, solid and direct.
- **Shape:** square (0 radius), 1px ink border, minimum height 2.75rem, padding 0.6rem by 1rem, weight 700.
- **Primary:** ink fill with white text. Used once per action cell for the main act ("Email Tristan", "Email me", "Download resume").
- **Secondary:** white fill with ink text and an ink border.
- **Hover / Focus:** primary moves to ledger green (fill and border). Secondary fills with selection lime. Both transition background and colour over 120ms on the workbook ease. Focus uses the global halo.
- **Grouping:** buttons stack in a grid inside an action cell (0.5rem gap), or wrap in a row (0.5rem gap).

### Title-bar Tools
- **Style:** white 600 text at 0.875rem on the ink bar, with a 1px title-bar-rule outline, padded 0.35rem by 0.7rem (0.55rem by 0.8rem on narrow screens).
- **Hover:** lime fill and border with ink text.

### Cells / Containers
- **Corner Style:** square.
- **Background:** cell white. Header cells use header grey and lay out the section title and an optional link at opposite ends, aligned on the baseline. A selected row turns every cell lime.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px hairline on the right of each cell and the bottom of each row.
- **Internal Padding:** 0.85rem by 1rem. Table cells drop their padding and let the table rule itself.

### Data Tables
- **Style:** full-width and collapsed, 0.9375rem, with 1px hairlines between every cell and padding of 0.6rem by 1rem. The head is header grey at 700. Numeric columns are right-aligned and never wrap.
- **Totals:** the footer row is 800 weight under a 2px ink rule, like a spreadsheet sum.
- **Narrow:** stacked tables become label-value lists (described in Layout).

### Tags
- **Style:** 0.8125rem at 600, padded 0.15rem by 0.5rem, with a 1px hairline border on the sheet ground. Square. Static, with no selected state.

### Navigation
- **Sheet tabs** (primary navigation): fixed to the bottom and indented by the gutter. Labels are 0.875rem at 600 in muted text, with a hairline divider on the right of each tab. Hover lifts a tab to white with ink text. The current page (`aria-current="page"`) is white, ledger green, weight 800, with the inset green underline. On narrow screens the tabs fill the width at 0.75rem.
- **Status bar:** muted 0.875rem copyright and footer links on the sheet ground.

### Formula Bar (signature)
A sticky strip that echoes the sheet's active cell. Hovering, focusing, or tapping a cell that has a formula writes its cell reference (such as "A2") into the name box and its formula or source into the formula slot, for example `=SOURCE("…")`, `=DATEDIF(…)`, or `=TARGET(…)`. On narrow screens, references report column A. The bar is `aria-hidden`. Every source it shows is also in the page as text (a visually hidden "Source:" line in sourced cells), so the bar is never the only place information lives.

### Selection Outline (signature motion)
A 2px ink rectangle with a fill handle that glides to the active cell. Its transform transitions over 220ms on `cubic-bezier(0.16, 1, 0.3, 1)`. At rest it sits on the selected row, or on the first cell with a formula, and it returns there when the pointer leaves the sheet. After font swaps and resizes it re-places instantly, without animating. It is the only authored motion. Under `prefers-reduced-motion` it, and the button transitions, become instant.

## Do's and Don'ts

### Do:
- **Do** put every piece of content inside a ruled cell on the 12-column row grid, with spans of 2, 3, 4, 6, 8, 9, or 12.
- **Do** fill unused spans with blank cells so the grid still reads.
- **Do** give a cell a formula (a source, a computed value, or a target) when the fact has one, and mark sourced facts with the green comment triangle.
- **Do** keep figures tabular and right-align numeric table columns. Close sums with the 2px ink total rule.
- **Do** use the ink block for the single most important action in a cell, and the white outlined block for the rest.
- **Do** cap reading text at 60 to 66ch inside wide cells.

### Don't:
- **Don't** round any corner. The global reset is 0 and stays 0.
- **Don't** use lime for anything except selection, hover, and focus, and don't put more than one selected row on a sheet.
- **Don't** add blurred or offset drop shadows, or float cards with gaps between them.
- **Don't** add a second typeface, or use Archivo's widened 112% width outside the name and the `#REF!` token.
- **Don't** add motion beyond the selection outline's glide and the 120ms button colour change.
- **Don't** put information only in the formula bar. It is aria-hidden, so the same text must also exist in the cell.
