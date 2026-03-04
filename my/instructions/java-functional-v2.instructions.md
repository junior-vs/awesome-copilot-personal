---
description: 'Functional-first Java guidelines for JDK 21 LTS: immutability, pure functions, Result types, declarative pipelines, lazy evaluation, and functional domain modeling'
applyTo: '**/*.java'
---

# Java Functional Programming Guidelines (JDK 21 LTS)

> **Scope**: Functional-first (strict) Java instruction. Enforces immutability, pure functions, algebraic data types, and declarative pipelines as the **primary design approach**.
> For naming conventions, collection standards, Javadoc, and Sonar compliance, see `java-core.instructions.md`.

> **JDK Version**: Default to **JDK 21 LTS**. Generate JDK 22+ features (unnamed variables `_`, `Stream.gather()`) **only** when the project build explicitly targets that version and the user opts in.

> **Conflict Resolution**: Project build config → Static analysis rules (Sonar/Checkstyle) → This file → `java-core.instructions.md`

---

## Core Principles

- **Immutability by default**: Treat mutability as the exception, never the rule. Justify every mutable field.
- **Pure functions**: Methods must return the same output for the same input with zero observable side effects.
- **Push side effects to boundaries**: Keep domain logic pure. Perform I/O, logging, and DB operations only at the outermost architectural layers (adapters, controllers, services).
- **Failures as values**: Model expected business failures with sealed `Result<T, E>` types — not exceptions. Use exceptions only for unexpected, unrecoverable infrastructure errors.
- **Logging boundary**: Never log inside pure domain logic or records. Log only at the application/service layer.

---

## Immutability

- Use `record` for all data carriers — they are implicitly immutable.
- Use compact constructors for validation and normalization.
- Use `List.of()`, `Set.of()`, `Map.of()` for fixed collections.
- Use `Stream.toList()` (JDK 16+) — returns unmodifiable list directly.
- Apply defensive copies in compact constructors when accepting mutable inputs.

```java
// Good: immutable value object with validation and normalization
public record PageRequest(int page, int size) {
    public PageRequest {
        if (page < 0)  throw new IllegalArgumentException("page must be >= 0");
        if (size < 1)  throw new IllegalArgumentException("size must be >= 1");
        size = Math.min(size, 100); // normalize upper bound
    }
}

// Good: defensive copy ensures true immutability
public record Order(List<LineItem> items) {
    public Order {
        items = List.copyOf(items);
    }
}
```

---

## Pure Functions

- Compute results in pure methods; perform I/O at the call boundary.
- Never mutate method arguments or write to shared state inside domain logic.
- Use memoization (`ConcurrentHashMap.computeIfAbsent`) for expensive pure computations.

```java
// Good: pure transformation — no I/O, no mutation
public static BigDecimal applyDiscount(BigDecimal price, double rate) {
    return price.multiply(BigDecimal.valueOf(1 - rate))
                .setScale(2, RoundingMode.HALF_UP);
}

// Good: I/O isolated to the application service layer
public record Order(List<LineItem> items, Discount discount) {
    public BigDecimal total() { // pure domain logic
        return items.stream()
            .map(LineItem::subtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .multiply(BigDecimal.ONE.subtract(discount.rate()));
    }
}

class OrderService {
    OrderConfirmation place(Order order) {
        var saved = repository.save(order);            // I/O at the boundary
        eventBus.publish(new OrderPlaced(saved.id())); // I/O at the boundary
        return new OrderConfirmation(saved.id(), saved.total());
    }
}

// Avoid: side effect contaminates domain logic
static BigDecimal applyDiscount(BigDecimal price, double rate) {
    auditLog.record("discount applied"); // ← never do this inside domain
    return price.multiply(BigDecimal.valueOf(1 - rate));
}
```

---

## Algebraic Data Types (Sealed + Records)

Use `sealed` interfaces with `record` subtypes to model closed domain hierarchies. The compiler enforces exhaustive handling in `switch` expressions.

- Never add a `default` branch when switching over a sealed hierarchy — exhaustiveness is the point.
- Use guarded patterns (`when`) for conditional refinement inside switch arms.

```java
// Domain modeling with sealed ADT
public sealed interface PaymentResult permits PaymentResult.Success, PaymentResult.Failure {
    record Success(String transactionId, BigDecimal amount) implements PaymentResult {}
    record Failure(String reason, int errorCode)            implements PaymentResult {}
}

// Exhaustive switch — no default needed
String message(PaymentResult result) {
    return switch (result) {
        case PaymentResult.Success(var id, var amt) -> "Paid: " + amt;
        case PaymentResult.Failure(var reason, var code) -> "Failed [" + code + "]: " + reason;
    };
}

// Avoid: default silently swallows unhandled new variants
return switch (result) {
    case PaymentResult.Success s -> "Paid";
    default -> "Unknown"; // ← compiler won't warn when new subtypes are added
};
```

---

## Result Type for Business Failures

Model expected failures as values using a sealed `Result<T, E>`. This forces callers to handle the failure path at compile time.

```java
// Generic Result ADT
public sealed interface Result<T, E extends Exception> permits Result.Ok, Result.Err {
    record Ok<T, E extends Exception>(T value)   implements Result<T, E> {}
    record Err<T, E extends Exception>(E error)  implements Result<T, E> {}

    default <U> Result<U, E> map(Function<T, U> f) {
        return switch (this) {
            case Ok(var v)  -> new Ok<>(f.apply(v));
            case Err(var e) -> new Err<>(e);
        };
    }

    default <U> Result<U, E> flatMap(Function<T, Result<U, E>> f) {
        return switch (this) {
            case Ok(var v)  -> f.apply(v);
            case Err(var e) -> new Err<>(e);
        };
    }
}

// Monadic chaining — short-circuits on first failure
Result<OrderConfirmation, OrderError> result = validateCart(cart)
    .flatMap(this::checkInventory)
    .flatMap(this::applyDiscount)
    .map(this::toConfirmation);
```

**When to use `Result` vs exceptions:**

| Situation | Model as |
| :--- | :--- |
| Expected business failure (out of stock, validation error, user not found) | `Result<T, E>` or `Optional<T>` |
| Unexpected infrastructure failure (DB unreachable, network timeout, NPE) | Unchecked exception |
| Truly recoverable I/O condition | Checked exception (rare) |

---

## Declarative Pipelines & Streams

- Name `Predicate` and `Function` variables by their behavior so pipelines read like prose.
- Use method references over inline lambdas when the intent is clear.
- Keep pipelines pure: never modify external state inside `.map()`, `.filter()`, or `.peek()`.
- Use `IntStream`, `LongStream`, `DoubleStream` for numeric operations to avoid boxing.

```java
// Good: named, composable predicates and functions
Predicate<User> isActive   = User::isActive;
Predicate<User> isPremium  = u -> u.tier() == Tier.PREMIUM;
Predicate<User> isEligible = isActive.and(isPremium);

Function<Order, Invoice> toInvoice = order ->
    new Invoice(order.id(), order.total(), LocalDate.now());

List<Invoice> invoices = orders.stream()
    .filter(isEligible)
    .map(toInvoice)     // reads: "map each order to an invoice"
    .toList();

// Avoid: inline complex logic duplicated at every call site
orders.stream()
    .filter(o -> o.isActive() && o.tier() == Tier.PREMIUM)
    .map(o -> new Invoice(o.id(), o.total(), LocalDate.now()))
    .toList();
```

---

## Optional — Functional Chaining

- Use `Optional<T>` **only as a return type** to signal a possibly-absent value.
- Chain transformations with `map` and `flatMap` — never call `.get()` without `.isPresent()`.
- Always use `.orElseGet(Supplier)` for alternative computations — never `.orElse(methodCall())`, which evaluates eagerly regardless.

```java
// Good: functional chain, no null checks
Optional<String> city = findUser(id)
    .flatMap(User::address)
    .flatMap(Address::city)
    .map(String::toUpperCase);

// Good: lazy alternative — remoteConfig() called only if local is absent
Optional<Config> config = localConfig()
    .or(() -> remoteConfig());

// Avoid: eager evaluation — remoteConfig() always runs
Optional<Config> config = localConfig()
    .orElse(fetchRemoteConfig()); // executed even when localConfig() is present
```

---

## Lazy Evaluation

Defer expensive computations until actually needed using `Supplier<T>`.

```java
// Good: report only generated when debug is active
Supplier<String> expensiveReport = () -> generateFullReport(data);
if (log.isDebugEnabled()) {
    log.debug("Report: {}", expensiveReport.get());
}

// Avoid: always computed, even when debug is off
log.debug("Report: {}", generateFullReport(data));
```

Use lazy terminal operations when you don't need the full result set:

```java
// Good: stops at first match — does not process remaining elements
Optional<User> admin = users.stream()
    .filter(User::isActive)
    .filter(User::isAdmin)
    .findFirst();

// Avoid: processes all elements even if only one is needed
List<User> activeAdmins = users.stream()
    .filter(User::isActive)
    .filter(User::isAdmin)
    .toList(); // then get(0)
```

---

## Higher-Order Functions & Composition

Compose behavior from small, named, testable functions using `.and()`, `.or()`, and `.andThen()`.

```java
// Good: compose named transformations
Function<String, String> normalize   = String::trim;
Function<String, String> capitalize  = s -> s.isEmpty() ? s :
    Character.toUpperCase(s.charAt(0)) + s.substring(1);
Function<String, String> formatName  = normalize.andThen(capitalize);

// Good: currying and partial application
Function<Double, Function<BigDecimal, BigDecimal>> computeTax =
    rate -> amount -> amount.multiply(BigDecimal.valueOf(1 + rate));

var applyVAT    = computeTax.apply(0.23);
var finalPrice  = applyVAT.apply(new BigDecimal("100.00"));
```

---

## Functional Domain Modeling

Push validation into the type system so **invalid states are unrepresentable**.

```java
// Good: Email is always valid after construction — no external validation needed
public record Email(String value) {
    public Email {
        Objects.requireNonNull(value, "email is required");
        if (!value.contains("@"))
            throw new IllegalArgumentException("Invalid email: " + value);
        value = value.strip().toLowerCase();
    }
}

// Good: accumulative validation — collect all errors before failing
public record ValidationResult<T>(T value, List<String> errors) {
    public boolean isValid() { return errors.isEmpty(); }

    public static <T> ValidationResult<T> combine(
            ValidationResult<T> a, ValidationResult<T> b, BinaryOperator<T> merge) {
        var allErrors = Stream.concat(a.errors.stream(), b.errors.stream()).toList();
        return new ValidationResult<>(merge.apply(a.value, b.value), allErrors);
    }
}
```

---

## Performance Considerations

- **Capturing lambdas** (closures) create a new object per invocation — extract them to `static final` fields in hot paths.
- **Non-capturing lambdas** and method references are cached by the JVM as singletons.
- For **small collections or tight inner loops**, an imperative loop has lower constant overhead than a stream pipeline. Default to streams for clarity; switch to imperative only when JMH profiling shows a measurable regression.

```java
// Avoid in hot paths: new closure object per call
orders.stream().filter(o -> o.total().compareTo(threshold) > 0).toList();

// Good: extracted predicate — created once, reused
private static final Predicate<Order> HIGH_VALUE =
    o -> o.total().compareTo(HIGH_VALUE_THRESHOLD) > 0;

orders.stream().filter(HIGH_VALUE).toList();
```

---

## Testing Pure Functions

Pure functions require no mocks and no setup — they are the easiest code to test.

- Use `@ParameterizedTest` + `@CsvSource` to cover all boundary conditions.
- Use Mockito **only** at infrastructure boundaries (repositories, HTTP clients). Never mock records or value objects.

```java
@ParameterizedTest(name = "rate {1} on {0} → {2}")
@CsvSource({
    "100.00, 0.10, 90.00",
    "100.00, 0.00, 100.00",
    "100.00, 1.00,  0.00"
})
void applyDiscount_ReturnsExpectedPrice(BigDecimal price, double rate, BigDecimal expected) {
    assertThat(Pricing.applyDiscount(price, rate))
        .isEqualByComparingTo(expected); // no mocks needed — it's a pure function
}

// Avoid: mocking value objects defeats the purpose of Records
Order mockOrder = mock(Order.class); // never do this
when(mockOrder.total()).thenReturn(BigDecimal.TEN);
```
