---
description: 'JDK 25 additions to java-core guidelines: unnamed variables, primitive patterns, Stream Gatherers, Structured Concurrency, Scoped Values, and stable preview features'
applyTo: '**/*.java'
---

# Java Core — JDK 25 Additions

> **Prerequisite**: This file **extends** `java-core.instructions.md`. All rules from that file still apply.
> Use this file only when the project build explicitly targets JDK 25:
> - Maven: `<java.version>25</java.version>`
> - Gradle: `sourceCompatibility = JavaVersion.VERSION_25`

> **Conflict Resolution**: Project build config → Sonar/Checkstyle → This file → `java-core.instructions.md`

---

## New Stable Features in JDK 25

| Feature | JEP | Notes |
| :--- | :--- | :--- |
| Unnamed Variables & Patterns (`_`) | JEP 456 | Stable since JDK 22 |
| Stream Gatherers (`Stream.gather()`) | JEP 485 | Stable since JDK 24 |
| Structured Concurrency | JEP 505 | Stable in JDK 25 |
| Scoped Values | JEP 506 | Stable in JDK 25 |
| Primitive Patterns in `switch` | JEP 488 | Stable in JDK 25 |
| Unnamed Classes & Instance Main | JEP 512 | Stable in JDK 25 — scripts/tooling only |
| Flexible Constructor Bodies | JEP 513 | Stable in JDK 25 |

---

## Unnamed Variables (`_`)

Use `_` to explicitly mark unused bindings in patterns, catch blocks, and lambdas.
This signals intent to the reader and eliminates "variable declared but never used" Sonar warnings.

```java
// Good: unused catch parameter
try {
    Integer.parseInt(input);
} catch (NumberFormatException _) {
    return 0;
}

// Good: unused pattern component in record deconstruction
if (result instanceof Result.Ok(var value, _)) {
    return value;
}

// Good: unused lambda parameter
list.forEach(_ -> counter.increment());

// Good: ignoring fields in switch arms
return switch (payment) {
    case CreditCard(var number, _)   -> processCredit(number);
    case PayPal(var email)           -> processDigital(email);
};
```

**Rules:**
- Use `_` only for variables that are **intentionally irrelevant** to the logic.
- Never use `_` as a shortcut to avoid naming something that actually matters.
- For JDK 21 targets, use an explicit name like `ignored` or `unused` instead.

---

## Primitive Patterns in `switch`

Dispatch directly over primitives in `switch` expressions without boxing. This eliminates `Integer`/`Long` wrapper allocations in type-dispatch logic.

```java
// Good: primitive pattern dispatch — no boxing
double fee = switch (statusCode) {
    case 200      -> 0.0;
    case 404      -> FLAT_FEE;
    case int code when code >= 500 -> PENALTY_FEE;
    default       -> DEFAULT_FEE;
};

// Avoid (JDK 21 style): boxing to Integer for switch
Integer boxed = statusCode; // unnecessary allocation
```

**Rules:**
- Use guarded patterns (`when`) for range conditions instead of nested `if` inside switch arms.
- Combine with sealed type patterns when mixing primitive and object dispatch.

---

## Stream Gatherers (`Stream.gather()`)

Use `Stream.gather()` for **stateful or complex intermediate operations** that cannot be expressed with existing stream operations (`map`, `filter`, `flatMap`). This keeps complex transformations inside a declarative pipeline instead of breaking into an imperative loop.

Built-in gatherers available via `java.util.stream.Gatherers`:

| Gatherer | Description |
| :--- | :--- |
| `Gatherers.windowFixed(n)` | Splits stream into fixed-size, non-overlapping windows |
| `Gatherers.windowSliding(n)` | Produces overlapping sliding windows |
| `Gatherers.scan(init, fn)` | Running accumulation (like `reduce` but emits each step) |
| `Gatherers.fold(init, fn)` | Like `reduce` but as an intermediate operation |
| `Gatherers.mapConcurrent(n, fn)` | Concurrent mapping with parallelism bound |

```java
// Good: fixed windows — process items in batches of 3
List<List<Order>> batches = orders.stream()
    .gather(Gatherers.windowFixed(3))
    .toList();

// Good: running total using scan
List<BigDecimal> runningTotals = amounts.stream()
    .gather(Gatherers.scan(BigDecimal.ZERO, BigDecimal::add))
    .toList();

// Good: custom gatherer for "take while increasing"
Gatherer<Integer, ?, Integer> takeWhileIncreasing = Gatherer.ofSequential(
    () -> new int[]{Integer.MIN_VALUE},
    (state, element, downstream) -> {
        if (element <= state[0]) return false;
        state[0] = element;
        return downstream.push(element);
    }
);

List<Integer> ascending = numbers.stream()
    .gather(takeWhileIncreasing)
    .toList();

// Avoid: breaking pipeline into imperative loop for stateful logic
List<List<Order>> batches = new ArrayList<>();
List<Order> current = new ArrayList<>();
for (Order o : orders) {
    current.add(o);
    if (current.size() == 3) {
        batches.add(List.copyOf(current));
        current.clear();
    }
}
```

**Rules:**
- Prefer built-in `Gatherers.*` before writing custom ones.
- Custom gatherers must be **stateless across items** unless state is explicitly encapsulated in the state supplier.
- Do not use `Gatherers.mapConcurrent` inside transactions or when ordering must be preserved.

---

## Structured Concurrency

Use `StructuredTaskScope` to run concurrent subtasks with clear parent-child lifecycle management. The parent scope **always waits for all children** before proceeding, eliminating thread leaks and dangling tasks.

```java
// Good: structured scope — both tasks scoped to the method's lifetime
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

    Subtask<UserProfile> profile  = scope.fork(() -> userService.fetchProfile(userId));
    Subtask<List<Order>> orders   = scope.fork(() -> orderService.fetchOrders(userId));

    scope.join()           // wait for both
         .throwIfFailed(); // propagate first failure as exception

    return new Dashboard(profile.get(), orders.get());
}

// Good: return first successful result, cancel the rest
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<Config>()) {

    scope.fork(() -> loadFromDatabase());
    scope.fork(() -> loadFromRemote());

    scope.join();
    return scope.result(); // first to succeed wins
}

// Avoid: unscoped CompletableFuture — tasks outlive the calling method
CompletableFuture<UserProfile> profile = CompletableFuture.supplyAsync(() -> fetchProfile(id));
CompletableFuture<List<Order>> orders  = CompletableFuture.supplyAsync(() -> fetchOrders(id));
// If fetchOrders throws, fetchProfile keeps running in the background — resource leak
```

**Rules:**
- Always use try-with-resources for `StructuredTaskScope` — it is `AutoCloseable`.
- Use `ShutdownOnFailure` when **all subtasks must succeed** (fan-out/fan-in).
- Use `ShutdownOnSuccess` when you need **the first successful result** (hedged requests, fallbacks).
- Never share mutable state between forked subtasks — pass immutable records or value objects.
- Do not call `scope.fork()` after `scope.join()` — tasks must be registered before joining.

---

## Scoped Values

Use `ScopedValue` to share immutable, bounded context across a call tree without passing parameters through every method. This replaces `ThreadLocal` for request-scoped data in virtual thread environments.

```java
// Declaration: one static constant per piece of context
public static final ScopedValue<RequestContext> REQUEST_CTX = ScopedValue.newInstance();

// Good: bind value for the duration of a specific call tree
ScopedValue.where(REQUEST_CTX, new RequestContext(userId, traceId))
    .run(() -> orderService.placeOrder(cart));

// Good: read from any method in the call tree — no parameter threading needed
public void placeOrder(Cart cart) {
    var ctx = REQUEST_CTX.get(); // always present within the bound scope
    auditLog.record(ctx.userId(), "ORDER_PLACED");
}

// Avoid: ThreadLocal — inheritable by child threads, mutable, leaks context
static final ThreadLocal<RequestContext> REQUEST_CTX = new ThreadLocal<>();
REQUEST_CTX.set(ctx);    // easy to forget cleanup
REQUEST_CTX.remove();    // manual cleanup — skipped if an exception is thrown
```

**Rules:**
- Declare `ScopedValue` constants as `public static final` — one per logical piece of context.
- Never mutate the value inside the scope — it is read-only within the bound call tree.
- Use `ScopedValue.where(...).call(...)` when the operation returns a value; `.run(...)` for void.
- Do not use `ScopedValue` as a general-purpose global — limit to genuinely cross-cutting context (tracing, auth, locale).

---

## Flexible Constructor Bodies

In JDK 25, constructors can execute statements **before** the `super()` or `this()` call, as long as they do not access `this`. This enables validation before delegation without static helper methods.

```java
// Good: validate before delegating to super — no static helper needed
public class PositiveAmount extends Amount {
    public PositiveAmount(BigDecimal value) {
        if (value.signum() <= 0)                         // runs before super()
            throw new IllegalArgumentException("Must be positive: " + value);
        super(value.setScale(2, RoundingMode.HALF_UP));  // delegation after validation
    }
}

// Avoid (JDK 21 workaround): static helper to work around the restriction
public class PositiveAmount extends Amount {
    public PositiveAmount(BigDecimal value) {
        super(validate(value)); // only way to run logic before super() in JDK 21
    }
    private static BigDecimal validate(BigDecimal v) {
        if (v.signum() <= 0) throw new IllegalArgumentException("Must be positive: " + v);
        return v.setScale(2, RoundingMode.HALF_UP);
    }
}
```

**Rules:**
- Statements before `super()`/`this()` must not read or write instance fields (`this` is not yet initialized).
- Use this feature for **validation and transformation of constructor arguments only**.
- Prefer `record` compact constructors for value objects — this feature is mainly useful for class hierarchies.

---

## Naming Additions for JDK 25

Extends the naming table in `java-core.instructions.md`:

| Identifier | Style | Guidance |
| :--- | :--- | :--- |
| Unnamed variable | `_` | Intentionally unused binding in pattern, catch, or lambda |
| `ScopedValue` constant | `UPPER_SNAKE_CASE` | `REQUEST_CTX`, `CURRENT_USER`, `TRACE_ID` |
| `StructuredTaskScope` variable | `lowerCamelCase` | `scope`, named by operation: `fetchScope`, `raceScope` |
| Custom `Gatherer` | `lowerCamelCase` | Named by transformation: `takeWhileIncreasing`, `windowByKey` |

---

## Common Smells Added in JDK 25

| Smell | JDK 25 Cure |
| :--- | :--- |
| Named but unused catch variable | Use `_`: `catch (Exception _)` |
| `ThreadLocal` for request context | Replace with `ScopedValue` |
| `CompletableFuture` fan-out without lifecycle | Replace with `StructuredTaskScope.ShutdownOnFailure` |
| Imperative stateful loop breaking a stream | Replace with `Stream.gather()` + built-in `Gatherers` |
| Static helper before `super()` call | Use flexible constructor body (validate before `super()`) |
| Boxing in primitive `switch` dispatch | Use primitive patterns directly in `switch` |
