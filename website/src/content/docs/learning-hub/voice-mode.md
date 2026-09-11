---
title: 'Using Voice Mode with GitHub Copilot'
description: 'Have a natural spoken conversation with a Copilot agent in VS Code while it works on your code — and interrupt it mid-response.'
authors:
  - GitHub Copilot Learning Hub Team
lastUpdated: 2026-09-11
estimatedReadingTime: '5 minutes'
tags:
  - voice
  - vscode
  - agents
  - experimental
relatedArticles:
  - ./agents-and-subagents.md
  - ./understanding-copilot-context.md
prerequisites:
  - VS Code with the GitHub Copilot extension
  - An eligible individual GitHub Copilot plan (not Business or Enterprise)
---

Voice Mode is an experimental feature in VS Code 1.137+ that lets you speak naturally with a Copilot agent while it works on your code. Instead of typing prompts, you talk — and you can interrupt the agent mid-response to redirect it, add context, or ask follow-up questions.

> **Status**: Experimental. Enable via `agents.voice.enabled: true` in VS Code settings. Voice Mode requires an eligible **individual** GitHub Copilot plan (Pro or Pro+); it is not currently available on Business or Enterprise plans.

## What Voice Mode Is (and Isn't)

Voice Mode is a *conversation interface* layered on top of the standard agent experience — the same underlying agent capabilities, tools, and context apply. The difference is the input modality: you speak instead of type, and the agent's responses are available both as text and (optionally) synthesized speech.

This makes it useful when:

- You're navigating a complex debugging session and want to think out loud
- Typing would interrupt your flow (for example, when reviewing a diff with both hands on the mouse)
- You want to quickly redirect a long-running agent task without switching focus to the keyboard

It is **not** a replacement for the full agent chat experience — structured inputs like `#file` references, code blocks, and `/commands` still benefit from the keyboard.

## Enabling Voice Mode

1. Open **VS Code Settings** (`Ctrl+,` / `Cmd+,`).
2. Search for `agents.voice.enabled` and set it to `true`.
3. Restart VS Code if prompted.

Once enabled, a microphone icon appears in the Copilot Chat panel. Click it (or use the keyboard shortcut shown in the panel) to start speaking.

### Additional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `agents.voice.enabled` | `false` | Enable or disable Voice Mode |
| `agents.voice.showTranscript` | `true` | Show a live transcript of what you say |
| `agents.voice.voice` | System default | Choose the voice used for spoken agent responses |

## Talking with an Agent

Once Voice Mode is active, speak your prompt naturally — no special phrasing required. The agent processes your speech using the same model and tools it uses for typed input.

**Example prompts that work well out loud**:

- *"Look at the failing test in the auth module and explain what's wrong."*
- *"Add input validation to the register endpoint — use the same pattern as the login endpoint."*
- *"Actually, use zod for validation instead. Keep the existing error format."*

The last example shows the key benefit: **interrupting mid-response**. If the agent is generating code you realize you don't want, speak up and it will stop and redirect.

## Interrupting an Agent

You can speak at any point while an agent is responding — even mid-sentence. The agent detects your speech, stops its current output, and processes your new input. This makes voice interactions feel more like a real conversation and less like a turn-based chat.

Useful interruption patterns:

- **Redirect**: *"Wait, actually do this in TypeScript, not JavaScript."*
- **Clarify scope**: *"Only change the controller, not the service layer."*
- **Stop entirely**: *"Stop, I'll handle this part myself."*

## Tips for Effective Voice Prompts

- **Be specific**: The same principles that make typed prompts effective apply to voice — the more specific the context, the better the result.
- **Name files and symbols**: Saying "the UserService class in user-service.ts" is clearer than "the user thing".
- **Use follow-up turns**: Voice Mode shines in multi-turn conversations. Ask something, hear the result, and immediately redirect or refine.
- **Combine with context attachments**: You can still attach files, issues, or PRs using the chat UI before starting to speak. Voice picks up where the attached context left off.

## Further Reading

- [VS Code Voice Mode documentation](https://code.visualstudio.com/docs/configure/accessibility/voice#use-voice-mode)
- [VS Code 1.137 release notes](https://code.visualstudio.com/updates/v1_137)
- [Agents and Subagents](../agents-and-subagents/) — Understanding how agents work during a voice session
- [Understanding Copilot Context](../understanding-copilot-context/) — How context affects what the agent understands when you speak

---
