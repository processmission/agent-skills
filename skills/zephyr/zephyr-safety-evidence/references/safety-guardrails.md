<!--
SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
SPDX-License-Identifier: MIT
-->

# Zephyr Safety Guardrails

Use this reference only when requirements or traceability are explicitly in a
safety, certification, ASIL, SIL, or safety-case context.

## Claim boundary

- Describe only what cited artifacts demonstrate for the stated baseline.
- Zephyr's public safety overview targets IEC 61508 SIL 3 / SC 3 for a limited
  source scope that remains to be defined. Treat source areas as candidate
  evidence until an approved scope, revision, and owner are cited.
- Project evidence is not product certification evidence. Platform, hardware,
  toolchain, integration, application, and assessor evidence remain with the
  responsible integrator and organizations.
- Tie IEC 61508 SIL statements to the applicable safety function and scope; do
  not assign SIL to arbitrary code from component evidence alone.
- Never infer certification, a safety integrity level, or readiness from draft,
  partial, or public-only evidence.

## Evidence layers

Keep these boundaries explicit:

1. Zephyr project evidence for an approved source scope and baseline.
2. Platform evidence for the BSP, drivers, middleware, hardware, and toolchain.
3. Product or vehicle evidence for the item, hazards, safety concepts,
   integration, validation, and safety case.

Do not use evidence from one layer to close a claim owned by another.

## Lifecycle routing

Select the applicable standard and route before defining gates. Do not apply a
single lifecycle to every safety task.

- For Zephyr's IEC 61508 effort, confirm the approved limited source scope and
  whether route 3s or 1s applies. Follow the current Safety Committee process
  and source baseline rather than assuming a fixed certification boundary.
- For ISO 26262 product work, establish the item definition, HARA, safety goals,
  and ASIL before the functional safety concept. Refine that into the technical
  safety concept and derived requirements before implementation, integration,
  verification, and assessment evidence is claimed complete.
- For another standard or route, record the lifecycle mapping, responsible
  owner, required outputs, and unresolved differences.

These activities may iterate, but later evidence cannot substitute for a
missing concept, scope, or ownership decision.

## Evidence record

For each safety-facing claim, record:

- claim and status;
- standard and edition, lifecycle route, scope layer, source baseline, and
  owner;
- requirement, process, or assessment source;
- code or configuration path and verification evidence for implementation
  claims, otherwise `not applicable` or an explicit gap;
- assumptions, contrary evidence, unresolved gaps, and next human decision.
