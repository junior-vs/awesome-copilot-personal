---
name: create-specification
description: 'Create a new specification file for the solution, optimized for Generative AI consumption, with strong safety, privacy, and clarity guarantees.'
---

# Create Specification

Your goal is to create a new specification file for `${input:SpecPurpose}`.

The specification file must define the requirements, constraints, and interfaces for the solution components in a manner that is clear, unambiguous, and structured for effective use by Generative AIs. Follow established documentation standards and ensure the content is machine-readable, self-contained, and safe to share.

## Safety, Privacy, and Scope

- **No Secrets or PII**: Never include real secrets, credentials, API keys, tokens, internal hostnames, IP addresses, or personally identifiable information (PII).
  - Always use obvious placeholders (e.g., `{{API_KEY}}`, `{{DB_PASSWORD}}`, `https://example.com`, `user@example.com`).
- **Anonymized Examples Only**: Use fictional or generic example data (names, emails, IDs, organizations).
- **Respect Organizational Policies**: If other instructions or repository documentation define security, privacy, or compliance rules, follow them and do not weaken those controls.
- **Ambiguous Purpose Handling**: If `${input:SpecPurpose}` is vague, broad, or conflicting:
  - Prefer a conservative, generic interpretation.
  - Clearly document assumptions in the **Purpose & Scope** and **Rationale & Context** sections.
- **Non-Destructive Behavior**: The specification must describe *what* is required, not destructive or harmful *how-to* instructions (no guidance on exploitation, data exfiltration, etc.).

## Best Practices for AI-Ready Specifications

- Use precise, explicit, and unambiguous language.
- Clearly distinguish between requirements, constraints, and recommendations.
- Use structured formatting (headings, lists, tables) for easy parsing.
- Avoid idioms, metaphors, or context-dependent references.
- Define all acronyms and domain-specific terms.
- Include examples and edge cases where applicable, using only fictional/sample data.
- Ensure the document is self-contained and does not rely on undocumented external context.
- Prefer technology-agnostic phrasing; when examples are stack-specific, label them as such.

The specification should be saved in the `/spec/` directory and named according to the following convention:

- **File Path**: `/spec/`
- **File Name Pattern**: `spec-[a-z0-9-]+.md`
- The name should be descriptive of the specification's content and start with the high-level purpose, which is one of:
  `schema`, `tool`, `data`, `infrastructure`, `process`, `architecture`, or `design`.
  - Example: `spec-architecture-order-service.md`, `spec-data-user-profile-schema.md`.

The specification file must be formatted as well-formed Markdown.

Specification files must follow the template below, ensuring that all sections are filled out appropriately. The front matter for the markdown should be structured correctly as per the example:

```md
---
title: [Concise Title Describing the Specification's Focus]
version: [Optional: e.g., 1.0, 2026-03-02]
date_created: [YYYY-MM-DD]
last_updated: [Optional: YYYY-MM-DD]
owner: [Optional: Team/Individual responsible for this spec]
tags: [Optional: List of relevant tags or categories, e.g., `infrastructure`, `process`, `design`, `app` etc]
---

# Introduction

[A short concise introduction to the specification and the goal it is intended to achieve.]

## 1. Purpose & Scope

[Provide a clear, concise description of the specification's purpose and the scope of its application. State the intended audience, assumptions, and any out-of-scope items.]

## 2. Definitions

[List and define all acronyms, abbreviations, and domain-specific terms used in this specification.]

## 3. Requirements, Constraints & Guidelines

[Explicitly list all requirements, constraints, rules, and guidelines. Use bullet points or tables for clarity.]

- **REQ-001**: Requirement 1
- **SEC-001**: Security Requirement 1
- **[3 LETTERS]-001**: Other Requirement 1
- **CON-001**: Constraint 1
- **GUD-001**: Guideline 1
- **PAT-001**: Pattern to follow 1

## 4. Interfaces & Data Contracts

[Describe the interfaces, APIs, data contracts, or integration points. Use tables or code blocks for schemas and examples.]

- Clearly specify request/response shapes, including required/optional fields.
- Use only anonymized or placeholder values in examples.

## 5. Acceptance Criteria

[Define clear, testable acceptance criteria for each requirement using Given-When-Then format where appropriate.]

- **AC-001**: Given [context], When [action], Then [expected outcome]
- **AC-002**: The system shall [specific behavior] when [condition]
- **AC-003**: [Additional acceptance criteria as needed]

## 6. Test Automation Strategy

[Define the testing approach, frameworks, and automation requirements. Keep this section technology-agnostic by default; any stack-specific examples must be labeled explicitly.]

- **Test Levels**: Unit, Integration, End-to-End
- **Frameworks (Example for .NET)**: MSTest, FluentAssertions, Moq
  - For other stacks, use equivalent, widely adopted testing and assertion libraries.
- **Test Data Management**: [approach for test data creation and cleanup]
- **CI/CD Integration**: [automated testing in CI pipelines, e.g., GitHub Actions]
- **Coverage Requirements**: [minimum code coverage thresholds]
- **Performance Testing**: [approach for load and performance testing]

## 7. Rationale & Context

[Explain the reasoning behind the requirements, constraints, and guidelines. Provide context for design decisions and recorded assumptions.]

## 8. Dependencies & External Integrations

[Define the external systems, services, and architectural dependencies required for this specification. Focus on **what** is needed rather than **how** it's implemented. Avoid specific package or library versions unless they represent architectural constraints.]

### External Systems
- **EXT-001**: [External system name] - [Purpose and integration type]

### Third-Party Services
- **SVC-001**: [Service name] - [Required capabilities and SLA requirements]

### Infrastructure Dependencies
- **INF-001**: [Infrastructure component] - [Requirements and constraints]

### Data Dependencies
- **DAT-001**: [External data source] - [Format, frequency, and access requirements]

### Technology Platform Dependencies
- **PLT-001**: [Platform/runtime requirement] - [Version constraints and rationale]

### Compliance Dependencies
- **COM-001**: [Regulatory or compliance requirement] - [Impact on implementation]

**Note**: This section should focus on architectural and business dependencies, not specific package implementations. For example, specify “OAuth 2.0 authentication library” rather than “Microsoft.AspNetCore.Authentication.JwtBearer v6.0.1”.

## 9. Examples & Edge Cases

```code
// Code snippet or data example demonstrating the correct application of the guidelines,
// including edge cases, using only anonymized or placeholder values.
// Example:
{
  "apiKey": "{{API_KEY}}",
  "endpoint": "https://api.example.com",
  "database": {
    "host": "db.example.internal",
    "port": 5432,
    "username": "app_user",
    "password": "{{DB_PASSWORD}}"
  },
  "user": {
    "email": "user@example.com",
    "name": "Example User"
  }
}
```

## 10. Validation Criteria

[List the criteria or tests that must be satisfied for compliance with this specification.]

- All requirements must be testable and verifiable
- All examples must use placeholder values for sensitive data
- All acceptance criteria must be measurable
- Security requirements must be validated through automated tests
- No real credentials or PII may be present in the specification

## 11. Related Specifications / Further Reading

[Link to related spec 1]
[Link to relevant external documentation]

```

