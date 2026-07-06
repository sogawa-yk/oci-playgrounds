# End-to-End Workflow

## 0. Establish Scope and State

1. Normalize the input URL and derive a neutral case slug.
2. Record the requested focus, constraints, and date in the run-state file.
3. Create the ignored case workspace from the bundled templates.
4. Check the repository for existing implementations that may answer part of the case.
5. Define what a useful conclusion would require; do not begin with a predetermined vendor conclusion.

## 1. Collect and Qualify Evidence

1. Open the input page and record its title, publisher, publication or update date, access date, and URL.
2. Capture the case's stated problem, actors, workloads, scale, components, outcomes, and explicit limitations.
3. Follow material links to official product documentation, architecture pages, repositories, talks, papers, or standards.
4. Add current official OCI documentation for every OCI service proposed later.
5. Record each source in the ledger with:
   - Source ID
   - Direct URL
   - Publisher and date
   - Source type and whether it is primary
   - Claims supported
   - Reliability and caveats
6. Use secondary sources only to locate or contextualize primary evidence. Clearly label them.

Do not infer a complete architecture from marketing language alone.

## 2. Create the Case Summary

Summarize:

- Business or operational problem stated by the source
- Users and workflow
- Inputs, outputs, and important data types
- AI or GenAI capabilities used
- Reported operating scale and quality measures
- Reported outcomes, with source attribution
- Explicit constraints and omitted information

Keep reported claims distinct from independently verified facts.

## 3. Reconstruct the Architecture

1. Draw a Mermaid flowchart showing actors, entry points, data sources, processing, AI/model services, retrieval or tools, storage, controls, observability, and outputs.
2. Add an evidence ID and one of these labels to every material node or flow:
   - `Confirmed`: directly stated by a primary source
   - `Inferred`: reasoned from evidence but not directly stated
   - `Validated`: observed in a hands-on experiment
   - `Unknown`: material detail cannot be established
3. For each inference, document alternatives, confidence, rationale, and what evidence could falsify it.
4. Do not use a plausible reference architecture as proof of the actual deployed architecture.

## 4. Decompose Technical Components

Create a table covering, when applicable:

- Client and interaction channel
- Identity, authorization, and tenant isolation
- API, orchestration, and workflow state
- Model and model-routing layer
- Prompt, guardrail, and policy handling
- Retrieval, indexing, reranking, and vector storage
- Agent tools and external system integration
- Document ingestion and parsing
- Data stores, object stores, queues, and caches
- Networking and private connectivity
- Evaluation, monitoring, tracing, logging, and feedback
- Security, privacy, retention, and governance
- Deployment, scaling, resiliency, and disaster recovery

For each component record responsibility, inputs and outputs, evidence status, dependencies, non-functional requirements, alternatives, and unresolved questions.

## 5. Develop OCI Realization Options

1. Map required capabilities to OCI services or implementation patterns; do not force a one-to-one product mapping.
2. Separate:
   - Direct OCI managed-service mapping
   - OCI-hosted open-source or custom implementation
   - Hybrid or external dependency
3. Cite current official OCI documentation for material service claims.
4. State region availability, quotas, service limits, IAM, network path, data residency, observability, operational ownership, and cost drivers when relevant and evidenced.
5. Provide alternatives where the source architecture is uncertain.
6. State gaps and unknowns without converting them into a competitive conclusion.

## 6. Select Implementation Validations

Turn material unknowns into a hypothesis register. Prioritize a hypothesis when it is:

- Important to feasibility, architecture, security, quality, latency, operability, or cost
- Not answerable from reliable documentation
- Testable with available time, tools, data, and authority
- Likely to change the final technical conclusion

For each selected hypothesis define:

- Hypothesis ID and claim
- Why it matters
- Minimal experiment
- Acceptance criteria and failure criteria
- Required environment and data
- Safety, cost, and cleanup considerations
- Expected artifact and evidence

Prefer vertical slices over broad prototypes. Use synthetic or public data.

## 7. Implement and Run Experiments

1. Reuse existing repository assets where appropriate.
2. Keep case-specific or comparison-oriented code under the ignored case workspace.
3. For an OCI experiment, read `references/oci-validation.md`, run the OCI CLI and Terraform preflight, and classify the validation as single-product or combined-service before creating code.
4. For a single-product OCI validation, create `<existing-product>/<validation-topic>/`. For a combined-service validation, create `integrations/<products-and-validation-topic>/`.
5. Define every required OCI infrastructure resource with Terraform under the validation directory's `terraform/` subdirectory. Do not use OCI CLI, SDK, Console, or shell provisioning as a substitute.
6. Use OCI CLI for authenticated OCI inspection and post-deployment verification. Do not use OCI CLI mutation commands for Terraform-managed infrastructure.
7. For reusable public code, choose a neutral validation name and comply with root `AGENTS.md`.
8. Record dependencies and versions.
9. Use placeholders in `.env.example` and `.tfvars.example`; never store credentials, real variable values, plan files, or state.
10. Run the experiment and the narrowest meaningful automated validation.
11. Capture exact Terraform commands, OCI CLI verification commands, conditions, observations, logs needed for evidence, and cleanup status.
12. Classify the result as `Validated`, `Disproved`, `Inconclusive`, or `Blocked`.
13. Update architecture and component claims only to the extent supported by the experiment.

An analogous prototype proves only the tested behavior; it does not prove the competitor's undisclosed implementation.

## 8. Build Technical Comparison Points

Compare capabilities only across explicit dimensions and conditions, such as:

- Functional fit and extensibility
- API, SDK, and integration surface
- Identity and private networking
- Data governance and residency
- Region, quota, and service-limit constraints
- Evaluation and observability
- Reliability and operational ownership
- Latency, throughput, quality, and cost under comparable measurements

For each point record the basis as documented fact, implementation result, inference, or unknown. Do not rank vendors from non-equivalent evidence. Mark unmeasured dimensions as unmeasured.

## 9. Produce the Final Brief

Use the final-brief template and include:

1. Executive summary
2. Scope and source quality
3. Case summary
4. Evidence-labeled architecture
5. Component decomposition
6. Confirmed facts, inferences, and unknowns
7. Implementation hypotheses, experiments, and results
8. OCI realization options and constraints
9. Neutral technical comparison points
10. Risks, limitations, and open questions
11. Conclusions and recommended next validation steps

Keep internal interpretation visibly separate from factual findings.

## 10. Audit and Close

1. Re-open cited URLs needed for material conclusions and check attribution.
2. Confirm all material architecture claims have evidence labels.
3. Confirm every selected hypothesis has a result or concrete blocker.
4. Run relevant tests and record their outcomes.
5. Check internal paths with `git check-ignore`.
6. Inspect tracked changes for secrets, customer data, competitor conclusions, and internal wording.
7. Confirm tracked implementation assets have runnable instructions and cleanup guidance.
8. For OCI infrastructure tests, confirm Terraform is formatted and validated, the plan was reviewed, OCI CLI verification was recorded, and temporary resources were destroyed or explicitly handed off.
9. Confirm OCI validation code uses the correct product or `integrations/` directory.
10. Update the run-state file and Definition of Done checklist.
