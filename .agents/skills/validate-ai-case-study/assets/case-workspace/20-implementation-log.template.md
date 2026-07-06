# Implementation Validation Log

## Environment

- Date:
- Platform:
- Runtime and versions:
- Region, service, or model versions:
- OCI CLI version and profile name:
- OCI CLI connection check:
- Terraform version:
- Terraform directory:
- Validation scope: `single-product | combined-service | not-applicable`
- Tracked implementation path:
- Data:
- Relevant configuration:

Do not record credentials or secrets.

## Hypotheses

| ID | Hypothesis | Acceptance criteria | Failure criteria | Environment/cost | Artifact path | Result status |
| --- | --- | --- | --- | --- | --- | --- |

## Experiment Records

### Hypothesis H-001

#### Why It Matters

#### Minimal Experiment

#### Commands

```text
# Record exact commands after redacting secrets.
```

#### Observations

#### Result

- Status: `Validated | Disproved | Inconclusive | Blocked | Not testable`
- Conditions:
- Evidence:
- Effect on architecture or comparison:
- Remaining uncertainty:
- Cleanup completed:

## Failed Attempts

| Date/time | Attempt | Observed failure | Diagnosis | Next action |
| --- | --- | --- | --- | --- |

## Verification Summary

| Command/check | Result | Notes |
| --- | --- | --- |

## Terraform Lifecycle

| Stage | Command or artifact | Result | Notes |
| --- | --- | --- | --- |
| Format | `terraform fmt -check` | | |
| Initialize | `terraform init` | | |
| Validate | `terraform validate` | | |
| Plan | `terraform plan` | | |
| Apply | Approval and result | | |
| OCI CLI verification | Read-only verification command | | |
| Cleanup | `terraform destroy` or handoff | | |
