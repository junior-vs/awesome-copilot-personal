---
name: copilot-instructions-blueprint-generator
description: 'Technology-agnostic blueprint generator for creating comprehensive, secure, and pattern-validated copilot-instructions.md files that guide GitHub Copilot to produce code consistent with project standards, architecture patterns, and exact technology versions by analyzing existing codebase patterns while validating security and quality.'
---

# Copilot Instructions Blueprint Generator

## Configuration Variables
${PROJECT_TYPE="Auto-detect|.NET|Java|JavaScript|TypeScript|React|Angular|Python|Multiple|Other"} <!-- Primary technology -->
${ARCHITECTURE_STYLE="Layered|Microservices|Monolithic|Domain-Driven|Event-Driven|Serverless|Mixed"} <!-- Architectural approach -->
${CODE_QUALITY_FOCUS="Maintainability|Performance|Security|Accessibility|Testability|All"} <!-- Quality priorities -->
${DOCUMENTATION_LEVEL="Minimal|Standard|Comprehensive"} <!-- Documentation requirements -->
${TESTING_REQUIREMENTS="Unit|Integration|E2E|TDD|BDD|All"} <!-- Testing approach -->
${VERSIONING="Semantic|CalVer|Custom"} <!-- Versioning approach -->
${SECURITY_VALIDATION="Enabled|Strict|Advisory"} <!-- Security pattern validation level -->

## Generated Prompt

"Generate a comprehensive, security-validated copilot-instructions.md file that will guide GitHub Copilot to produce code consistent with our project's standards, architecture, and technology versions. The instructions must be strictly based on actual code patterns in our codebase while ensuring those patterns meet security and quality standards. Follow this approach:

### 1. Core Instruction Structure

```markdown
# GitHub Copilot Instructions

## Critical Safety Notice

⚠️ **Pattern Validation Required:** While this document guides you to follow existing codebase patterns, you must NEVER replicate patterns that:
- Contain security vulnerabilities (SQL injection, XSS, buffer overflows, etc.)
- Use deprecated or insecure APIs
- Lack input validation or sanitization
- Expose sensitive data or credentials
- Violate the principle of least privilege

When unsafe patterns are detected in the codebase, flag them and suggest secure alternatives based on current security best practices.

## Priority Guidelines

When generating code for this repository:

1. **Security First**: Security takes precedence over pattern consistency. Never replicate insecure patterns.
2. **Version Compatibility**: Always detect and respect the exact versions of languages, frameworks, and libraries used in this project
3. **Context Files**: Prioritize patterns and standards defined in the .github/copilot directory
4. **Validated Codebase Patterns**: When context files don't provide specific guidance, scan the codebase for established patterns and validate their quality
5. **Architectural Consistency**: Maintain our ${ARCHITECTURE_STYLE} architectural style and established boundaries
6. **Code Quality**: Prioritize ${CODE_QUALITY_FOCUS == "All" ? "maintainability, performance, security, accessibility, and testability" : CODE_QUALITY_FOCUS} in all generated code

## Technology Version Detection

Before generating code, scan the codebase to identify:

1. **Language Versions**: Detect the exact versions of programming languages in use
   - Examine project files, configuration files, and package managers
   - Look for language-specific version indicators (e.g., <LangVersion> in .NET projects)
   - Never use language features beyond the detected version
   - Flag any usage of deprecated features in the detected version

2. **Framework Versions**: Identify the exact versions of all frameworks
   - Check package.json, .csproj, pom.xml, requirements.txt, etc.
   - Respect version constraints when generating code
   - Never suggest features not available in the detected framework versions
   - Flag frameworks with known security vulnerabilities

3. **Library Versions**: Note the exact versions of key libraries and dependencies
   - Generate code compatible with these specific versions
   - Never use APIs or features not available in the detected versions
   - Flag libraries with known security advisories

4. **Security Dependencies**: Identify security-critical dependencies
   - Note authentication/authorization libraries and their versions
   - Identify cryptographic libraries and their configurations
   - Document input validation approaches

## Context Files

Prioritize the following files in .github/copilot directory (if they exist):

- **architecture.md**: System architecture guidelines
- **tech-stack.md**: Technology versions and framework details
- **coding-standards.md**: Code style and formatting standards
- **security-guidelines.md**: Security requirements and patterns
- **folder-structure.md**: Project organization guidelines
- **exemplars.md**: Exemplary code patterns to follow

## Codebase Scanning Instructions

When context files don't provide specific guidance:

1. **Identify Similar Files**: Find files similar to the one being modified or created
2. **Analyze Patterns**: Look for patterns in:
   - Naming conventions (classes, methods, variables, files)
   - Code organization and structure
   - Error handling and exception management
   - Logging approaches and levels
   - Documentation style and completeness
   - Testing patterns and coverage

3. **Validate Pattern Quality**: Before adopting discovered patterns, verify they:
   - Follow security best practices
   - Don't contain common anti-patterns
   - Use proper error handling
   - Include appropriate input validation
   - Are consistent across multiple files (not isolated incidents)

4. **Pattern Precedence**: When multiple patterns exist:
   - Prioritize patterns from recently modified files with high test coverage
   - Prefer patterns that include security measures over those that don't
   - Choose patterns that are most widely adopted (3+ instances)
   - When patterns conflict significantly, flag for human review

5. **Pattern Limitations**: Never introduce patterns not found in the existing codebase unless:
   - Required for security (e.g., adding missing input validation)
   - Fixing deprecated API usage
   - Addressing known vulnerabilities

## Code Quality Standards

### Security (Mandatory for All Code)
- **Input Validation**: Validate and sanitize all external inputs
- **Authentication & Authorization**: Follow existing patterns for auth, ensure proper access control
- **Data Protection**: Handle sensitive data according to existing patterns, encrypt at rest and in transit
- **Injection Prevention**: Use parameterized queries, escape user input properly
- **Error Handling**: Don't expose sensitive information in error messages
- **Dependency Security**: Follow existing patterns for dependency management
- **Logging Security**: Never log sensitive data (passwords, tokens, PII)

${CODE_QUALITY_FOCUS.includes("Maintainability") || CODE_QUALITY_FOCUS == "All" ? `### Maintainability
- Write self-documenting code with clear, descriptive naming
- Follow the naming and organization conventions evident in the codebase
- Follow established patterns for consistency
- Keep functions focused on single responsibilities (max 50 lines as default)
- Limit function complexity (cyclomatic complexity < 10 as default)
- Add comments only for non-obvious business logic` : ""}

${CODE_QUALITY_FOCUS.includes("Performance") || CODE_QUALITY_FOCUS == "All" ? `### Performance
- Follow existing patterns for memory and resource management
- Avoid N+1 queries; use batch operations where appropriate
- Follow established patterns for handling computationally expensive operations
- Follow established patterns for asynchronous operations
- Apply caching consistently with existing patterns
- Monitor and optimize based on profiling data` : ""}

${CODE_QUALITY_FOCUS.includes("Accessibility") || CODE_QUALITY_FOCUS == "All" ? `### Accessibility
- Follow WCAG 2.1 AA standards as baseline
- Follow existing accessibility patterns in the codebase
- Match ARIA attribute usage with existing components
- Maintain keyboard navigation support consistent with existing code
- Ensure sufficient color contrast (4.5:1 for text)
- Apply text alternative patterns consistent with the codebase` : ""}

${CODE_QUALITY_FOCUS.includes("Testability") || CODE_QUALITY_FOCUS == "All" ? `### Testability
- Follow established patterns for testable code
- Match dependency injection approaches used in the codebase
- Apply the same patterns for managing dependencies
- Follow established mocking and test double patterns
- Match the testing style used in existing tests
- Aim for minimum 80% code coverage for new code` : ""}

## Documentation Requirements

${DOCUMENTATION_LEVEL == "Minimal" ?
`- Match the level and style of comments found in existing code
- Document public APIs and non-obvious behavior
- Follow existing patterns for documenting parameters
- Keep documentation concise and up-to-date` : ""}

${DOCUMENTATION_LEVEL == "Standard" ?
`- Follow the exact documentation format found in the codebase
- Match the XML/JSDoc style and completeness of existing comments
- Document all public methods: purpose, parameters, returns, exceptions
- Follow existing patterns for usage examples
- Match class-level documentation style and content
- Document security considerations for sensitive operations` : ""}

${DOCUMENTATION_LEVEL == "Comprehensive" ?
`- Follow the most detailed documentation patterns found in the codebase
- Match the style and completeness of the best-documented code
- Document public and internal APIs comprehensively
- Follow existing patterns for linking documentation
- Match the level of detail in explanations of design decisions
- Include security considerations, performance notes, and usage examples` : ""}

## Testing Approach

### Test Coverage Requirements
- All new code must include corresponding tests
- Follow the test patterns most prevalent in the codebase
- Maintain or improve existing test coverage

${TESTING_REQUIREMENTS.includes("Unit") || TESTING_REQUIREMENTS == "All" ?
`### Unit Testing
- Match the exact structure and style of existing unit tests
- Follow the same naming conventions for test classes and methods (e.g., MethodName_Scenario_ExpectedBehavior)
- Use the same assertion patterns found in existing tests
- Apply the same mocking approach used in the codebase
- Follow existing patterns for test isolation
- Test edge cases, error conditions, and security boundaries` : ""}

${TESTING_REQUIREMENTS.includes("Integration") || TESTING_REQUIREMENTS == "All" ?
`### Integration Testing
- Follow the same integration test patterns found in the codebase
- Match existing patterns for test data setup and teardown
- Use the same approach for testing component interactions
- Follow existing patterns for verifying system behavior
- Test security boundaries and authentication/authorization` : ""}

${TESTING_REQUIREMENTS.includes("E2E") || TESTING_REQUIREMENTS == "All" ?
`### End-to-End Testing
- Match the existing E2E test structure and patterns
- Follow established patterns for UI testing
- Apply the same approach for verifying user journeys
- Test critical security flows (authentication, authorization, data access)` : ""}

${TESTING_REQUIREMENTS.includes("TDD") || TESTING_REQUIREMENTS == "All" ?
`### Test-Driven Development
- Write tests before implementation
- Follow TDD patterns evident in the codebase
- Match the progression of test cases seen in existing code
- Apply the same refactoring patterns after tests pass` : ""}

${TESTING_REQUIREMENTS.includes("BDD") || TESTING_REQUIREMENTS == "All" ?
`### Behavior-Driven Development
- Match the existing Given-When-Then structure in tests
- Follow the same patterns for behavior descriptions
- Apply the same level of business focus in test cases
- Ensure scenarios cover security requirements` : ""}

## Technology-Specific Guidelines

${PROJECT_TYPE == ".NET" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### .NET Guidelines
- Detect and strictly adhere to the specific .NET version in use
- Use only C# language features compatible with the detected version
- Follow LINQ usage patterns exactly as they appear in the codebase
- Match async/await usage patterns from existing code (avoid async void except for event handlers)
- Apply the same dependency injection approach used in the codebase
- Use the same collection types and patterns found in existing code
- Follow existing patterns for IDisposable and resource management
- **Security**: Use parameterized SQL queries, validate model state, use [Authorize] attributes appropriately` : ""}

${PROJECT_TYPE == "Java" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### Java Guidelines
- Detect and adhere to the specific Java version in use
- Follow the exact same design patterns found in the codebase
- Match exception handling patterns from existing code
- Use the same collection types and approaches found in the codebase
- Apply the dependency injection patterns evident in existing code
- Follow existing patterns for resource management (try-with-resources)
- **Security**: Use PreparedStatement, validate inputs, follow existing authentication patterns` : ""}

${PROJECT_TYPE == "JavaScript" || PROJECT_TYPE == "TypeScript" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### JavaScript/TypeScript Guidelines
- Detect and adhere to the specific ECMAScript/TypeScript version in use
- Follow the same module import/export patterns found in the codebase
- Match TypeScript type definitions with existing patterns (use strict mode if enabled)
- Use the same async patterns (promises, async/await) as existing code
- Follow error handling patterns from similar files
- **Security**: Sanitize user input, use parameterized queries, avoid eval(), validate on both client and server` : ""}

${PROJECT_TYPE == "React" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### React Guidelines
- Detect and adhere to the specific React version in use
- Match component structure patterns from existing components (functional vs. class components)
- Follow the same hooks and lifecycle patterns found in the codebase
- Apply the same state management approach used in existing components
- Match prop typing and validation patterns from existing code
- **Security**: Sanitize dangerouslySetInnerHTML usage, validate props, follow CSP policies` : ""}

${PROJECT_TYPE == "Angular" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### Angular Guidelines
- Detect and adhere to the specific Angular version in use
- Follow the same component and module patterns found in the codebase
- Match decorator usage exactly as seen in existing code
- Apply the same RxJS patterns found in the codebase (proper subscription management)
- Follow existing patterns for component communication
- **Security**: Use Angular's built-in sanitization, validate route guards, secure HTTP interceptors` : ""}

${PROJECT_TYPE == "Python" || PROJECT_TYPE == "Auto-detect" || PROJECT_TYPE == "Multiple" ? `### Python Guidelines
- Detect and adhere to the specific Python version in use
- Follow PEP 8 style guide unless codebase uses different conventions
- Follow the same import organization found in existing modules
- Match type hinting approaches if used in the codebase
- Apply the same error handling patterns found in existing code
- Follow the same module organization patterns
- **Security**: Use parameterized queries, validate inputs, sanitize outputs, follow existing patterns for secrets management` : ""}

## Error Handling & Resilience

- **Consistent Exception Handling**: Follow existing patterns for exception handling
- **Graceful Degradation**: Handle failures gracefully without exposing sensitive information
- **Logging**: Log errors appropriately (match existing logging patterns)
- **User Feedback**: Provide meaningful error messages without revealing system details
- **Retry Logic**: Follow existing patterns for transient failure handling

## Edge Cases & Conflict Resolution

### When No Clear Pattern Exists
1. Fall back to industry best practices for the specific technology stack
2. Prioritize security and maintainability
3. Document the rationale for the chosen approach
4. Flag for human review if the decision is significant

### When Patterns Conflict
1. Prioritize security-compliant patterns over insecure ones
2. Choose patterns from files with higher test coverage
3. Prefer recently modified files over legacy code
4. If still unclear, flag for human review

### When Codebase is Small or New
1. Use established best practices for the technology stack
2. Follow official framework guidelines
3. Prioritize security, testability, and maintainability
4. Establish clear patterns for future consistency

## Version Control Guidelines

${VERSIONING == "Semantic" ?
`- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- Match existing patterns for documenting breaking changes
- Follow the same approach for deprecation notices
- Update version numbers according to the scope of changes` : ""}

${VERSIONING == "CalVer" ?
`- Follow Calendar Versioning patterns as applied in the codebase
- Match existing patterns for documenting changes
- Follow the same approach for highlighting significant changes
- Use the established date format consistently` : ""}

${VERSIONING == "Custom" ?
`- Match the exact versioning pattern observed in the codebase
- Follow the same changelog format used in existing documentation
- Apply the same tagging conventions used in the project
- Maintain consistency with historical versioning` : ""}

## General Best Practices

- **Naming**: Follow naming conventions exactly as they appear in existing code
- **Organization**: Match code organization patterns from similar files
- **Error Handling**: Apply error handling consistent with existing patterns
- **Testing**: Follow the same approach to testing as seen in the codebase
- **Logging**: Match logging patterns from existing code (level, format, content)
- **Configuration**: Use the same approach to configuration as seen in the codebase
- **Comments**: Add comments where the "why" is not obvious from the code
- **Consistency**: When in doubt, prioritize consistency with existing code over external best practices
- **Security Exception**: Deviate from existing patterns when necessary to fix security issues

## Project-Specific Guidance

- **Thorough Analysis**: Scan the codebase thoroughly before generating any code
- **Architectural Boundaries**: Respect existing architectural boundaries without exception
- **Style Matching**: Match the style and patterns of surrounding code
- **Security Validation**: Always validate discovered patterns for security issues
- **Quality Check**: Ensure adopted patterns represent good practices, not anti-patterns
- **Human Escalation**: When uncertain about security or pattern quality, flag for human review
```

### 2. Codebase Analysis Instructions

To create the copilot-instructions.md file, perform comprehensive analysis:

#### Phase 1: Technology Stack Identification

1. **Identify Exact Technology Versions**:
   - ${PROJECT_TYPE == "Auto-detect" ? "Detect all programming languages, frameworks, and libraries by scanning file extensions and configuration files" : `Focus on ${PROJECT_TYPE} technologies`}
   - Extract precise version information from:
     - package.json, package-lock.json (Node.js)
     - .csproj, packages.config, Directory.Build.props (.NET)
     - pom.xml, build.gradle (Java)
     - requirements.txt, pyproject.toml, Pipfile (Python)
     - composer.json (PHP)
   - Document version constraints and compatibility requirements
   - Cross-reference with .nvmrc, .python-version, .tool-versions

2. **Security Dependency Audit**:
   - Identify security-critical dependencies (auth, crypto, validation libraries)
   - Note versions of security libraries
   - Flag any dependencies with known vulnerabilities
   - Document security configuration patterns

#### Phase 2: Architecture & Pattern Analysis

3. **Understand Architecture**:
   - Analyze folder structure and module organization
   - Identify clear layer boundaries and component relationships
   - Document communication patterns between components
   - Map data flow and dependency directions
   - Identify architectural style (${ARCHITECTURE_STYLE})

4. **Document Code Patterns**:
   - **Naming Conventions**: Catalog naming patterns for classes, methods, variables, files
   - **Documentation Styles**: Note comment styles, completeness, and formats (XML, JSDoc, etc.)
   - **Error Handling**: Document exception handling patterns, error logging approaches
   - **Testing Approaches**: Map test structures, naming conventions, assertion styles
   - **Pattern Frequency**: Count pattern occurrences to identify dominant conventions

5. **Pattern Quality Validation**:
   - **Security Review**: Evaluate patterns for security best practices
     - Check for SQL injection prevention (parameterized queries)
     - Validate input sanitization implementations
     - Review authentication and authorization patterns
     - Check for proper error handling (no sensitive data leakage)
     - Verify secure communication patterns (HTTPS, encryption)
   - **Anti-Pattern Detection**: Flag common anti-patterns
     - God classes or methods
     - Circular dependencies
     - Hard-coded credentials or configuration
     - Lack of input validation
     - Missing error handling
   - **Best Practice Alignment**: Compare patterns with industry standards
     - OWASP security guidelines
     - Framework-specific best practices
     - SOLID principles adherence

#### Phase 3: Quality Standards Documentation

6. **Note Quality Standards**:
   - **Performance**: Identify optimization techniques actually used
     - Caching strategies
     - Async/await patterns
     - Database query optimization
     - Resource pooling
   - **Security**: Document security practices implemented
     - Authentication/authorization mechanisms
     - Input validation techniques
     - Data encryption approaches
     - Secret management patterns
   - **Accessibility**: Note accessibility features present (if applicable)
     - ARIA usage
     - Keyboard navigation
     - Screen reader support
     - Color contrast standards
   - **Code Quality**: Document quality patterns
     - Code complexity metrics
     - Function length patterns
     - Test coverage levels
     - Dependency management approaches

#### Phase 4: Edge Case & Conflict Documentation

7. **Handle Pattern Conflicts**:
   - Document conflicting patterns found in the codebase
   - Provide resolution strategy based on:
     - File modification date
     - Test coverage
     - Security compliance
     - Frequency of pattern usage
   - Flag significant conflicts for human review

8. **Define Fallback Strategies**:
   - For areas with no clear patterns
   - For deprecated or insecure patterns
   - For new features not present in codebase
   - For technology-specific best practices

### 3. Implementation Notes

The final copilot-instructions.md should:

- **Location**: Be placed in the .github/copilot directory
- **Evidence-Based**: Reference only patterns and standards that exist in the codebase
- **Security-Validated**: Include security review findings and guidelines
- **Version-Explicit**: Include explicit version compatibility requirements
- **Quality-Focused**: Avoid prescribing practices not validated for quality
- **Example-Rich**: Provide concrete examples from the codebase
- **Balanced**: Be comprehensive yet concise enough for effective use
- **Conflict-Aware**: Address known pattern conflicts with clear resolution guidance
- **Fallback-Ready**: Include guidance for scenarios without clear patterns

### 4. Security Validation Checklist

${SECURITY_VALIDATION == "Strict" ? `
Before finalizing the copilot-instructions.md, verify:

☐ All authentication/authorization patterns are secure and up-to-date
☐ Input validation patterns are comprehensive and properly implemented
☐ No hard-coded credentials or sensitive data in documented patterns
☐ SQL/NoSQL query patterns use parameterization or safe ORM practices
☐ Error handling patterns don't expose sensitive system information
☐ Cryptographic practices use current standards (no MD5, SHA1 for security)
☐ Session management follows security best practices
☐ CORS, CSP, and other security headers are properly configured
☐ Dependencies with known vulnerabilities are flagged
☐ Logging patterns exclude sensitive data (passwords, tokens, PII)
☐ File upload patterns include proper validation and sanitization
☐ API security patterns handle authentication, rate limiting, and validation

Flag any security concerns for immediate review.
` : SECURITY_VALIDATION == "Enabled" ? `
Security review checklist (advisory):
- Review authentication and authorization patterns
- Check input validation approaches
- Verify SQL query safety
- Check for sensitive data exposure
- Review error handling security
- Validate cryptographic approaches
` : ""}

### 5. Quality Metrics to Include

Document the following metrics found in the codebase:

- **Test Coverage**: Average test coverage percentage
- **Code Complexity**: Typical cyclomatic complexity ranges
- **Function Length**: Typical function/method length patterns
- **File Organization**: Average file sizes and organization patterns
- **Documentation Density**: Comment-to-code ratio in well-documented files
- **Dependency Count**: Number and types of dependencies per module

Important: Only include guidance based on patterns actually observed and validated in the codebase. Explicitly instruct Copilot to prioritize security and code quality, while maintaining consistency with existing code where those patterns meet quality standards. When existing patterns are problematic, provide secure alternatives.
"

## Expected Output

A comprehensive, security-validated copilot-instructions.md file that will guide GitHub Copilot to produce code that is:
1. ✅ Perfectly compatible with your existing technology versions
2. ✅ Consistent with your established patterns and architecture
3. ✅ Secure and free from common vulnerabilities
4. ✅ Aligned with quality best practices
5. ✅ Capable of handling edge cases and pattern conflicts

The output should enable GitHub Copilot to make informed, secure, and context-aware code generation decisions.
