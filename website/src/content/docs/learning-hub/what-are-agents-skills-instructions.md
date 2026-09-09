---
title: 'What are Agents, Skills, and Instructions'
description: 'Understand the primary customization primitives that extend GitHub Copilot for specific workflows.'
authors:
  - GitHub Copilot Learning Hub Team
lastUpdated: 2026-09-09
estimatedReadingTime: '9 minutes'
prev: false
---

Building great experiences with GitHub Copilot starts with understanding the core primitives that shape how Copilot behaves in different contexts. This article clarifies what each artifact does, how it is packaged inside this repository, and when to use it.

## Agents

Agents are configuration files (`*.agent.md`) that describe:

- The tasks they specialize in (for example, "Terraform Expert" or "LaunchDarkly Flag Manager").
- Which tools or MCP servers they can invoke.
- Optional instructions that guide the conversation style or guardrails.

When you assign an issue to Copilot or open the **Agents** panel in VS Code, these configurations let you swap in a specialized assistant. Each agent in this repo lives under `agents/` and includes metadata about the tools it depends on.

In products that support delegation, a primary agent can also launch temporary subagents for focused work such as planning, research, or review. See [Agents and Subagents](../agents-and-subagents/) for the coordination model.

### When to reach for an agent

- You have a recurring workflow that benefits from deep tooling integrations.
- You want Copilot to proactively execute commands or fetch context via MCP.
- You need persona-level guardrails that persist throughout a coding session.
- You want a coordinator that can delegate narrower work to subagents.

## Skills

Skills are self-contained folders that package reusable capabilities for GitHub Copilot. Each skill lives in its own directory and contains a `SKILL.md` file along with optional bundled assets such as reference documents, templates, and scripts.

A `SKILL.md` defines:

- A **name** (used as a `/command` in VS Code Chat and for agent discovery).
- A **description** that tells agents and users when the skill is relevant.
- Detailed instructions for how the skill should be executed.
- References to any bundled assets the skill needs.

Skills follow the open [Agent Skills specification](https://agentskills.io/home), making them portable across coding agent systems beyond GitHub Copilot.

### Why skills over prompts

Skills replace the earlier prompt file (`*.prompt.md`) pattern and offer several advantages:

- **Agent discovery**: Skills include extended frontmatter that lets agents find and invoke them automatically—prompts could only be triggered manually via a slash command.
- **Richer context**: Skills can bundle reference files, scripts, templates, and other assets alongside their instructions, giving the AI much more to work with.
- **Cross-platform portability**: The Agent Skills specification is supported across multiple coding agent systems, so your investment travels with you.
- **Slash command support**: Like prompts, skills can still be invoked via `/command` in VS Code Chat.

### When to reach for a skill

- You want to standardize how Copilot responds to a recurring task.
- You need bundled resources (templates, schemas, scripts) to complete the task.
- You want agents to discover and invoke the capability automatically.
- You prefer to drive the conversation, but with guardrails and rich context.

## Instructions

Instructions (`*.instructions.md`) provide background context that Copilot reads whenever it works on matching files. They often contain:

- Coding standards or style guides (naming conventions, testing strategy).
- Framework-specific hints (Angular best practices, .NET analyzers to suppress).
- Repository-specific rules ("never commit secrets", "feature flags must live in `flags/`").

Instructions sit under `instructions/` and can be scoped globally, per language, or per directory using glob patterns. They help Copilot align with your engineering playbook automatically.

### When to reach for instructions

- You need persistent guidance that applies across many sessions.
- You are codifying architecture decisions or compliance requirements.
- You want Copilot to understand patterns without manually pasting context.

## How the artifacts work together

Think of these artifacts as complementary layers:

1. **Instructions** lay the groundwork with long-lived guardrails.
2. **Skills** let you trigger rich, reusable workflows on demand—and let agents discover those workflows automatically.
3. **Agents** bring the most opinionated behavior, bundling tools and instructions into a single persona.
4. **Hooks** add deterministic automation at lifecycle boundaries, ensuring guardrails that run regardless of what the agent decides.
5. **Plugins** bundle all of the above into an installable unit you can share across projects with one command.

By combining these primitives, teams can achieve:

- Consistent onboarding for new developers.
- Repeatable operations tasks with reduced context switching.
- Tailored experiences for specialized domains (security, infrastructure, data science, etc.).

## Hooks

Hooks are shell commands or HTTP requests that run automatically at key moments during a Copilot agent session: before and after each tool use, when the session starts or ends, or when a user submits a prompt. Unlike agents and skills — which influence what the AI decides to do — hooks are **deterministic**: they run the same way every time regardless of model output.

A hook configuration (`hooks.json`) declares which events trigger which commands:

```json
{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "type": "command",
        "bash": "npx prettier --write .",
        "timeoutSec": 30
      }
    ]
  }
}
```

Hook configurations for a repository live in `.github/hooks/`, and support events including `sessionStart`, `sessionEnd`, `preToolUse`, `postToolUse`, `agentStop`, `userPromptSubmitted`, and more.

### When to reach for hooks

- You need formatting, linting, or validation to happen reliably after every code change.
- You want to approve or deny specific tool executions (e.g., block dangerous commands in CI).
- You need audit logs or notifications triggered by agent activity.
- You want to inject dynamic context (branch name, environment state) into every session automatically.

**Learn more**: [Automating with Hooks](../automating-with-hooks/)

## Plugins

Plugins are installable packages that bundle agents, skills, hooks, and MCP server configurations into a single unit. Instead of manually copying files across every project, a plugin lets your whole team install a curated set of capabilities with one command:

```bash
copilot plugin install context-engineering@awesome-copilot
```

Plugins follow the open [Agent Plugins 1.0 specification](https://agent-plugins.org/), making them portable: a plugin works in both GitHub Copilot CLI and VS Code without repackaging. Each plugin includes a `plugin.json` manifest, and can optionally ship canvas extensions, MCP server configuration via `mcp.json`, and more.

Both Copilot CLI and VS Code come with two marketplaces registered by default: `copilot-plugins` (official) and `awesome-copilot` (community). You can browse them without any setup.

### When to reach for a plugin

- You want to distribute a consistent set of agents and skills across your team in one step.
- You are packaging a domain toolkit (e.g., "Rails development", "Azure infrastructure") for others to install.
- You want to version and update your team's Copilot customizations centrally.

**Learn more**: [Installing and Using Plugins](../installing-and-using-plugins/)

## Agentic Workflows

Agentic Workflows are AI-powered automations that run Copilot coding agents inside GitHub Actions. Written as markdown files with natural-language instructions, they can be triggered on a schedule, by repository events, or by slash commands on issues and PRs — no YAML Actions syntax required.

```markdown
---
name: "Daily Issues Report"
on:
  schedule: daily on weekdays
permissions:
  issues: read
safe-outputs:
  create-issue:
    labels: [report]
---
Summarize open issues opened in the last 24 hours and create a daily report issue.
```

Workflows are compiled to `.lock.yml` files via the `gh aw` CLI extension and then run by GitHub Actions.

### When to reach for agentic workflows

- You want autonomous, event-driven automation that requires reasoning or summarization.
- You need scheduled reports, triage automations, or slash-command-triggered reviews.
- You want to automate tasks that go beyond what static GitHub Actions can do.

**Learn more**: [Agentic Workflows](../agentic-workflows/)

## Next steps

- Explore the rest of the **Fundamentals** track for deeper dives on chat modes, collections, and MCP servers.
- Browse the [Awesome Agents](../../agents/), [Skills](../../skills/), [Instructions](../../instructions/), [Hooks](../../hooks/), and [Plugins](../../plugins/) directories for inspiration.
- Try generating your own artifacts, then add them to the repo to keep the Learning Hub evolving.

---
