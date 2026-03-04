---
description: 'Core Java development guidelines for JDK 21 LTS: naming, data modeling, null safety, streams, exceptions, and static analysis compliance'
applyTo: '**/*.java'
---

# Java Core Development Guidelines (JDK 21 LTS)

## Project Overview

> **Fill in before using this file in your repository.**
> - **Project type**: e.g., REST API / Microservice / Monolith / Batch Job
> - **Architecture**: e.g., Hexagonal / Layered (Controller → Service → Repository)
> - **Key modules**: e.g., `domain/`, `application/`, `infra/`, `api/`
> - **Build tool**: Maven (`<java.version>21</java.version>`) or Gradle (`sourceCompatibility = JavaVersion.VERSION_21`)
> - **Main frameworks**: e.g., Spring Boot 3.x, Quarkus 3.x, Micronaut 4.x

---

## JDK 21 Stable Feature Baseline

Use these features freely — they are **not** preview:

| Feature | Stable Since |
| :--- | :--- |
| Records | JDK 16 |
| Sealed Classes | JDK 17 |
| Pattern Matching for `instanceof` | JDK 16 |
| Pattern Matching for `switch` | JDK 21 |
| Text Blocks | JDK 15 |
| `var` (local type inference) | JDK 10 |
| Sequenced Collections (`getFirst`, `getLast`) | JDK 21 |
| `Stream.toList()` (unmodifiable) | JDK 16 |

> **Do not generate** code using JDK 22+ or preview features unless the project build files target that version and the user explicitly requests it.

---

## Naming Conventions

Follow [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html):

| Identifier | Style | Example |
| :--- | :--- | :--- |
| Classes / Records / Enums | `UpperCamelCase` | `OrderService`, `PaymentMethod` |
| Methods | `lowerCamelCase` verb | `calculateTotal()`, `isAvailable()` |
| Variables / Record components | `lowerCamelCase` noun | `createdAt`, `customerId` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Packages | `lowercase` | `com.example.order` |

- Use `var` only when the type is **obvious** from the right-hand side (e.g., `var list = new ArrayList<String>()`). Avoid when the return type is not immediately clear.
- Avoid generic names like `data`, `obj`, `list1`, `temp`.

---

## Data Modeling

- **Prefer Records** for all transparent data carriers (DTOs, value objects, results). They eliminate manual `equals`, `hashCode`, and `toString`.
- Use **compact constructors** for validation invariants.
- Use **Sealed interfaces** to model closed domain hierarchies (Algebraic Data Types). This allows the compiler to enforce exhaustiveness in `switch` expressions.

```java
// Good: Domain modeling with sealed + records
public sealed interface PaymentMethod permits CreditCard, PayPal {}
public record CreditCard(String number, String vaultId) implements PaymentMethod {}
public record PayPal(String email) implements PaymentMethod {}

// Good: Compact constructor for validation
public record Money(BigDecimal amount, String currency) {
    public Money {
        Objects.requireNonNull(amount, "amount is required");
        Objects.requireNonNull(currency, "currency is required");
        if (amount.signum() < 0) throw new IllegalArgumentException("Amount cannot be negative");
    }
}
```

---

## Immutability

- Design classes to be immutable by default. Use `final` fields and `record`.
- Use `List.of()`, `Set.of()`, `Map.of()` for collections that must not change.
- When accepting mutable collections in a constructor, always create a defensive copy:

```java
public record Order(List<String> items) {
    public Order {
        items = List.copyOf(items); // Unmodifiable defensive copy
    }
}
```

---

## Null Safety

- Never return `null` for collections — return `List.of()`, `Set.of()`, or `Map.of()`.
- Use `Optional<T>` **only as a return type** to signal an absent value. Never use `Optional` for fields or method parameters.
- Use `Objects.requireNonNull(val, "message")` in constructors and factory methods for mandatory arguments.

```java
// Good
public Optional<User> findById(String id) { ... }

// Avoid
public User findById(String id) { return null; } // Never return null
public void process(Optional<String> name) { ... } // Never Optional as parameter
```

---

## Streams & Functional Style

- Use Streams for collection processing when the pipeline is clear and readable.
- Always use `Stream.toList()` (JDK 16+) for unmodifiable results. Avoid `Collectors.toList()` when immutability is desired.
- Use `IntStream`, `LongStream`, `DoubleStream` for numeric operations to avoid boxing overhead.
- Keep pipelines **pure**: never modify external state inside `.map()`, `.filter()`, or `.peek()`.
- If a pipeline requires multi-line lambdas or complex state, refactor to a loop or extract private helper methods.

```java
// Good: Pure, declarative pipeline
List<String> activeNames = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();

// Avoid: Side effect inside pipeline
List<String> results = new ArrayList<>();
users.stream().filter(User::isActive).forEach(u -> results.add(u.name())); // Don't do this
```

---

## Switch Expressions & Pattern Matching

- Use **switch expressions** (not statements) for all multi-branch logic. Avoid `default` when covering a sealed hierarchy — the compiler will enforce exhaustiveness.
- Use **Pattern Matching for `instanceof`** to avoid manual casting.
- Use **guarded patterns** (`when`) for conditional refinement.

```java
// Good: Exhaustive switch on sealed type
double fee = switch (payment) {
    case CreditCard(var num, var vault) -> calculateCreditFee(num);
    case PayPal(var email) -> 0.0;
};

// Good: Pattern matching instead of casting
if (obj instanceof Order(String id, var customer, double total) && total > 1000) {
    log.info("High value order {} for {}", id, customer.name());
}
```

---

## Exception Handling

- Catch the **most specific** exception type. Never catch `Exception`, `Throwable`, or `Error`.
- Never swallow exceptions silently. Catch blocks must log, rethrow, or handle meaningfully.
- Prefer **unchecked exceptions** (`RuntimeException`) for infrastructure and programming errors.
- Use **checked exceptions** only for truly recoverable business conditions (e.g., `IOException` on file operations).
- Always use **try-with-resources** for any `AutoCloseable` (files, streams, JDBC connections).
- For expected business failures, consider modeling with `sealed Result<T, E>` instead of throwing.

```java
// Good: Specific exception + try-with-resources
try (var lines = Files.lines(path)) {
    return lines.map(this::parse).toList();
} catch (IOException e) {
    throw new UncheckedIOException("Failed to read config: " + path, e);
}

// Good: Result type for business failures
public sealed interface OrderResult {
    record Success(Order order) implements OrderResult {}
    record Failure(String reason) implements OrderResult {}
}
```

---

## Collections

- Declare variables using **interface types**: `List`, `Set`, `Map` — never `ArrayList` or `HashMap`.
- Specify initial capacity for `ArrayList` or `HashMap` when the size is known to avoid resizing.
- Use `list.getFirst()` / `list.getLast()` (JDK 21 Sequenced Collections) instead of `list.get(0)` / `list.get(list.size() - 1)`.

---

## Documentation & Annotations

- Document the **contract and invariants**, not the implementation logic.
- Use `@param`, `@return`, `@throws` consistently on public APIs.
- Always use `@Override` on overriding methods.
- Use `@Nullable` / `@NotNull` (JSR-305 or JetBrains) to assist static analysis.
- Use `@Deprecated(since = "x.y", forRemoval = true)` for planned removals — align removal with a major version bump.

---

## Static Analysis Compliance

All generated code must comply with **SonarLint** and **Checkstyle** rules:

- Avoid high Cyclomatic and Cognitive Complexity (keep methods under ~15 lines / 10 branches).
- Manage all resources with try-with-resources (`S2095`).
- Never use `System.out.println` in application code — use a proper logger (`S106`).
- Logging must happen at the **application layer** (services, controllers). Never inside pure domain logic or records.

> If a conflict arises between a style preference and a Sonar rule, the **Sonar rule takes precedence** to keep CI/CD green.

---

## Security

- Never include real secrets, API keys, passwords, or tokens in generated code. Use placeholders: `{{API_KEY}}`, `{{DB_PASSWORD}}`, `user@example.com`.
- Validate all public API inputs immediately using guard clauses or compact constructors.
- Avoid `==` on value-based classes (`Optional`, `LocalDate`, `Duration`) — always use `.equals()`.

---

## Common Smells to Avoid

| Smell | Cure |
| :--- | :--- |
| Primitive obsession | Wrap domain values in Records (`Email`, `Money`, `UserId`) |
| Returning `null` | Return `Optional<T>` or empty collections |
| Deep nesting / arrow code | Guard clauses + pattern matching + stream pipelines |
| Mutable DTOs | Use Records |
| Catching `Exception` | Catch specific subtypes |
| `Optional` as parameter/field | Use `@Nullable` or overloading instead |
| `list.get(0)` on ordered collection | Use `list.getFirst()` (JDK 21+) |
| Side effects in streams | Use `Collectors` or `reduce()` to accumulate |

---

## Build Verification

After any change, verify:

```bash
# Maven
mvn clean install

# Gradle
./gradlew build          # macOS / Linux
gradlew.bat build        # Windows
```

A **green build with failing static analysis is not acceptable** for merge.
