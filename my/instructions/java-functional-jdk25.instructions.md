---
description: 'JDK 25 additions to java-functional guidelines: unnamed patterns, Stream Gatherers for functional pipelines, Scoped Values as functional context, and primitive pattern ADTs'
applyTo: '**/*.java'
---

# Java Functional — JDK 25 Additions

> **Prerequisite**: This file **extends** both `java-functional.instructions.md` and `java-core-jdk25.instructions.md`. All rules from those files still apply.
> Use this file only when the project build explicitly targets JDK 25.

---

## Unnamed Patterns in Sealed ADTs

Use `_` to ignore irrelevant components when deconstructing sealed types. This keeps switch arms focused on the data that actually matters for the current logic.

```java
sealed interface OrderEvent permits OrderEvent.Placed, OrderEvent.Shipped, OrderEvent.Cancelled {
    record Placed(String orderId, Customer customer, BigDecimal total) implements OrderEvent {}
    record Shipped(String orderId, String trackingCode, LocalDate eta)  implements OrderEvent {}
    record Cancelled(String orderId, String reason)                     implements OrderEvent {}
}

// Good: _ discards fields irrelevant to this particular transformation
String summary(OrderEvent event) {
    return switch (event) {
        case Placed(var id, _, var total)    -> "Order %s placed for %s".formatted(id, total);
        case Shipped(var id, var tracking, _) -> "Order %s shipped — track: %s".formatted(id, tracking);
        case Cancelled(var id, _)            -> "Order %s cancelled".formatted(id);
    };
}

// Avoid: binding every field even when unused
String summary(OrderEvent event) {
    return switch (event) {
        case Placed(var id, var customer, var total)        -> "Order %s placed for %s".formatted(id, total);
        // customer is never used — _ is clearer
        case Shipped(var id, var tracking, var eta)         -> "Order %s shipped — track: %s".formatted(id, tracking);
        // eta is never used
        case Cancelled(var id, var reason)                  -> "Order %s cancelled".formatted(id);
        // reason is never used
    };
}
```

**Rules:**
- Use `_` only when the field is **genuinely irrelevant** to the arm's logic.
- Never use `_` to suppress a field you might need later — name it and use it, or restructure.
- Nested unnamed patterns are allowed: `case Placed(var id, Customer(_, var email), _)`.

---

## Stream Gatherers for Functional Pipelines

`Stream.gather()` fills the gap between stateless intermediate operations (`map`, `filter`) and terminal collectors. Use it to keep **stateful transformations declarative** instead of breaking out of the pipeline.

### Functional patterns enabled by Gatherers

```java
// Running accumulation (scan) — emit each intermediate result
List<BigDecimal> runningRevenue = dailySales.stream()
    .gather(Gatherers.scan(BigDecimal.ZERO, BigDecimal::add))
    .toList();

// Fixed-size batching — process items in groups
List<List<Order>> batches = orders.stream()
    .gather(Gatherers.windowFixed(100))
    .toList();

// Sliding window — detect trends over N consecutive elements
List<List<BigDecimal>> windows = prices.stream()
    .gather(Gatherers.windowSliding(5))
    .toList();

// Bounded concurrent mapping — fan-out with parallelism limit
List<EnrichedOrder> enriched = orders.stream()
    .gather(Gatherers.mapConcurrent(8, order -> enrich(order)))
    .toList();
```

### Custom functional Gatherer

When built-in gatherers are not enough, build a custom one as a pure function of state:

```java
// Gatherer: emit elements only while they are strictly increasing
Gatherer<Integer, ?, Integer> takeWhileStrictlyIncreasing = Gatherer.ofSequential(
    () -> new int[]{Integer.MIN_VALUE},       // state: last seen value
    (state, element, downstream) -> {
        if (element <= state[0]) return false; // stop — element is not increasing
        state[0] = element;
        return downstream.push(element);
    }
);

List<Integer> ascending = Stream.of(1, 3, 2, 5, 4, 6)
    .gather(takeWhileStrictlyIncreasing)
    .toList(); // → [1, 3]
```

**Rules:**
- Custom Gatherers must encapsulate **all state** in the state supplier — never capture external mutable state.
- Use `Gatherer.ofSequential` for ordered, stateful operations; `Gatherer.of` for parallelizable ones.
- A Gatherer that returns `false` from its integrator signals early termination — downstream will stop pulling.
- Do not use `Gatherers.mapConcurrent` when element ordering must be preserved or inside a transaction.

---

## Result Type with Unnamed Patterns

Combine `Result<T, E>` with unnamed variables to simplify switch arms that only care about one variant.

```java
// Good: _ discards the error when only the success path matters
String display(Result<Order, OrderError> result) {
    return switch (result) {
        case Result.Ok(var order)  -> "Order #" + order.id();
        case Result.Err(_, _)     -> "Unavailable"; // error details irrelevant here
    };
}

// Good: extract only the error code from a Failure
int errorCode(Result<?, AppException> result) {
    return switch (result) {
        case Result.Ok(_)           -> 0;
        case Result.Err(var ex, _) -> ex.code();
    };
}

// Good: nested unnamed pattern — only the customer email matters
String recipientEmail(OrderEvent event) {
    return switch (event) {
        case OrderEvent.Placed(_, Customer(_, var email), _) -> email;
        default -> "no-reply@example.com";
    };
}
```

---

## Scoped Values as Functional Context

`ScopedValue` is the functional replacement for `ThreadLocal` — it is **immutable within its scope** and **bounded to a specific call tree**, making it safe with virtual threads and referentially transparent within the scope.

```java
// Declaration
public static final ScopedValue<RequestContext> REQUEST_CTX = ScopedValue.newInstance();

// Bind at the application boundary (controller/entry point)
ScopedValue.where(REQUEST_CTX, new RequestContext(userId, traceId, locale))
    .run(() -> orderService.placeOrder(cart));

// Read anywhere in the call tree — pure from the reader's perspective
public OrderConfirmation placeOrder(Cart cart) {
    var ctx = REQUEST_CTX.get();
    var order = buildOrder(cart, ctx.userId());
    auditLog.record(ctx.traceId(), "ORDER_PLACED");
    return confirm(order);
}

// Good: rebind for a narrower scope — does not mutate the parent scope
ScopedValue.where(REQUEST_CTX, ctx.withLocale(Locale.ENGLISH))
    .call(() -> notificationService.send(orderId));
```

**Functional rules for Scoped Values:**
- Treat `ScopedValue` as **read-only within the bound call tree** — never design code that expects the value to change during execution.
- Use `ScopedValue.where(...).call(...)` when the operation must return a value (referentially transparent).
- Nest scopes with `.where(A, x).where(B, y).run(...)` to bind multiple values atomically.
- Do not use `ScopedValue` to pass mutable objects — only immutable records or value objects.

---

## Primitive Patterns in Functional ADTs

Combine primitive patterns with sealed types to dispatch over mixed primitive/object hierarchies without boxing.

```java
// Sealed type with primitive record components
sealed interface Metric permits Metric.Counter, Metric.Gauge, Metric.Histogram {
    record Counter(long count)              implements Metric {}
    record Gauge(double value)              implements Metric {}
    record Histogram(int[] buckets, long n) implements Metric {}
}

// Good: primitive patterns dispatch without boxing
String format(Metric metric) {
    return switch (metric) {
        case Metric.Counter(long c)                          -> "count=" + c;
        case Metric.Gauge(double v)   when v < 0            -> "gauge=NEGATIVE";
        case Metric.Gauge(double v)                          -> "gauge=" + v;
        case Metric.Histogram(_, long n) when n == 0        -> "histogram=empty";
        case Metric.Histogram(var b, long n)                 -> "histogram[n=%d]".formatted(n);
    };
}
```

---

## Validation: Accumulative Style with Gatherers

Combine accumulative validation with `Stream.gather()` for pipeline-based multi-field validation that collects all errors before failing.

```java
// Gatherer that collects all ValidationErrors without short-circuiting
Gatherer<ValidationResult<?>, List<String>, ValidationResult<?>> collectErrors =
    Gatherer.ofSequential(
        ArrayList::new,
        (errors, result, downstream) -> {
            errors.addAll(result.errors());
            return downstream.push(result);
        },
        (errors, downstream) -> {
            if (!errors.isEmpty())
                downstream.push(ValidationResult.failed(errors));
        }
    );

// Usage: validate all fields, collect all errors at once
List<ValidationResult<?>> results = Stream.of(
        validateName(cmd.name()),
        validateEmail(cmd.email()),
        validateAge(cmd.age())
    )
    .gather(collectErrors)
    .toList();
```

---

## Updated Smells Table for Functional JDK 25

Extends the smells table in `java-functional.instructions.md`:

| Smell | JDK 25 Functional Cure |
| :--- | :--- |
| Naming every bound variable in switch arms | Use `_` for irrelevant record components |
| Stateful loop breaking a functional pipeline | Use `Stream.gather()` with `Gatherers.windowFixed` / `scan` / custom Gatherer |
| `ThreadLocal` for request context in domain logic | Replace with `ScopedValue` — immutable, scope-bound, virtual-thread safe |
| Boxing in numeric ADT dispatch | Use primitive patterns directly in sealed `switch` |
| Static helper method before `super()` in value class | Use flexible constructor body for pre-`super()` validation |
| Accumulating validation errors imperatively | Use a custom `Gatherer` to collect errors inside a stream pipeline |
