---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: oss-technical-ppt
description: >-
  Design or restyle editable PowerPoint presentations using a restrained
  technical-review visual system. Use for architecture reviews, engineering
  reports, process explanations, comparisons, state diagrams, review plans,
  and roadmaps that require balanced 16:9 layouts, deliberate vertical rhythm,
  semantic colors, native PowerPoint components, anonymized reusable examples,
  and an iterative render-image-review-adjust feedback loop.
---

# OSS Technical PPT

Create clean, restrained, editable technical presentations. Optimize the whole
canvas, not only the text block at the top of the slide.

## Anonymization

Use neutral placeholders such as System, Platform, Module, Component, Layer,
Stage, Path A, State A, Project A, and Phase 1 in reusable examples.

Remove or generalize product and repository names, branches, revisions, file
paths, APIs, hardware models, organizations, internal URLs, proprietary
workflows, and confidential measurements. Preserve only the visual relationship
between objects.

## Visual direction

Use a restrained technical-review style inspired by Swiss grids and engineering
documentation.

Prefer white backgrounds, large dark titles, blue structural accents, pale-gray
surfaces, thin rules, flat native shapes, strong alignment, and generous but
purposeful whitespace.

Avoid gradients, textures, glassmorphism, heavy shadows, 3D effects, decorative
icons, fake application interfaces, dense dashboards, repeated pills, and
unnecessary animation.

## Canvas

Use this default geometry:

```text
Aspect ratio:       16:9
Canvas:             1280 × 720
Left/right margin:  48 px
Top margin:         28 px
Title divider:      y = 132 px
Body frame:         y = 156–642 px
Footer baseline:    y = 666 px
Page number:        bottom-right
```

Keep all primary content inside the body frame. Use equal side margins.

## Vertical rhythm and canvas balance

Treat vertical distribution as a hard layout requirement.

- Make the main content occupy roughly 65–85% of the usable body height.
- Do not crowd all text into the upper half while leaving the lower half empty.
- Keep the visual center of the main content close to the vertical center of the
  body frame.
- Keep unused space above and below the main content visually comparable unless
  the composition intentionally uses asymmetry.
- Do not leave more than about 25% of the body frame unused below a crowded text
  block.
- If content is short, increase spacing between semantic groups or vertically
  center the group; do not simply top-align everything.
- If content is long, shorten it or split the slide. Do not reduce spacing and
  font size until the slide becomes cramped.

Use these default vertical gaps:

```text
Divider to first content:       28–40 px
Section heading to key claim:   32–52 px
Key claim to detail group:      20–32 px
Between detail rows:            10–18 px
Details to conclusion:          24–40 px
Conclusion to footer region:    36–56 px
```

Use 1.2–1.35 line spacing for body copy. Separate semantic groups with real
space; do not simulate spacing with repeated blank lines inside one text box.

## Text-box construction

Do not place an entire column into one large top-aligned text box.

Split repeated content into independent editable objects:

1. Number or category
2. Section title
3. Key statement or metric
4. Detail group
5. Conclusion or implication

Position these objects independently so the column uses its full vertical frame.
Use middle vertical alignment for a short single statement and top alignment for
multi-line detail groups.

Do not depend on automatic shrink-to-fit for body copy. Shorten the copy before
shrinking text.

## Typography

Prefer Microsoft YaHei, Noto Sans CJK SC, Source Han Sans SC, Arial, then a
neutral sans-serif fallback.

```text
Cover title:          56–64 pt
Slide title:          35–40 pt
Section heading:      22–26 pt
Key claim:            22–30 pt
Body text:            16–18 pt
Diagram label:        14–16 pt
Footer text:          10–12 pt
Page number:          11–12 pt
```

Use bold only for titles, headings, key stages, active states, and conclusions.
Keep one-line titles on one line. Never shrink body text below 16 pt merely to
make a layout fit.

## Color palette

```text
Ink             #111827
Muted           #5B6472
White           #FFFFFF
Pale Gray       #F3F4F6
Panel Gray      #EDEDED
Rule            #B8BCC4
Primary Blue    #3D8DFF
Blue Pale       #DCEEFF
Blue Light      #6DCBF4
Green Pale      #E8F5EC
Amber Pale      #FFF4D6
Red Pale        #FCE8E8
Dark Red        #C94A4A
```

Use blue for active paths and key transitions, gray for neutral structure,
green for completion, amber for caution or boundaries, red for faults, dark ink
for hard gates, and muted gray for supporting text. Keep meanings consistent
throughout the deck.

## Page chrome

Use the same small blue kicker, large title, thin divider, footer, and two-digit
page number on every slide. Do not allow page chrome to compete with the body.

Keep the cover minimal: category label, large title, short subtitle, one compact
metadata bar, and optional context note.

## Layout selection

Choose layouts by relationship, not habit.

| Relationship | Layout |
| --- | --- |
| Hierarchy | Vertical stack or tree |
| Structure plus responsibilities | Left diagram and right explanation |
| Baseline versus modified | Two horizontal lanes |
| Sequential process | Horizontal stage flow |
| Lifecycle | State-transition diagram |
| Three related responsibilities | Three-part mechanism layout |
| Preparation versus execution | Two stacked lanes |
| Exact comparison | Structured table |
| Ordered review phases | Stage-zero gate and horizontal waves |
| Parallel roadmap | Three equal columns |
| Principles or highlights | Numbered statement rows |

Vary the slide silhouette. Do not turn every slide into a grid of cards.

## Three-column layout

Use three columns only when the three topics have parallel meaning and similar
content weight.

For a 1280 × 720 slide, use this vertical band model:

```text
Column frame:       y = 164–624
Number + title:     y = 172–228
Key claim:          y = 270–324
Detail group:       y = 350–492
Conclusion:         y = 536–590
```

Treat these bands as anchors, not rigid coordinates. Keep equivalent objects in
all columns aligned to the same bands.

Hard rules:

- Use separate text boxes for title, key claim, details, and conclusion.
- Anchor the conclusion in the lower band instead of attaching it to the final
  detail line.
- Distribute the internal groups across the column height.
- Do not let all three columns end in the upper half of the slide.
- Do not use full-height divider lines when the content occupies only a small
  area at the top; shorten the lines or rebalance the content.
- If one column has less content, preserve band alignment rather than pulling its
  content upward.
- If the columns cannot remain balanced at 16 pt or larger, split the slide.

## Two-column hierarchy layout

Use a compact stack on the left and aligned explanation rows on the right. Keep
layer boxes equal in width, connect them with short lines, and highlight no more
than two layers. Align each right-side explanation with its corresponding layer.

## Dual-lane layout

Use two aligned horizontal paths for baseline-versus-modified or
current-versus-target flows. Use gray for the baseline and blue only for changed
or added stages. Keep connectors horizontal and place short explanations below
the lanes.

## Horizontal process layout

Use five to seven equal-width stages, 10–14 px gaps, and 60–100 px node heights.
Highlight only one stage at a time. Split long processes into two lanes instead
of shrinking labels.

## State-machine layout

Use pale gray for neutral states, blue pale for ready states, primary blue for
active states, green for completion, and red for faults. Use blue for primary
transitions, dark ink for terminal transitions, red for fault transitions, and
dashed gray for reset or rebuild.

Create connectors before nodes. Keep transition labels outside connector paths
and prevent arrows from crossing nodes or text.

## Comparison table

Use a dark header, blue primary-option header, alternating white and pale-gray
rows, a narrow interpretation column, and one conclusion bar below the table.
Limit a slide to five or six comparison rows.

## Review-plan layout

Use one full-width dark prerequisite gate, followed by four equal phases, then
one full-width shared gate. Keep arrows behind the phases. Do not repeat shared
conditions in every phase.

## Roadmap layout

Use three equal columns with parallel structure: number, title, objective,
focus, and completion definition. Use pale red, blue, and green only when their
semantic meanings apply. Anchor one principle bar near the bottom.

## Panels and connectors

Use flat rectangles or subtly rounded rectangles with 1 px strokes, 10–16 px
insets, and no shadows. Avoid nested panels and button-like shapes.

Create connectors before nodes. Use 2 px blue primary arrows, dark terminal
arrows, red fault arrows, and dashed gray optional arrows. Keep connectors short,
aligned, behind objects, and away from labels.

## Native editability

Use native PowerPoint text boxes, shapes, lines, connectors, tables, and charts.
Do not rasterize diagrams, flows, tables, roadmaps, or review plans. Do not use
generated images as substitutes for editable diagrams.

When images are unnecessary, keep the presentation free of embedded media.

## Existing deck handling

Treat an existing deck as the primary visual reference. Preserve its palette,
typography, chrome, spacing, footer, and page-number positions. Do not mix
unrelated templates.

When no template exists, use a restrained technical grid inspired by Swiss
International Style, engineering documents, and Codex Grid-like composition.

## Implementation

Use the available presentation skill and `@oai/artifact-tool` from a JavaScript
ES module. Do not use `python-pptx`.

Centralize colors, typography, margins, and reusable layout helpers. Use stable
object names. Preserve previous PPTX versions during iteration.

## Mandatory visual feedback loop

Run this loop after every draft or revision round:

1. Export a versioned PPTX.
2. Render every slide to PNG.
3. Generate a montage for deck-level rhythm review.
4. Read the montage image and every slide image at full size with the available
   image-viewing tool.
5. Record an internal issue list containing slide number, visible symptom,
   likely layout cause, severity, and concrete correction.
6. Modify the slide source.
7. Export and render again.
8. Repeat until no blocker or major visual issue remains.

Do not approve a deck by reading source code or layout coordinates alone. The
rendered image is the visual truth.

Perform at least one image-review-and-revision pass for every deck. If the first
render has no obvious problem, still inspect every slide and explicitly check
vertical balance, alignment, wrapping, spacing, and consistency before final QA.

Classify feedback as:

- BLOCKER: clipping, overflow, unreadable text, broken connector, or hidden object
- MAJOR: top-heavy composition, large accidental dead space, cramped text,
  inconsistent alignment, title wrap, or unbalanced columns
- MINOR: small spacing, weight, color, or polish inconsistency

## Image review checklist

For every rendered slide, check:

- Is content visually centered in the usable body frame?
- Are the upper and lower whitespace regions balanced?
- Does the main content use enough of the canvas without becoming crowded?
- Are semantic groups separated by visible breathing room?
- Are repeated columns aligned to the same vertical bands?
- Is a conclusion visually separated and anchored rather than appended to a list?
- Are titles, labels, and body copy free of awkward wrapping?
- Are font size, weight, and line spacing consistent?
- Are connectors behind nodes and clear of text?
- Are margins, dividers, footer, and page number consistent?

Specifically reject the slide when text is crowded in the upper half and the
lower half is empty without an intentional visual reason.

## Structural QA

After visual approval, run the overflow checker and validate the PPTX structure.
Verify slide count, canvas bounds, unresolved placeholders, embedded media,
native editability, and successful rendering.

Do not let a passing overflow test override a failed visual review. A slide can
fit within the canvas and still be badly composed.

## Final checklist

- [ ] Use a 16:9 grid and equal side margins
- [ ] Keep titles on one line and body text at 16 pt or larger
- [ ] Use semantic colors consistently
- [ ] Match the layout to the information relationship
- [ ] Balance upper and lower whitespace
- [ ] Distribute short content through the usable body height
- [ ] Keep repeated columns aligned to shared vertical bands
- [ ] Use separate text boxes for headings, claims, details, and conclusions
- [ ] Keep connectors behind nodes
- [ ] Keep diagrams natively editable
- [ ] Remove project-specific content from reusable examples
- [ ] Render every slide to images after each revision round
- [ ] Read the montage and every full-size slide image
- [ ] Fix blocker and major visual findings, then re-render
- [ ] Pass structural and overflow checks only after visual approval
