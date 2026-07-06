# Goal Usage

## Recommended Goal

Replace `<URL>` and paste this into the Codex composer:

```text
/goal Use $validate-ai-case-study to analyze <URL>. Execute the complete evidence-based workflow autonomously and satisfy the skill's Definition of Done. Store case analysis, inferred architecture, OCI mapping, comparisons, and the final brief only in ignored internal directories. Implement the smallest useful experiments for material uncertainties and record acceptance criteria and results. For OCI validation, use OCI CLI for connection and verification, use Terraform for every infrastructure lifecycle operation, and place code under the correct product or integrations directory. Keep tracked implementation vendor-neutral and reproducible. Do not create billable cloud resources or modify external systems without my approval.
```

The skill contains the detailed workflow, so keep the Goal concise. Add focus, region, budget, or deadline constraints after the URL when needed.

## Multiple Sources

```text
/goal Use $validate-ai-case-study to analyze these sources as one case: <URL-1>, <URL-2>. Treat the first URL as the primary case study, reconcile conflicting claims explicitly, execute the complete workflow, and satisfy the skill's Definition of Done.
```

## Goal Controls

- Use `/goal` to view the active Goal in the CLI.
- Use `/goal pause`, `/goal resume`, or `/goal clear` in the CLI.
- In the Codex app, use the progress controls above the composer to pause, resume, edit, or clear it.
- Continue steering with follow-up messages while the Goal runs.

If `/goal` is unavailable, enable it with:

```bash
codex features enable goals
```

Alternatively set this in Codex `config.toml`:

```toml
[features]
goals = true
```
