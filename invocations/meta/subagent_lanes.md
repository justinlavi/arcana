---
type: reference
title: "Subagent Review Lanes"
aliases: ["subagent-lanes", "review-lanes"]
tags: [arcana/invocations, type/reference, scope/meta]
authority: grimoire
last_verified: 2026-05-30
---

# Subagent Review Lanes

An optional acceleration for judgment-heavy review workflows. When subagents or parallel reviewers are available, the read-only analysis phases of a host workflow can be split into isolated lanes so each reviewer goes deep without competing for attention.

This is **not** a slash command and **not** a new phase. Lanes change only *how* the read-only judgment analysis is computed (one context vs many) — never *what* is decided, applied, or logged. The host workflow's numbered phases remain the default, primary path. A host workflow supplies its own lane table; this fragment owns the reusable contract, dispatch, synthesis, and serial fallback.

The page schema, magical boundary, and hub convention are documented elsewhere; this file references them rather than restating.

## Read first

- **Parallelize or not** — the script-vs-AI split governs when fan-out earns its cost. See [[docs/script_vs_ai|script vs ai]].
- **Page schema** — lane findings cite pages by the frontmatter contract. See [[docs/page_schema|page schema]].
- **Magical boundary** — system terminology stays in Arcana; finding *content* for a grimoire stays domain-natural. See [[invocations/grimoire/validate_boundaries|validate boundaries]].

## Portability: the linear workflow is primary

The numbered phases of the host workflow are self-sufficient and come first. Lanes are strictly additive.

- An agent that cannot spawn subagents MUST be able to run the host workflow exactly as written by ignoring this fragment entirely. Deleting every lane pointer must still leave a complete, runnable linear workflow.
- Fan out only when subagents are available **and** the host workflow flags lanes as worthwhile. Otherwise run the phases serially, in documented order.

## What may be delegated, and what the orchestrator always owns

Delegate only **read-only judgment analysis**. The orchestrator/maintainer stays on the critical path and never delegates:

- mechanical validation (the host workflow's validator phase);
- applying or confirming edits (`/grm-lint` confirm-then-apply, `/grm-improve` and `/arc-improve` defer changes over ten files);
- log appends;
- synthesis of lane reports.

Lanes read and propose. They do not edit, confirm, or log.

## Per-lane output contract

Give every lane the same output shape so reports merge instead of staying prose-only:

- `lane`: one of the host workflow's named lanes.
- `scope_reviewed`: concrete files, globs, or pages inspected.
- `checks_run`: read-only validators or commands run, or `none`.
- `findings`: ordered by impact and risk. Each finding carries:
  - `id`: stable, so synthesis can reference it.
  - `priority`: `P0`-`P3`.
  - `evidence`: `file:line` references.
  - `invariant_or_claim`: the rule or claim at stake — a source-of-truth / contract / read-path rule for an Arcana lane; a routing / orphan / freshness / boundary / cross-ref rule for a grimoire lane.
  - `recommendation`.
  - `action`: `apply_now` | `defer` | `codify` | `retain`. (For surface-only passes such as lint contradictions and stale claims, the action is to surface; lanes never apply.)
  - `blast_radius`: files or surfaces affected. Pairs with the host defer threshold.
  - `read_path_delta`: effect on the shortest useful path — agent read path for Arcana, hub -> leaf route depth for a grimoire — or `n/a`.
- `deferred_opportunities`: changes too broad for the current pass.
- `workflow_updates`: heuristics worth folding back into the host workflow for future passes.

## Dispatch template

One lane per scope, dispatched as a read-only explorer:

```text
Review <WORKFLOW_TARGET> in this lane only.
Lane:
Scope:
Read only. Do not edit, confirm, or log unless explicitly assigned a write scope.
Find the issues this lane is responsible for, with file:line evidence.
Return the lane output contract from subagent_lanes.md.
```

When worker agents are permitted to edit, assign **disjoint** write scopes. Otherwise use read-only explorers and let the orchestrator apply the integrated patch.

## Synthesis

Merge the lane reports in the main context before any edit. Look for:

- the same finding from two lanes — usually a missing canonical home (an Arcana source-of-truth gap, or a grimoire ghost-reference / missing cross-ref);
- conflicting recommendations — usually unclear ownership or audience boundaries;
- repeated `defer` items that deserve a backlog, roadmap, or TODO.

The host workflow defines its own synthesis matrix and grading; this fragment only requires that synthesis happens in the main context before editing.

## Serial fallback (the default for agents that cannot fan out)

If subagents are unavailable, run the same lanes serially, keep their notes separate until synthesis, and report that the pass was serialized. An agent that cannot fan out runs each phase serially in the documented order and loses nothing but wall-clock time.

## Related

- Proven in: [[invocations/arcana/quality/review_architecture|review architecture]]
- Consumers: [[invocations/grimoire/improve_grimoire|improve grimoire]], [[invocations/grimoire/lint|lint]]
- Parallelize-or-not: [[docs/script_vs_ai|script vs ai]]
