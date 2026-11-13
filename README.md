# Tank Factory Skills — Architect v3

[`v3/`](v3/README.md) holds the ten skills the v3 Architect agent runs on the new-product path
(`brief_to_backlog/full`), one per stage, from research to the build plan:

| Hat | Skills |
| --- | --- |
| Product Owner | `product-research`, `prd`, `po-evals` |
| Designer | `ui-prompts`, `wireframes` |
| Tech Lead | `trd`, `stack-profile`, `tech-lead-evals` |
| Architect | `context-build`, `build-plan` |

Each folder under `v3/architect/` holds `SKILL.md`, a template, a passing example and a lint
script that mirrors the stage's code gate. [`v3/visuals/`](v3/visuals/README.md) holds high-resolution
PNGs: one board per building block of the sample product, and the slides of the deck *The Initial Context*. `v3/examples/reading-capture/` is one fictional product
carried through all ten. From `v3/`, `python selftest.py` checks that every lint passes on the
example and fails on a seeded violation.

The v3 `prd` and `trd` share their names with the v1 skills above but follow the v3 shapes. Install
one set or the other under a given name; the v3 index, the factory ids and the decisions made where
v3 is silent are in [`v3/README.md`](v3/README.md).

## Use a skill

**In Claude Code**, copy the skill's folder into `~/.claude/skills/` to have it in every project,
or into a project's `.claude/skills/` to share it with everyone working in that repository.

```bash
git clone https://github.com/aqueirozbr-vibez/tank-factory-skills.git
cp -r tank-factory-skills/skills/prd ~/.claude/skills/prd
```

```powershell
git clone https://github.com/aqueirozbr-vibez/tank-factory-skills.git
Copy-Item -Recurse tank-factory-skills\skills\prd $HOME\.claude\skills\prd
```

Claude picks a skill up from its description when a request matches it. You can also call it by
name, as `/prd` or `/trd`.

**In the Claude apps**, upload the skill as a zip whose top folder is the skill's folder. From the
root of this repository:

```bash
python -c "import shutil; shutil.make_archive('prd', 'zip', 'skills', 'prd')"
```

That writes `prd.zip` with `prd/SKILL.md` inside. A `.skill` file is the same zip renamed.

**The lint scripts** use only the Python 3 standard library. Each exits with 1 on any `FAIL`. A
`WARN` line is a question to answer, usually a number or a boundary the document has not stated
yet.

```bash
python skills/prd/scripts/lint_prd.py path/to/prd.md
python skills/trd/scripts/lint_trd.py path/to/trd.md
```

## With Tank Factory v1

The factory's planner and builder do not load these skills yet. The factory starts Claude Code in
bare mode with a fixed tool list for each role, and bare mode skips skill discovery. How skills
should reach factory agents is an open decision in the factory.

Until then, use them before the factory starts. Write your product's PRD and TRD with them in your
own Claude session, then turn the TRD's phases into the issues the factory builds. The factory's
[getting started guide](https://github.com/aqueirozbr-vibez/tank-factory-v1/blob/main/docs/GETTING_STARTED.md)
covers writing those issues.

## Add a skill

- Give each skill its own folder under `skills/`, named like the skill.
- Start `SKILL.md` with YAML front matter holding `name`, which matches the folder, and
  `description`. An agent reads the description to decide whether to use the skill, so say what
  it does and when to use it.
- Put templates in `assets/`, reference material in `references/`, and runnable checks in
  `scripts/`. Scripts use the Python 3 standard library only.
- Keep `SKILL.md` short and point to the references for detail.
- Run the skill's own checks against its example before you push.

## Credits

© 2026 Tank Factory. All skills and other contents of this repository are the property of Tank
Factory, licensed under [CC BY 4.0](LICENSE). Reuse them with credit as set out in [NOTICE.md](NOTICE.md).
