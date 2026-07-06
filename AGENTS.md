# Project Instructions

## Repository Purpose

This repository contains reproducible technical validation assets for cloud-native and enterprise GenAI patterns. It focuses on implementation, evaluation, and repeatable experiments.

Tracked content must remain technically neutral. Provider-specific implementations are allowed, but tracked files must not include presales positioning, commercial recommendations, vendor rankings, or internal competitive assessments.

These instructions apply to the entire repository unless a more specific `AGENTS.md` exists in a subdirectory.

## What Can Be Added to Tracked Files

- Reproducible validation code and sample applications
- Setup, execution, and cleanup instructions
- Evaluation scripts, metrics, and result templates
- Public, licensed, or synthetic sample data
- Infrastructure as Code, container definitions, and deployment manifests
- `.env.example` files containing placeholders only
- Vendor-neutral technical documentation and architecture descriptions
- Provider-specific implementation notes stated as technical facts
- Known technical limitations and open issues
- Unit, integration, and smoke tests

## What Must Not Be Added to Tracked Files

- OCI positioning or claims of vendor superiority
- Competitor criticism, vendor rankings, or commercial comparisons
- Presales talk tracks, battlecards, or customer-facing recommendations
- Customer-specific analysis or architecture decisions
- Internal competitive assessments or unreviewed business conclusions
- Confidential information, customer data, personal data, or internal materials
- API keys, tokens, passwords, certificates, private keys, or other secrets
- Internal-only Markdown notes, Obsidian metadata, or PowerPoint drafts
- Generated raw results or logs that may contain sensitive data

## Internal Notes

Internal notes may be written only under ignored directories such as:

- `local-notes/`
- `internal-briefs/`
- `slide-drafts/`

Use an `.internal.md` or `.private.md` suffix when practical. These files are for local use only and may be copied manually into Obsidian after human review.

Do not create internal notes unless the user explicitly requests them. Never move internal notes into tracked directories.

## Editing Rules

- Keep facts, assumptions, interpretations, and open questions clearly separated.
- Mark uncertain statements as assumptions or open questions.
- Do not put OCI-versus-competitor conclusions in `README.md`, public documentation, code comments, test fixtures, or commit-ready files.
- Isolate provider-specific behavior behind adapters or clearly scoped modules when the design permits it.
- Preserve existing samples unless a task explicitly requests migration or restructuring.
- Prefer small, auditable changes over unrelated repository-wide rewrites.
- Do not edit files under ignored internal-note directories unless explicitly asked.
- If content classification is uncertain, keep it out of tracked files and ask before adding it.

## Security and Configuration

- Never commit or expose secrets.
- Read runtime credentials from environment variables or an approved secret store.
- Use `.env.example` for configuration examples and use obvious placeholder values.
- Do not place real tenancy IDs, customer identifiers, private endpoints, or account-specific data in examples.
- Review logs, screenshots, notebooks, generated output, and Terraform state for sensitive values before tracking them.
- Use only public, licensed, anonymized, or synthetic test data.

## Reproducibility Requirements

For a new or substantially changed validation sample:

1. State the validation objective and assumptions.
2. Document prerequisites, dependencies, and required configuration.
3. Provide repeatable setup and execution steps.
4. Include a validation method or test where practical.
5. Record relevant model, region, quota, index, network, and workload conditions when they can affect results.
6. Document cleanup steps for resources that can continue to incur cost.
7. State known limitations without turning observations into vendor rankings or commercial recommendations.

## OCI Validation Rules

- Use OCI CLI for OCI connection checks, authenticated inspection, and post-deployment verification. Do not expose config values, fingerprints, tenancy identifiers, or key material in logs or tracked files.
- Use Terraform for every OCI infrastructure create, update, and delete operation. Do not provision validation infrastructure with OCI Console clicks, ad hoc OCI CLI mutation commands, SDK provisioning scripts, or shell scripts.
- Use OCI CLI only for read-only discovery and verification unless a task explicitly requires a non-infrastructure operational action.
- Run `terraform fmt -check`, `terraform init`, `terraform validate`, and review `terraform plan` before apply. Obtain the required approval before cost-incurring apply or destructive cleanup.
- Destroy temporary OCI infrastructure with Terraform and document cleanup. Never use OCI CLI deletion as the normal cleanup path for Terraform-managed resources.
- Keep credentials, private keys, Terraform state, plan files, and real `.tfvars` out of Git. Provide `.tfvars.example` or variable documentation with placeholders when needed.
- Record the OCI CLI version, selected profile name, target region, Terraform version, plan result, apply result, verification commands, and cleanup result without recording secret values.

Place OCI validation code according to its scope:

- For a single-product validation, use the existing product directory and create a kebab-case subdirectory named for the behavior being validated, for example `oke/native-ingress-controller/` or `batch/slim-image-logging/`.
- For a multi-product or combined-service validation, create a separate, clearly named directory under `integrations/`, for example `integrations/generative-ai-opensearch-rag/`.
- Put deployable infrastructure in a `terraform/` subdirectory of the validation directory. Keep application code, tests, helper scripts, and documentation alongside it in clearly named subdirectories.
- Include a README that states the objective, products involved, prerequisites, architecture, Terraform workflow, OCI CLI verification, expected result, limitations, cost considerations, and cleanup steps.
- Do not use ambiguous directory names such as `test`, `sample`, `tmp`, or numbered experiments without a descriptive validation topic.

## External AI Case-Study Workflow

When a task starts from another company's or vendor's public AI case-study URL and requests architecture analysis, OCI realization options, hands-on validation, or technical comparison, use the repository skill at `.agents/skills/validate-ai-case-study/`.

- Store the case summary, inferred architecture, OCI mapping, comparison, and final brief under `internal-briefs/case-studies/` only.
- Verify the run directory with `git check-ignore` before writing analysis.
- Keep case-specific prototypes in the ignored run directory.
- Put completed OCI validation code in the required product or `integrations/` directory after removing case-specific interpretation, secrets, and non-redistributable material.
- Use Terraform for OCI infrastructure lifecycle and OCI CLI for connection checks and verification.
- Promote only neutral, reusable, reproducible, and secret-free implementation assets to tracked directories.
- Preserve `Confirmed`, `Inferred`, `Validated`, and `Unknown` evidence labels in internal conclusions.

## Documentation Style

- Explain what a sample does, how to run it, how to verify it, and what assumptions it uses.
- Keep public documentation technically neutral and reproducible.
- Avoid claims of vendor superiority and commercial recommendations.
- Avoid customer-specific names, references, data, and conclusions.
- Describe measured results as conditional observations, not universal claims.
- Link to primary documentation when a platform-specific fact needs a source.

## Validation Before Completion

- Run the narrowest relevant tests, linters, or configuration validation available.
- Do not claim a command or deployment succeeded unless it was actually run successfully.
- Report what was verified and what was not verified.
- Check that newly generated files do not include secrets or ignored internal material.
