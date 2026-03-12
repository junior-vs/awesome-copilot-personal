---
name: update-specification
description: 'Update an existing specification file for the solution, optimized for Generative AI consumption based on new requirements or updates to any existing code.'
---

# Update Specification

## Safety, Privacy, and Security

**CRITICAL: All specification updates must adhere to these safety rules:**

- **NO SECRETS OR CREDENTIALS**: Never include real API keys, passwords, database credentials, connection strings, private keys, certificates, or authentication tokens in specification updates
- **USE PLACEHOLDERS ONLY**: Use templated placeholders like `{{API_KEY}}`, `{{DB_PASSWORD}}`, `{{OAUTH_CLIENT_SECRET}}`, `{{DATABASE_CONNECTION_STRING}}`, `{{SERVICE_ENDPOINT}}`
- **NO INTERNAL INFRASTRUCTURE DETAILS**: Use anonymized/example hostnames like `api.example.com`, `db.example.internal`, `10.0.x.x` instead of real production infrastructure
- **NO PII OR SENSITIVE DATA**: Never include personally identifiable information, customer data, or proprietary business logic details in examples
- **ANONYMIZED EXAMPLES ONLY**: All code examples, configuration samples, and interface definitions must use fictional/anonymized data
- **RESPECT ORGANIZATIONAL POLICIES**: If organizational security policies, compliance requirements, or existing documentation standards conflict with this template, the organizational policies take precedence
- **PRESERVE EXISTING SAFETY CONTROLS**: When updating specifications, preserve existing placeholder patterns and security controls unless explicitly instructed to remove them

**File Validation Requirements:**
- Verify `${file}` exists in `/spec/` directory before attempting updates
- Validate the existing file follows the specification template structure
- If the file doesn't exist, create a new specification following the create-specification SKILL
- If the file is malformed or doesn't follow the template, request clarification before proceeding
- Preserve front matter fields (`date_created`, `owner`) from the original specification
- Update `last_updated` field with current date
- Increment `version` field appropriately (or add if missing)

**Update Conflict Resolution:**
- If new requirements conflict with existing requirements, document both and flag the conflict in the Rationale section
- Preserve existing content unless explicitly instructed to replace or remove it
- When adding new requirements, use the next available identifier number (e.g., if REQ-005 exists, start new requirements at REQ-006)
- If update instructions are ambiguous, use conservative interpretation and note clarification needs in Introduction

## Primary Directive

Your goal is to update the existing specification file `${file}` based on new requirements or updates to any existing code.

The specification file must define the requirements, constraints, and interfaces for the solution components in a manner that is clear, unambiguous, and structured for effective use by Generative AIs. Follow established documentation standards and ensure the content is machine-readable and self-contained.

## Best Practices for AI-Ready Specifications

- Use precise, explicit, and unambiguous language.
- Clearly distinguish between requirements, constraints, and recommendations.
- Use structured formatting (headings, lists, tables) for easy parsing.
- Avoid idioms, metaphors, or context-dependent references.
- Define all acronyms and domain-specific terms.
- Include examples and edge cases where applicable (using anonymized data and placeholders for sensitive values).
- Ensure the document is self-contained and does not rely on external context.
- **Enforce safety, privacy, and security controls** in all updated content.

The specification should be saved in the [/spec/](/spec/) directory and named according to the following convention: `[a-z0-9-]+.md`, where the name should be descriptive of the specification's content and starting with the highlevel purpose, which is one of [schema, tool, data, infrastructure, process, architecture, or design].

The specification file must be formatted in well formed Markdown.

Specification files must follow the template below, ensuring that all sections are filled out appropriately. The front matter for the markdown should be structured correctly as per the example following:

```md
---
title: [Concise Title Describing the Specification's Focus]
version: [Optional: e.g., 1.0, Date - increment appropriately when updating]
date_created: [YYYY-MM-DD - preserve from original]
last_updated: [YYYY-MM-DD - update to current date]
owner: [Optional: Team/Individual responsible for this spec - preserve from original unless ownership changes]
tags: [Optional: List of relevant tags or categories, e.g., `infrastructure`, `process`, `design`, `app` etc]
---

# Introduction

[A short concise introduction to the specification and the goal it is intended to achieve. When updating, note the nature of changes if significant.]

## 1. Purpose & Scope

[Provide a clear, concise description of the specification's purpose and the scope of its application. State the intended audience and any assumptions.]

## 2. Definitions

[List and define all acronyms, abbreviations, and domain-specific terms used in this specification.]

## 3. Requirements, Constraints & Guidelines

[Explicitly list all requirements, constraints, rules, and guidelines. Use bullet points or tables for clarity. When adding new requirements, use the next available identifier number.]

- **REQ-001**: Requirement 1
- **SEC-001**: Security Requirement 1 (e.g., "All credentials must use secret management service")
- **[3 LETTERS]-001**: Other Requirement 1
- **CON-001**: Constraint 1
- **GUD-001**: Guideline 1
- **PAT-001**: Pattern to follow 1

## 4. Interfaces & Data Contracts

[Describe the interfaces, APIs, data contracts, or integration points. Use tables or code blocks for schemas and examples. **Use placeholders for all sensitive configuration values.**]

Example:
```json
{
  "endpoint": "{{API_ENDPOINT}}",
  "apiKey": "{{API_KEY}}",
  "timeout": 30000
}
```

## 5. Acceptance Criteria

[Define clear, testable acceptance criteria for each requirement using Given-When-Then format where appropriate.]

- **AC-001**: Given [context], When [action], Then [expected outcome]
- **AC-002**: The system shall [specific behavior] when [condition]
- **AC-003**: [Additional acceptance criteria as needed]

## 6. Test Automation Strategy

[Define the testing approach, frameworks, and automation requirements.]

- **Test Levels**: Unit, Integration, End-to-End
- **Frameworks**: MSTest, FluentAssertions, Moq (for .NET applications)
- **Test Data Management**: [approach for test data creation and cleanup]
- **CI/CD Integration**: [automated testing in GitHub Actions pipelines]
- **Coverage Requirements**: [minimum code coverage thresholds]
- **Performance Testing**: [approach for load and performance testing]

## 7. Rationale & Context

[Explain the reasoning behind the requirements, constraints, and guidelines. Provide context for design decisions.]

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

**Note**: This section should focus on architectural and business dependencies, not specific package implementations. For example, specify "OAuth 2.0 authentication library" rather than "Microsoft.AspNetCore.Authentication.JwtBearer v6.0.1".

## 9. Examples & Edge Cases

```code
// Code snippet or data example demonstrating the correct application of the guidelines, including edge cases
```

## 10. Validation Criteria

[List the criteria or tests that must be satisfied for compliance with this specification.]

## 11. Related Specifications / Further Reading

[Link to related spec 1]
[Link to relevant external documentation]
