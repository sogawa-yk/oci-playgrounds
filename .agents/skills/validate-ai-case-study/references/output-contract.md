# Output Contract

## Workspace Layout

Create this ignored workspace for each run:

```text
internal-briefs/case-studies/<YYYY-MM-DD>-<case-slug>/
├── 00-run-state.private.md
├── 01-source-ledger.internal.md
├── 10-case-analysis.internal.md
├── 20-implementation-log.internal.md
├── 90-final-brief.internal.md
└── artifacts/
    ├── prototypes/
    ├── raw-results/
    └── diagrams/
```

Initialize and rename the templates with:

```bash
python3 .agents/skills/validate-ai-case-study/scripts/init_case_workspace.py <URL> --slug <case-slug>
```

The script validates the URL and slug, checks that the destination is ignored before creating it, copies the matching files from `assets/case-workspace/`, and records the primary URL and start time. Use `--resume` only to add missing templates without overwriting an existing run. Create `artifacts/` subdirectories only when needed.

Before writing content, run:

```bash
git check-ignore -v internal-briefs/case-studies/<YYYY-MM-DD>-<case-slug>/00-run-state.private.md
```

The command must identify an ignore rule. Do not use `git add -f` for any case-workspace file.

## Run-State Contract

Update `00-run-state.private.md` after each phase, before a long-running command, after an error, and before ending a turn. It must always state:

- Input URL and scope
- Current phase and status
- Completed artifacts
- Evidence or implementation gaps
- Blockers and approval needed
- Exact next action
- Definition of Done checklist
- Last verification commands and results

## Evidence Status

Use exactly these statuses for material claims:

| Status | Meaning |
| --- | --- |
| `Confirmed` | Directly supported by a cited primary source |
| `Inferred` | Reasoned from cited evidence but not directly stated |
| `Validated` | Observed in a documented implementation experiment |
| `Unknown` | Available evidence cannot establish the claim |

Use `High`, `Medium`, or `Low` confidence for inferences. Implementation validation of a behavior does not convert an inference about a third party's actual deployment into a confirmed fact.

## Implementation Result Status

Use exactly one result per hypothesis:

| Status | Meaning |
| --- | --- |
| `Validated` | Acceptance criteria passed under recorded conditions |
| `Disproved` | Failure criteria or contradictory evidence was observed |
| `Inconclusive` | Experiment ran but cannot resolve the hypothesis |
| `Blocked` | Experiment could not run because of a named external constraint |
| `Not testable` | A concrete rationale shows implementation would not answer the question |

## Tracked Artifact Promotion Gate

Keep a prototype ignored unless every answer below is yes:

- Is the artifact independently useful as a technical validation sample?
- Is its name and documentation neutral rather than competitor-specific?
- Are setup, run, verification, cleanup, assumptions, and limitations documented?
- Are all credentials represented only by placeholders?
- Is all data public, licensed, anonymized, or synthetic?
- Are internal interpretation, OCI positioning, vendor rankings, and customer details absent?
- Are redistribution rights clear for every included asset?
- Did relevant tests or validation commands pass?
- For OCI infrastructure, is the complete lifecycle defined in a `terraform/` subdirectory with no ad hoc provisioning path?
- Was OCI CLI used for connection and verification, with only non-sensitive status recorded?
- Is a single-product validation under its existing product directory, or a combined-service validation under a clearly named `integrations/` directory?

If any answer is no or uncertain, leave the artifact in the ignored workspace.

## Minimum Final Deliverables

The final brief must link or refer to:

- Source ledger
- Case analysis and architecture diagram
- Component decomposition
- Hypothesis register
- Implementation commands, artifacts, and results
- OCI realization options with official sources
- Technical comparison matrix
- Limitations and unknowns
- Verification record

## OCI Validation Artifact Layout

Use this layout for a single-product validation:

```text
<existing-product>/<validation-topic>/
├── README.md
├── app/ or src/
├── terraform/
├── scripts/
└── tests/
```

Use this layout for a combined-service validation:

```text
integrations/<product-a>-<product-b>-<validation-topic>/
├── README.md
├── app/ or src/
├── terraform/
├── scripts/
└── tests/
```

Create only the subdirectories needed by the validation. Use descriptive lowercase kebab-case names. Keep competitive interpretation and raw results in the ignored case workspace rather than the tracked implementation directory.
