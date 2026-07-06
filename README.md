# OCI Playgrounds

This repository contains reproducible technical validation assets for cloud-native services and enterprise GenAI patterns. It is a collection of independent samples, experiments, infrastructure definitions, and troubleshooting notes rather than a single deployable application.

Although some samples target a specific provider or service, the documentation is intended to describe technical behavior without vendor rankings, commercial recommendations, or presales positioning.

## Scope

The repository currently covers areas such as:

- Enterprise GenAI applications, agents, and API experiments
- Retrieval-Augmented Generation and document processing
- Container, Kubernetes, and managed Kubernetes validation
- Batch, Functions, CI/CD, networking, and infrastructure experiments
- Java and Python application samples
- Repeatable troubleshooting procedures and technical notes
- Evaluation, observability, and operational validation

Each subdirectory is an independent workspace. Its README and configuration files are the source of truth for sample-specific prerequisites and commands.

## Non-goals

This repository does not provide:

- Vendor rankings or superiority claims
- Commercial recommendations or product positioning
- Presales battlecards or competitive talk tracks
- Customer-specific architecture decisions
- Internal competitive assessments
- Production support guarantees or universal benchmark conclusions

## Repository Layout

| Path | Purpose |
| --- | --- |
| `enterprise-ai/`, `genai/` | Enterprise AI and GenAI samples and experiments |
| `oke/` | Kubernetes and ingress-related validation assets |
| `batch/`, `fn/` | Batch and Functions samples |
| `ci/`, `devops/` | Build, delivery, and runtime validation |
| `helidon/` | Helidon and Java examples |
| `terraform/` | Infrastructure as Code samples |
| `integrations/` | Cross-product validation samples, created as needed |
| `docs/` | Public technical notes and troubleshooting records |
| `.agents/skills/` | Repository-scoped Codex workflows |
| `coherence/`, `others/` | Additional focused experiments |

The layout can evolve as new validations are added. Provider-specific code should stay in clearly scoped modules or directories when practical.

## Getting Started

1. Clone the repository.
2. Choose the sample directory that matches the validation you want to run.
3. Read that directory's README and inspect its deployment or dependency files.
4. Create local configuration from `.env.example` when one is provided.
5. Run the documented validation and cleanup steps.

Prerequisites vary by sample and may include Python, Java, Docker, Terraform, a Kubernetes cluster, a cloud account, or service-specific command-line tools.

## Configuration and Secrets

- Never commit API keys, tokens, passwords, private keys, customer data, or account-specific confidential information.
- Store local values in ignored `.env` files or an approved secret store.
- Commit only placeholder configuration in `.env.example`.
- Review logs, notebooks, screenshots, Terraform state, and generated results before adding them to Git.

## Design Principles

- Keep implementations reproducible and narrowly scoped.
- Separate provider-specific code from common logic when practical.
- Make prerequisites, assumptions, and limitations explicit.
- Use public, licensed, anonymized, or synthetic sample data.
- Prefer small examples that are easy to inspect, run, verify, and clean up.
- Record results with their environment and workload conditions.

Results may vary by region, service or model version, quota, indexing configuration, network path, and workload characteristics.

## Automated Case-Study Validation

The repository includes a Codex workflow for analyzing a public enterprise AI case-study URL, reconstructing its architecture, decomposing components, exploring OCI realization options, and implementing focused experiments for material unknowns.

See [AI Case-Study Validation Workflow](docs/workflows/ai-case-study-validation.md) for the process and a ready-to-use `/goal` prompt. The workflow stores competitive interpretation and final internal briefs only in Git-ignored directories.

## Internal Notes

Competitive analysis, OCI mapping, customer-specific interpretation, presales material, and slide drafts are not part of the public repository. Keep this material only in the ignored local directories `local-notes/`, `internal-briefs/`, or `slide-drafts/`, then move it to the appropriate internal knowledge system after human review.

## Contributing Validation Assets

Before adding or updating a sample:

1. State the objective and expected outcome.
2. Document prerequisites, configuration, run steps, verification, and cleanup.
3. Add a focused test or validation command when practical.
4. Describe known limitations as technical facts.
5. Confirm that no secrets, confidential data, internal notes, or vendor-comparison conclusions are included.

See [AGENTS.md](AGENTS.md) for the repository's detailed content and editing rules.
