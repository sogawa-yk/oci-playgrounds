---
name: validate-ai-case-study
description: Analyze public enterprise AI or GenAI case-study URLs end to end. Use when a user provides another company's, cloud provider's, or vendor's case-study URL and asks for an evidence-based summary, architecture reconstruction, technical component decomposition, OCI realization options, Terraform-based OCI deployment, implementation experiments for unresolved questions, neutral technical comparison points, or a consolidated internal brief. Keep competitive interpretation and OCI mapping in ignored internal directories while organizing sanitized OCI validation code by product or integration and using OCI CLI for environment access.
---

# Validate AI Case Study

Turn a public case-study URL into an evidence-backed technical analysis and, where useful, a reproducible implementation validation. Preserve a strict boundary between public technical assets and internal interpretation.

## Required Input

Require at least one public source URL. Accept optional focus areas, time or cost limits, target regions, and implementation constraints. If the URL is missing or inaccessible, request a working URL before proceeding.

## Start the Run

1. Read the repository-root `AGENTS.md`.
2. Read [references/workflow.md](references/workflow.md) and [references/output-contract.md](references/output-contract.md) completely.
3. Run `python3 .agents/skills/validate-ai-case-study/scripts/init_case_workspace.py <URL> --slug <case-slug>` from the repository root. Use `--resume` only to add missing templates to an existing run.
4. Confirm the script reports that the case directory is ignored. Stop and correct the ignore rule before writing analysis if initialization fails.
5. Initialize and continuously update the run-state file. Treat it as the durable checkpoint across context compaction or resumed Goal runs.

## Apply Evidence Discipline

- Cite the original URL and every material supporting source with a direct URL and access date.
- Prefer primary sources: the case study, official product documentation, official repositories, standards, and research papers.
- Use current official OCI documentation for OCI service capabilities, limits, and availability.
- Label every material architecture claim as `Confirmed`, `Inferred`, `Validated`, or `Unknown`.
- Add confidence (`High`, `Medium`, or `Low`) and a rationale to inferred claims.
- Never turn absence of documentation into proof that a capability does not exist.
- Do not copy full articles. Record short evidence notes and paraphrased findings.

## Execute the Workflow

Follow every phase in `references/workflow.md`:

1. Collect and qualify sources.
2. Write the case summary.
3. Reconstruct the architecture with evidence labels.
4. Decompose the technical components and data flows.
5. Develop OCI realization options and constraints.
6. Convert material unknowns into testable hypotheses.
7. Implement and run the smallest useful validation experiments.
8. Build neutral technical comparison points under explicit conditions.
9. Produce the final internal brief.
10. Audit evidence, secrets, reproducibility, and tracked-versus-ignored boundaries.

Do not skip implementation merely because documentation is incomplete. Implement when a material uncertainty is testable and the result can change the technical conclusion. Record a reason when implementation would not resolve the uncertainty or cannot be performed safely.

## Validate Through Implementation

- Define each hypothesis and acceptance criteria before writing code.
- Prefer local, mocked, emulated, or free validation before managed cloud deployment.
- Keep case-specific prototypes and raw output inside the ignored case workspace.
- Before any OCI hands-on validation, read [references/oci-validation.md](references/oci-validation.md) completely and perform its OCI CLI preflight.
- Use Terraform for every OCI infrastructure create, update, and delete operation. Use OCI CLI for connection, discovery, and verification, not infrastructure provisioning.
- For a single-product OCI validation, create a descriptive subdirectory under the existing product directory. For a combined-service validation, create a clearly named directory under `integrations/`.
- Put completed OCI validation code in that tracked validation directory when it is reusable, reproducible, secret-free, customer-free, and vendor-neutral in presentation. Keep competitive rationale and raw results in the ignored case workspace.
- For tracked samples, include prerequisites, `.env.example` placeholders, run steps, tests, cleanup, assumptions, and limitations.
- Record exact commands, versions, relevant configuration, observed results, and failed attempts.
- Treat authentication, quota, region, network, and service-version failures as blocked observations, not evidence for an architecture conclusion.

## Respect Autonomy Boundaries

Continue autonomously for public web research, repository-local file creation, local implementation, tests, and non-destructive validation.

Request user approval before:

- Creating billable cloud resources or actions with material cost exposure
- Modifying or deleting external systems, data, or repositories
- Using credentials that are not already authorized for the task
- Sending messages, publishing content, or opening pull requests
- Running destructive or production-impacting operations

When approval is unavailable, use a safe local substitute where possible. Otherwise record the blocker, its impact, and the exact next step without inventing a result.

## Enforce the Content Boundary

Store case summaries, inferred competitor architecture, OCI mapping, technical comparisons, business interpretation, and final briefs only below the ignored case workspace.

Tracked files may contain only neutral and reusable technical code or documentation. Before promoting an artifact, verify that it contains no competitor evaluation, OCI superiority claim, customer-specific information, secrets, internal wording, or source material that cannot be redistributed.

## Definition of Done

Complete the Goal only when all of the following are true:

- The source ledger records the input URL, relevant primary sources, access dates, and source quality.
- The analysis contains a concise case summary, evidence-labeled architecture, component decomposition, data flow, assumptions, and unknowns.
- OCI realization options cite current official documentation and state constraints without superiority claims.
- Every material unknown has an implementation decision: validated, disproved, inconclusive, blocked with a concrete reason, or explicitly not testable with rationale.
- Selected implementation experiments have acceptance criteria, runnable artifacts, commands, and recorded results.
- OCI validations record a successful OCI CLI preflight or a concrete connection blocker.
- Any deployed OCI infrastructure is defined and lifecycle-managed with Terraform in the required product or `integrations/` directory.
- Technical comparison points state the evaluation conditions and do not rank vendors without comparable measured evidence.
- The final brief separates confirmed facts, inferences, validation results, unknowns, and internal interpretation.
- Internal outputs are ignored, any tracked outputs are neutral and reproducible, and no secrets are present.
- The run-state checklist and verification record are complete.

If a required item is blocked by missing authority or unavailable external state, do not claim completion. Record the blocker and ask for the smallest necessary user action.

## Goal Invocation

Read [references/goal-usage.md](references/goal-usage.md) when the user asks to run this workflow with `/goal` or needs a ready-to-paste Goal prompt.
