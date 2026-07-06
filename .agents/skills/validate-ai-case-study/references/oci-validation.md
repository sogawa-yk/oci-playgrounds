# OCI Hands-On Validation Rules

Read and follow this reference before creating code or connecting to OCI for an implementation experiment.

## Tool Responsibilities

Use tools with these non-overlapping responsibilities:

| Tool | Required use | Prohibited use |
| --- | --- | --- |
| OCI CLI | Confirm installation, select an explicit profile, perform authenticated read-only discovery, inspect deployed resources, and verify experiment results | Creating, updating, or deleting Terraform-managed infrastructure |
| Terraform with the OCI provider | Define, plan, create, update, and destroy every OCI infrastructure resource required by the validation | Storing secrets, real `.tfvars`, state, or saved plans in Git |
| Application code or OCI SDK | Exercise workload APIs and application behavior after infrastructure exists | Replacing Terraform with provisioning code |

Do not use OCI Console clicks, ad hoc CLI mutation commands, SDK provisioning scripts, or shell provisioning as the source of truth for validation infrastructure.

## Preflight

Before OCI implementation:

1. Run `command -v oci` and `oci --version`.
2. Confirm the intended profile exists in `~/.oci/config` without printing config values.
3. Validate that the profile has required fields, a region, and readable key material without exposing any values.
4. Run a least-privilege, read-only OCI CLI command appropriate to the target service to prove authenticated connectivity.
5. Record only the CLI version, profile name, target region, command purpose, timestamp, and pass/fail result.
6. Run `command -v terraform` and `terraform version`.
7. If any required check fails, mark OCI execution `Blocked`; do not infer that a service or architecture is unavailable.

Do not print or record tenancy OCIDs, user OCIDs, fingerprints, private-key paths, private keys, security tokens, or complete configuration files.

## Choose the Validation Directory

Classify the implementation before writing code.

### Single Product

For one primary OCI product, use the existing product directory and a descriptive behavior subdirectory:

```text
<existing-product>/<validation-topic>/
```

Examples:

```text
oke/native-ingress-controller/
batch/slim-image-logging/
genai/structured-output-validation/
```

Use the repository's established product spelling when it exists. Name the child directory for the capability, limit, integration behavior, or failure mode being validated.

### Combined Services

For a validation whose result depends materially on multiple OCI products, create a separate directory:

```text
integrations/<product-a>-<product-b>-<validation-topic>/
```

Example:

```text
integrations/generative-ai-opensearch-rag/
```

Do not hide a combined-service validation under one product when that would make ownership or scope misleading.

### Validation Contents

Use only the subdirectories the validation needs:

```text
<validation-directory>/
├── README.md
├── app/ or src/
├── terraform/
├── scripts/
└── tests/
```

The README must state the objective, OCI products, architecture, prerequisites, variables, Terraform lifecycle, OCI CLI verification, expected results, limitations, cost considerations, and cleanup.

## Terraform Lifecycle

1. Put all OCI resource definitions in `<validation-directory>/terraform/`.
2. Declare Terraform and OCI provider version constraints.
3. Use variables for region, compartment, profile, names, and configurable sizes. Do not hardcode real account identifiers.
4. Commit placeholder examples only, such as `terraform.tfvars.example`.
5. Run `terraform fmt -check`.
6. Run `terraform init` without committing `.terraform/` or lock-sensitive local data other than the dependency lock file.
7. Run `terraform validate`.
8. Generate and review `terraform plan` before apply. Do not commit the plan file.
9. Obtain approval before an apply that creates cost-bearing resources or modifies external state.
10. Verify the deployed state with read-only OCI CLI commands and application tests.
11. Destroy temporary resources with `terraform destroy`, subject to the required destructive-action approval.
12. Record any intentionally retained resources, owner, reason, and cleanup responsibility.

Never use OCI CLI deletion to clean up Terraform-managed resources. If drift or a partially failed deployment requires recovery, repair or import the resource through Terraform and document the exception.

## Evidence to Record

Record in the implementation log:

- Validation directory and scope classification
- OCI CLI and Terraform versions
- Non-sensitive profile name and target region
- Preflight and authenticated connectivity result
- Terraform format, init, validate, and plan results
- Apply approval and outcome
- Read-only OCI CLI verification commands and sanitized observations
- Application test commands and results
- Terraform destroy result or explicit resource handoff
- Remaining drift, blockers, cost exposure, and cleanup owner
