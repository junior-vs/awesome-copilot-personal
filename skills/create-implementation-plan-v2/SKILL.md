---
name: create-implementation-plan
description: 'Create a new implementation plan file for new features, refactoring existing code or upgrading packages, design, architecture or infrastructure.'
---

# Create Implementation Plan

## Safety, Privacy, and Security

**CRITICAL: All implementation plans must adhere to these safety rules:**

- **NO SECRETS OR CREDENTIALS**: Never include real API keys, passwords, database credentials, connection strings, private keys, certificates, or authentication tokens in implementation plans
- **USE PLACEHOLDERS ONLY**: Use templated placeholders like `{{API_KEY}}`, `{{DB_PASSWORD}}`, `{{OAUTH_CLIENT_SECRET}}`, `{{DATABASE_CONNECTION_STRING}}`, `{{PRIVATE_KEY_PATH}}`
- **NO INTERNAL INFRASTRUCTURE DETAILS**: Use anonymized/example hostnames like `db.example.internal`, `api.example.com`, `10.0.x.x` instead of real production infrastructure
- **NO PII OR SENSITIVE DATA**: Never include personally identifiable information, customer data, or proprietary business logic details
- **ANONYMIZED EXAMPLES ONLY**: All code examples, configuration samples, and implementation details must use fictional/anonymized data
- **RESPECT ORGANIZATIONAL POLICIES**: If organizational security policies, compliance requirements, or existing governance conflict with this template, the organizational policies take precedence
- **NON-DESTRUCTIVE PLANS**: Implementation plans must not prescribe actions that could cause data loss, service disruption, or security vulnerabilities without explicit safeguards and rollback procedures

**Handling Ambiguous Inputs:**
- If `${input:PlanPurpose}` is vague, empty, or unclear, use conservative defaults and request clarification in the plan's introduction
- If the purpose doesn't match allowed prefixes (`upgrade|refactor|feature|data|infrastructure|process|architecture|design`), choose the closest match and note the clarification needed
- If conflicting instructions are present, prioritize: (1) Organizational policies, (2) Security requirements, (3) This template, (4) General best practices

## Primary Directive

Your goal is to create a new implementation plan file for `${input:PlanPurpose}`. Your output must be machine-readable, deterministic, and structured for autonomous execution by other AI systems or humans.

## Execution Context

This prompt is designed for AI-to-AI communication and automated processing. All instructions must be interpreted literally and executed systematically without human interpretation or clarification.

## Core Requirements

- Generate implementation plans that are fully executable by AI agents or humans
- Use deterministic language with zero ambiguity
- Structure all content for automated parsing and execution
- Ensure complete self-containment with no external dependencies for understanding
- **Enforce safety, privacy, and security controls** in all generated content

## Plan Structure Requirements

Plans must consist of discrete, atomic phases containing executable tasks. Each phase must be independently processable by AI agents or humans without cross-phase dependencies unless explicitly declared.

## Phase Architecture

- Each phase must have measurable completion criteria
- Tasks within phases must be executable in parallel unless dependencies are specified
- All task descriptions must include specific file paths, function names, and exact implementation details (using anonymized examples and placeholders for sensitive values)
- No task should require human interpretation or decision-making
- **All tasks must include safety validation criteria** (e.g., "Verify no credentials committed", "Confirm rollback procedure tested")

## AI-Optimized Implementation Standards

- Use explicit, unambiguous language with zero interpretation required
- Structure all content as machine-parseable formats (tables, lists, structured data)
- Include specific file paths, line numbers, and exact code references where applicable
- Define all variables, constants, and configuration values explicitly (using placeholders for secrets)
- Provide complete context within each task description
- Use standardized prefixes for all identifiers (REQ-, TASK-, etc.)
- Include validation criteria that can be automatically verified
- **Ensure all examples use anonymized/fictional data**

## Output File Specifications

- Save implementation plan files in `/plan/` directory
- Use naming convention: `[purpose]-[component]-[version].md`
- Purpose prefixes: `upgrade|refactor|feature|data|infrastructure|process|architecture|design`
- Example: `upgrade-system-command-4.md`, `feature-auth-module-1.md`, `refactor-payment-service-2.md`
- File must be valid Markdown with proper front matter structure

## Mandatory Template Structure

All implementation plans must strictly adhere to the following template. Each section is required and must be populated with specific, actionable content. AI agents must validate template compliance before execution.

## Template Validation Rules

- All front matter fields must be present and properly formatted
- All section headers must match exactly (case-sensitive)
- All identifier prefixes must follow the specified format
- Tables must include all required columns
- No placeholder text may remain in the final output
- **All sensitive values must use templated placeholders**
- **No real credentials or PII may be present**

## Status

The status of the implementation plan must be clearly defined in the front matter and must reflect the current state of the plan. The status can be one of the following (status_color in brackets): `Completed` (bright_green badge), `In progress` (yellow badge), `Planned` (blue badge), `Deprecated` (red badge), or `On Hold` (orange badge). It should also be displayed as a badge in the introduction section.

```md
---
goal: [Concise Title Describing the Package Implementation Plan's Goal]
version: [Optional: e.g., 1.0, Date]
date_created: [YYYY-MM-DD]
last_updated: [Optional: YYYY-MM-DD]
owner: [Optional: Team/Individual responsible for this spec]
status: 'Completed'|'In progress'|'Planned'|'Deprecated'|'On Hold'
tags: [Optional: List of relevant tags or categories, e.g., `feature`, `upgrade`, `chore`, `architecture`, `migration`, `bug` etc]
---

# Introduction

![Status: <status>](https://img.shields.io/badge/status-<status>-<status_color>)

[A short concise introduction to the plan and the goal it is intended to achieve.]

## 1. Requirements & Constraints

[Explicitly list all requirements & constraints that affect the plan and constrain how it is implemented. Use bullet points or tables for clarity.]

- **REQ-001**: Requirement 1
- **SEC-001**: Security Requirement 1 (e.g., "All credentials must use secret management service")
- **[3 LETTERS]-001**: Other Requirement 1
- **CON-001**: Constraint 1
- **GUD-001**: Guideline 1
- **PAT-001**: Pattern to follow 1

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: [Describe the goal of this phase, e.g., "Implement feature X", "Refactor module Y", etc.]

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Description of task 1 (use placeholders like {{API_KEY}} for secrets) | ✅ | 2025-04-25 |
| TASK-002 | Description of task 2 | |  |
| TASK-003 | Description of task 3 | |  |

### Implementation Phase 2

- GOAL-002: [Describe the goal of this phase, e.g., "Implement feature X", "Refactor module Y", etc.]

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Description of task 4 | |  |
| TASK-005 | Description of task 5 | |  |
| TASK-006 | Description of task 6 | |  |

## 3. Alternatives

[A bullet point list of any alternative approaches that were considered and why they were not chosen. This helps to provide context and rationale for the chosen approach.]

- **ALT-001**: Alternative approach 1
- **ALT-002**: Alternative approach 2

## 4. Dependencies

[List any dependencies that need to be addressed, such as libraries, frameworks, or other components that the plan relies on. Use version ranges and anonymized examples.]

- **DEP-001**: Dependency 1 (e.g., "Library X v2.x or higher")
- **DEP-002**: Dependency 2 (e.g., "Service Y available at {{SERVICE_URL}}")

## 5. Files

[List the files that will be affected by the feature or refactoring task. Use relative paths from project root.]

- **FILE-001**: Description of file 1 (e.g., `src/services/auth.ts`)
- **FILE-002**: Description of file 2 (e.g., `config/database.yml` - use {{DB_PASSWORD}} placeholder)

## 6. Testing

[List the tests that need to be implemented to verify the feature or refactoring task. Include safety/security validation tests.]

- **TEST-001**: Description of test 1
- **TEST-002**: Description of test 2
- **TEST-SEC-001**: Verify no credentials committed to version control
- **TEST-SEC-002**: Confirm all secrets use placeholder format

## 7. Risks & Assumptions

[List any risks or assumptions related to the implementation of the plan. Include security and privacy risks.]

- **RISK-001**: Risk 1
- **RISK-SEC-001**: Risk that credentials might be accidentally committed (Mitigation: pre-commit hooks, secret scanning)
- **ASSUMPTION-001**: Assumption 1

## 8. Related Specifications / Further Reading

[Link to related spec 1]
[Link to relevant external documentation]
