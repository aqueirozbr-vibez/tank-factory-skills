# Tank Factory skills

Agent skills for [Tank Factory v1](https://github.com/aqueirozbr-vibez/tank-factory-v1).
A skill is a folder an agent loads when a task calls for it. It holds a `SKILL.md` with the
instructions, plus the templates, references and scripts those instructions point to.

## Skills

| Skill | What it does | What is inside |
| --- | --- | --- |
| [`prd`](skills/prd/SKILL.md) | Writes a Product Requirements Document in a fixed shape: capabilities with the guarantee each holds, numeric goals, personas, testable requirements, a published instrument for every automated judgment, phases with numeric gates, risks and open questions. | Template, section contract, a full example PRD, `lint_prd.py` |
| [`trd`](skills/trd/SKILL.md) | Writes the Technical Requirements Document from a PRD: component decisions, C4 and Mermaid diagrams, data model, API contract, network, agents, security, tests and open decisions, each section traced to the PRD line it serves. | Template, section contract, diagram patterns, a full example TRD, `lint_trd.py` |

The two work as a pair. The PRD's fixed headings are the anchors the TRD cites, and the example
TRD was written from the example PRD.

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
