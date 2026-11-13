---
name: stack-profile
description: Technical stage of the Tank Factory Architect (Tech Lead hat) — choose a product's stack inside the factory guardrails and the supported stacks, and write the stack profile (per repository: languages and versions, package manager, base image, quality commands, boundary-check tool, binding framework, scanners, load-test tool, template; plus product kind and guardrail requests) into the TRD's Stack section and the envelope. Use when a TRD needs its Stack section, when a product's language, framework or major version changes, or when an adopted repository's stack must be recorded.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# stack-profile

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Tech Lead | technical, as-built TRD, any stack change | the `stack_profile` block in TRD §2 and the same object in the envelope | `stack_profile` gate (below) | tech lead at the TRD checkpoint, bound to the TRD SHA and the profile hash |

A factory holds governance, never a stack: each product's stack is decided here. The profile is what the rest of the factory **runs on** — code writes it to `.factory/stack.yaml`, the Sysop builds the image from it, and every later gate calls its quality commands. You propose it; a person approves it; code writes it. So every value must be exact enough to execute.

## Inputs

- The PRD (its screens decide `product_kind`; its NFR rows constrain the choice) and the TRD draft.
- The factory guardrails, `environment.yaml`: `base_image_sources`, `package_registries`, `secret_sources`, `network_allowlist`.
- The supported stacks (`references/supported-stacks.json`; the factory image's list wins when it differs). `references/environment.example.yaml` shows the guardrails file.
- As-built and stack changes: the repository's manifests, lockfiles and CI configuration.

## Steps

1. **Set `product_kind`** from the PRD: `ui` when it names screens and has no service of its own, `service` when it names none, `ui_and_service` otherwise. Done when it agrees with the PRD's `Product kind:` line and `Screens:` lines.
2. **List the repositories** the product needs. Fewer is better: each one adds an image, a pipeline and a boundary. Done when every TRD container lives in exactly one repository.
3. **Choose each repository's stack** from the supported stacks, and justify the choice in the TRD's `Choice | Pick | Alternatives | Why` table against a PRD id. Done when every language is supported and pinned (`python@3.12`).
4. **Fill every field** of the profile (Shape). Take tool names from the supported stack's row so the factory has a scanner set, a binding framework and a boundary checker for it. Done when no field is empty.
5. **Check the guardrails.** Each base image must match a `base_image_sources` pattern; each package registry and each outbound destination the stack needs must be on the lists. Anything outside goes into `guardrail_requests[]` with its reason — it becomes a blocking decision at the checkpoint and a policy PR for a factory Admin. Prefer a choice inside the guardrails when one meets the requirement.
6. **Self-check.** `python3 scripts/lint_stack_profile.py docs/trd/<product>.md --guardrails <environment.yaml> --prd docs/prd/<product>.md [--new-product] [--repo <path>]`. Done at 0 fail.
7. **Copy the block** unchanged into the envelope's `stack_profile`.

## Shape

One fenced block in TRD §2, opened with ```` ```json stack_profile ````:

```json
{
  "product_kind": "ui_and_service",
  "repositories": [
    {
      "repository": "acme/web",
      "template": "typescript-web",
      "languages": ["typescript@5.6"],
      "package_manager": "pnpm@9",
      "base_image": "registry.example/approved/node:22-bookworm",
      "quality": {
        "format": "pnpm format:check",
        "lint": "pnpm lint",
        "typecheck": "pnpm typecheck",
        "test": "pnpm test",
        "focused_test_pattern": "pnpm vitest run {files}"
      },
      "boundary_check": "dependency-cruiser",
      "bindings": "playwright",
      "scanners": "typescript-default",
      "load_test": "k6"
    }
  ],
  "guardrail_requests": [
    {"kind": "registry", "value": "npm.pkg.example", "reason": "private design-system package (FR-3.1)"}
  ]
}
```

| Field | Rule |
| --- | --- |
| `repository` | `owner/name`, one entry per repository |
| `template` | required for every repository of a new product; the supported stack's template id |
| `languages` | `name@version`, each a supported language |
| `package_manager` | `name@version`; it implies the registry the guardrails must allow |
| `base_image` | a full reference matching an allowed source, with a tag |
| `quality.format` / `lint` / `typecheck` / `test` | check-only commands that exit non-zero on a violation — environment setup proves each one fails on a seeded violation |
| `quality.focused_test_pattern` | the test command for a subset, containing `{files}` |
| `boundary_check`, `bindings`, `scanners`, `load_test` | from the supported stack's row |
| `guardrail_requests[]` | `kind` (`registry`, `base_image_source` or `network`), `value`, `reason` |

## The gate

- Every field present for every repository.
- Each stack is a supported stack. One outside the list cannot be approved, so it is never proposed.
- Every base image comes from an allowed source.
- Every registry and destination is inside the guardrails or listed in `guardrail_requests[]`.
- `product_kind` agrees with the PRD's screens.
- A template is named for every repository of a new product.
- As-built: every language, package manager and version matches the manifests and lockfiles.

## Limits

The profile lives only in the TRD and the envelope; `.factory/` is written by code after the approval. A later stack change is a TRD amendment through the same checkpoint. Two gate corrections, then `blocked(stack_profile)`; a non-empty `guardrail_requests[]` holds the project `blocked(stack_guardrails)` until the policy PR merges or the TRD is amended.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
