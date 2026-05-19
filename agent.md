# enter-the-metrics agent skill source of truth

This repository uses [`nullroute-commits/agency-agents`](https://github.com/nullroute-commits/agency-agents) as the upstream source of truth for reusable AI agent skills.

## Upstream references

- Repository: `https://github.com/nullroute-commits/agency-agents`
- Copilot integration guide: `integrations/github-copilot/README.md`
- Integration index: `integrations/README.md`

## Default skill pack for this repository

Use the upstream agents directly for work on this stack:

- `engineering/engineering-code-reviewer.md`
- `engineering/engineering-backend-architect.md`
- `testing/testing-api-tester.md`
- `testing/testing-reality-checker.md`
- `project-management/project-management-project-shepherd.md`

## Operating rule

Do not fork or rewrite the upstream agent definitions in this repository unless a project-specific override is required. Treat the upstream repository as the canonical source, and update this file only when the selected skill set or upstream references change.

## Sync procedure

1. Review the upstream `agency-agents` repository for the latest agent definitions.
2. Install or refresh the selected agents with the upstream Copilot workflow:
   - `./scripts/install.sh --tool copilot`, or
   - copy the selected `.md` files into `~/.github/agents/` and `~/.copilot/agents/`.
3. Keep this file aligned with the upstream paths used by this project.
