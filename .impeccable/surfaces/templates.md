---
version: 1
slug: "templates"
primary_target: "templates"
related_targets: ["templates/base.html","static/css/site.css"]
---

# Surface brief: career site (all public pages)

Scope: every public page (Home, About, Experience, Projects, Project detail, Resume, Contact, 404). Visitor mode: Persuade.
Audience and job: recruiters screening full-time Data / Business Analyst candidates (May 2027 grad), deciding in under a minute whether to reach out.
Action: email Tristan, download the resume PDF, or open LinkedIn, all working from the first viewport.
Constraints: brief-pinned "modern, sharp edges", so no rounded corners anywhere. No headshot. Content stays in the database, and the fallback mode must still render.

## Direction contract

THESIS: The site is a confidently designed analyst's workbook: ruled cells, row numbers, a formula bar, and sheet tabs. It refuses the category's hero-plus-rounded-cards portfolio and every soft corner.

OWN-WORLD: The ground is a cool off-white with white cells, divided only by 1px grey hairlines. The ink is near-black. One lime selection fill (#C8F23A) is the only loud colour, and it owns a full-width band. Deep green (#0D5C3D) is used for links, the active tab, and the comment-marker triangles. Type is Archivo, self-hosted: heavy at poster scale for the name, normal width for body, tabular numerals everywhere data sits. Buttons are square ink blocks.

STORY: A visitor learns who Tristan is, sees that he's seeking DA/BA roles from May 2027, finds facts backed by sources (cell comments shown in the formula bar), sees computed months of experience, and acts by emailing or downloading.

FIRST VIEWPORT: A title bar at the top holds the name link plus Email, Resume PDF, and LinkedIn tools. Below it, the formula bar shows the active cell's source or formula. The sheet has a column-letter strip and a row-number gutter. Rows 1-3: the name spans all 12 columns at about 6rem, with the headline beneath it. Row 4: the seeking line as a full-bleed lime selected row. Row 5: three fact cells, then an action cell with "Email Tristan" (ink block) and "Download resume". Sheet tabs are fixed at the bottom.

FORM: The Workbook (spreadsheet as designed object), candidate 6 of 7 on the ordered list; seed key 044e1046. Signature interaction: hovering or focusing a sourced cell puts its formula or source into the formula bar. Motion: a single selection-outline move.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved
- Headshot: none available; the design must not depend on one.
