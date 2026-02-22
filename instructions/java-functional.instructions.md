---
description: 'Guidelines for generating and reviewing Java code targeting JDK 21 (LTS) and JDK 25, enforcing functional programming principles, immutability, and modern concurrency'
applyTo: '**/*.java'
name: 'Java Functional Programming Guidelines (JDK 21 & 25)'
tools: ['search/codebase', 'edit/editFiles', 'search', 'web/fetch']
---

These instructions guide GitHub Copilot in generating clean, maintainable, and modern Java code targeting both **JDK 21 (LTS)** and **JDK 25 (LTS)**. They enforce strict functional and reactive programming principles.

Recommendations are grounded in industry-standard literature:
- *Effective Java* (Joshua Bloch)
- *Java Concurrency in Practice* (Brian Goetz)
- *Modern Java in Action* (Raoul-Gabriel Urma)
- *Functional and Reactive Domain Modeling* (Debasish Ghosh)
- *Functional Programming in Java* (Pierre-Yves Saumont)
- *Reactive Systems in Java* (Clement Escoffier & Ken Finnigan)

> **Scope**: This is the **functional-first (purista)** Java instruction. It enforces strict functional programming principles — immutability, pure functions, algebraic data types, and declarative pipelines — as the **primary design approach**. For a more **general/pragmatic** Java instruction covering mixed paradigms (OOP + functional), see `java-improved.instructions.md`.

## General Instructions

- **Determine Target Version**: Always adapt code generation to the project's target JDK (21 or 25). If the context does not explicitly indicate JDK 25, default to JDK 21 compatibility.
- **Default to Immutability**: Treat immutability as the absolute default (*Effective Java*, Item 17). Mutability must be strictly isolated and justified.
- **Enforce Pure Functions**: Design methods to produce the same output for the same input with zero observable side effects.
- **Push Side Effects to Boundaries**: Keep the domain core pure. Perform I/O, logging, and database operations only at the outermost architectural layers (Adapters/Controllers).
- **Logging Boundary**: Logging must happen at the **application layer** (services, controllers, adapters), never inside pure domain logic. A dedicated logging instruction will cover this topic in depth.
- **Model Failures as Values**: Use sealed interface result types (e.g., `Result<T, E>`) for expected business failures instead of throwing exceptions across domain boundaries.
- **Assume Virtual Threads Execution**: Write thread-safe code by confining state to the execution thread. Do not use `ThreadLocal` or shared mutable state; rely on immutability to prevent data races (*Java Concurrency in Practice*).
- **Adhere to Static Analysis Rules**: Always generate code compliant with standard SonarQube rules (e.g., prevent resource leaks `S2095`). Never generate code smells or deprecated patterns.

## JDK Features Baseline

Leverage the following modern Java features by default to support functional design.

| Feature | Min JDK | Primary Functional Use Case |
|---|---|---|
| **Records** | 16 (21+) | Implement immutable value objects and Data Transfer Objects without boilerplate. |
| **Sealed Classes** | 17 (21+) | Model closed-hierarchy domain states and Algebraic Data Types (Sum Types). |
| **Record Patterns** | 21 | Destructure records directly in `switch` and `instanceof` (e.g., `case Point(int x, int y)`). |
| **Pattern Matching for switch** | 21 | Perform exhaustive structural dispatch without explicit casting or `default` fallbacks for sealed types. |
| **Virtual Threads** | 21 | Execute blocking I/O concurrently without complex reactive plumbing (`Mono`/`Flux`). |
| **Sequenced Collections** | 21 | Traverse collections with predictable encounter orders (`getFirst()`, `getLast()`). |
| **Unnamed Variables (`_`)** | 22 (stable) | Ignore unused variables in lambdas, exceptions, or pattern matching. **Not available in JDK 21** (Preview via JEP 443). Stable since JDK 22 (JEP 456). |
| **Stream Gatherers** | 24 (stable) | Create custom intermediate stream operations (`Stream.gather()`). Preview in JDK 22–23 (JEP 461/473), **stable since JDK 24** (JEP 485). |
| **Structured Concurrency** | 25 (stable) | Orchestrate multiple concurrent subtasks reliably using `StructuredTaskScope`. Preview in JDK 21 (JEP 453), **stable in JDK 25** (JEP 505). |
| **Scoped Values** | 25 (stable) | Propagate immutable, read-only context across threads. **Preview in JDK 21** (JEP 446), **stable in JDK 25** (JEP 506). |
| **Primitive Patterns** | 25 | Dispatch over primitives in `switch` statements without boxing. |

## Version-Specific Conditional Guidance

Apply these specific rules based on the detected or requested JDK version.

### For JDK 21 (LTS) Projects
- **Concurrency**: Use `CompletableFuture` combined with an `Executor` backed by Virtual Threads (`Executors.newVirtualThreadPerTaskExecutor()`) for parallel I/O tasks. `StructuredTaskScope` and `ScopedValue` are available as **Preview** (JEP 453/446) — do not use in production.
- **Streams**: Rely on standard `Stream` API operations (`map`, `filter`, `reduce`, `collect`). `Stream.gather()` is **not available** in JDK 21. Extract complex transformations into pure functions.
- **Variables**: **Unnamed Variables (`_`) are not available in JDK 21** (Preview only in JDK 22+). Name unused variables explicitly (e.g., `ignored` or `ex`).

### For JDK 25 Projects
- **Concurrency**: Prefer `StructuredTaskScope` (JEP 505, stable) over `CompletableFuture` for orchestrating multiple concurrent I/O calls to guarantee thread lifecycle management. Use `ScopedValue` (JEP 506, stable) over `ThreadLocal`.
- **Streams**: Use `Stream.gather()` (JEP 485, stable since JDK 24) for complex, stateful intermediate stream operations. Gatherers enable custom transformations (windowing, scanning, folding) without breaking the declarative pipeline.
- **Variables**: Use the Unnamed Variable `_` (JEP 456, stable since JDK 22) for ignored exceptions, lambda parameters, or pattern variables.

### Universal Anti-Patterns (Avoid in both JDK 21 and 25)
- **Avoid Thread Pooling for I/O**: Do not use `Executors.newFixedThreadPool()` for I/O tasks. Always use Virtual Threads.
- **String Handling**: Use `String.formatted()` or Text Blocks (`"""`) for string composition. These are stable since JDK 15+.

---

## Core Functional Principles

### 1. Immutability First

Immutability eliminates an entire class of bugs caused by shared mutable state (*Functional Thinking*, ch. 3).

- Declare all fields and local variables `final` by default.
- Use `List.of()`, `Set.of()`, `Map.of()` for fixed collections.
- Use `Stream.toList()` — it returns an unmodifiable list directly.
- Apply **defensive copies** when accepting or returning mutable types.
- Prefer **Records** for value objects — they are implicitly immutable.

#### Good Example - Immutable Record with Validation
```java
// Immutable value object with normalized and validated input
record PageRequest(int page, int size) {
    PageRequest {
        if (page < 0) throw new IllegalArgumentException("page must be >= 0");
        if (size < 1) throw new IllegalArgumentException("size must be >= 1");
        size = Math.min(size, 100); // normalize
    }
}
```

#### Bad Example - Mutable Class
```java
// Exposes state to uncontrolled modification
class PageRequest {
    public int page;
    public int size;
}
```

### 2. Pure Functions

A pure function has no side effects and returns the same value for the same arguments (*Becoming Functional*, ch. 2; *Functional Programming in Java*, ch. 1).

- Separate computation from I/O: compute results in pure methods, perform I/O at the call boundary.
- Avoid mutating method arguments.
- Avoid reading from or writing to shared mutable state inside domain logic.

#### Good Example - Pure Function
```java
// Pure transformation; no I/O, no mutation
static BigDecimal applyDiscount(BigDecimal price, double rate) {
    return price.multiply(BigDecimal.valueOf(1 - rate))
                .setScale(2, RoundingMode.HALF_UP);
}
```

#### Bad Example - Impure Function with Side Effects
```java
static BigDecimal applyDiscount(BigDecimal price, double rate) {
    auditLog.record("discount applied"); // Side effect contaminates domain logic
    return price.multiply(BigDecimal.valueOf(1 - rate));
}
```

Additional guidelines for pure functions:

- **Use Memoization** for expensive pure computations to preserve performance while maintaining referential transparency.
- **Avoid hidden state**: Do not read from or write to fields outside the function scope.

#### Good Example - Memoized Pure Function
```java
public class TaxCalculator {
    private final Map<Double, BigDecimal> cache = new ConcurrentHashMap<>();

    // Pure logic wrapped in a memoizer
    public BigDecimal calculate(double rate) {
        return cache.computeIfAbsent(rate, r ->
            heavyComputation(r));
    }
}
```

### 3. Algebraic Data Types (Sealed Classes and Records)

Model domain variants as **sum types** using sealed interfaces paired with records (*Functional and Reactive Domain Modeling*, ch. 2).

- Use `sealed interface` to define a closed set of domain states.
- Use Pattern Matching for `switch` for exhaustive structural dispatch.
- **For JDK 25:** Use primitive patterns to avoid boxing and unnamed variables (`_`) for ignored bindings.
- **Use Exhaustive Switch**: Never use a `default` clause when switching over a `sealed` hierarchy.
- **JDK 25 Specific**: Use the Unnamed Variable `_` for ignored pattern components.

#### Good Example - Exhaustive Pattern Matching
```java
sealed interface OrderStatus permits Pending, Shipped, Delivered {}

String message(OrderStatus status) {
    return switch (status) {
        case Pending p -> "Wait...";
        case Shipped s -> "On the way";
        case Delivered d -> "Arrived";
        // No default: Compiler enforces exhaustiveness
    };
}
```

#### Good Example - Exhaustive Switch (JDK 21 & JDK 25)
```java
sealed interface PaymentResult permits PaymentResult.Success, PaymentResult.Failure {
    record Success(String transactionId, BigDecimal amount) implements PaymentResult {}
    record Failure(String reason, int errorCode)            implements PaymentResult {}
}

String message(PaymentResult result) {
    return switch (result) {
        // JDK 21+ Record Pattern matching
        case PaymentResult.Success(String id, BigDecimal amt) -> "Paid: " + amt;

        // JDK 25+ Unnamed variable (_) ignores the 'reason' field
        case PaymentResult.Failure(_, int code) -> "Failed with code: " + code;
    };
}
```

#### Bad Example - Open Hierarchy with Default Clause
```java
String message(PaymentResult result) {
    return switch (result) {
        case PaymentResult.Success s -> "Paid";
        default -> "Unknown"; // Silent mismatch when new variants are added
    };
}
```

### 3a. Sealed Interfaces with Generic Bounds

Combine sealed interfaces with generic type parameters to create **type-safe, reusable algebraic data types**. Use bounded generics (`<T extends ...>`) to constrain the type space at compile time.

#### Good Example - Generic Sealed Result with Bounds
```java
// Generic Result type with bounded error type
sealed interface Result<T, E extends Exception> permits Result.Ok, Result.Err {
    record Ok<T, E extends Exception>(T value) implements Result<T, E> {}
    record Err<T, E extends Exception>(E error) implements Result<T, E> {}

    // Functor: transform the success value
    default <U> Result<U, E> map(Function<T, U> f) {
        return switch (this) {
            case Ok(var v)  -> new Ok<>(f.apply(v));
            case Err(var e) -> new Err<>(e);
        };
    }

    // Monad: chain operations that may also fail
    default <U> Result<U, E> flatMap(Function<T, Result<U, E>> f) {
        return switch (this) {
            case Ok(var v)  -> f.apply(v);
            case Err(var e) -> new Err<>(e);
        };
    }
}
```

#### Good Example - Bounded Sealed Validator
```java
// Sealed hierarchy constrained to Comparable types
sealed interface Validator<T extends Comparable<T>> permits RangeValidator, RegexValidator {
    Result<T, ValidationException> validate(T input);
}

record RangeValidator<T extends Comparable<T>>(T min, T max) implements Validator<T> {
    public Result<T, ValidationException> validate(T input) {
        if (input.compareTo(min) < 0 || input.compareTo(max) > 0)
            return new Result.Err<>(new ValidationException("Out of range: " + input));
        return new Result.Ok<>(input);
    }
}
```

### 4. Declarative Pipelines with Streams

Replace imperative loops with declarative `Stream` pipelines.

- Use method references for clarity.
- Avoid stateful lambdas.
- **For JDK 25:** Use `Stream.gather()` for complex, stateful intermediate operations instead of breaking the pipeline into an imperative loop.

#### Good Example - Declarative Pipeline
```java
Predicate<Order> isEligible = order -> order.total().compareTo(MIN_AMOUNT) >= 0;

List<Invoice> invoices = orders.stream()
    .filter(isEligible)
    .map(Order::toInvoice)
    .toList();
```

#### Bad Example - Imperative Loop with Shared Mutable State
```java
List<Invoice> invoices = new ArrayList<>();
for (Order o : orders) {
    if (o.total().compareTo(MIN_AMOUNT) >= 0) {
        invoices.add(o.toInvoice());
    }
}
```

Additional guidelines for Stream reductions:

- **Use Monoids** for `Stream.reduce()` operations. A monoid must have an **Identity** element and follow **Associativity**.
- **Prefer Stream Gatherers (JDK 25)** for complex windowing or stateful transformations to keep the pipeline declarative.

#### Good Example - Monoidal Reduction
```java
// Integer addition is a monoid: Identity 0, Associative (a+b)+c == a+(b+c)
int sum = numbers.stream().reduce(0, Integer::sum);
```

### 5. Optional for Absent Values

Use `Optional<T>` to make absent values explicit. Chain transformations functionally (*Modern Java in Action*, ch. 11).

#### Good Example - Functional Optional Chain
```java
Optional<String> displayName = findById(id)
    .filter(User::isActive)
    .map(User::name);
```

#### Bad Example - Imperative Unwrapping
```java
Optional<User> opt = findById(id);
if (opt.isPresent()) {
    return opt.get().name(); // Defeats the purpose of Optional
}
return null;
```

### 6. Higher-Order Functions and Function Composition

Pass behavior as data using functional interfaces (`Function`, `Predicate`, `Supplier`). Compose them to build complex pipelines from simple, testable, and named steps (*Becoming Functional*, ch. 5; *Functional Programming in Java*, ch. 2).

- Name predicates and functions by their behavior.
- Use `.and()`, `.or()`, and `.andThen()` to compose logic instead of writing complex inline lambdas.

#### Good Example - Function Composition
```java
// Reusable, composable functions and predicates
Predicate<User> isActive   = User::isActive;
Predicate<User> isPremium  = u -> u.tier() == Tier.PREMIUM;
Predicate<User> isEligible = isActive.and(isPremium);

Function<String, String> normalize  = String::trim;
Function<String, String> upperFirst = s -> s.isEmpty() ? s :
    Character.toUpperCase(s.charAt(0)) + s.substring(1);
Function<String, String> formatName = normalize.andThen(upperFirst);

List<String> formattedNames = users.stream()
    .filter(isEligible)
    .map(u -> formatName.apply(u.name()))
    .toList();
```

#### Bad Example - Inline Complex Logic
```java
// Inline logic duplicated across call sites, hard to read and test individually
List<String> formattedNames = users.stream()
    .filter(u -> u.isActive() && u.tier() == Tier.PREMIUM)
    .map(u -> {
        String s = u.name().trim();
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1);
    })
    .toList();
```

Additional composition techniques:

- **Use Currying** to transform a function with multiple arguments into a chain of single-argument functions.
- **Use Partial Application** to create specialized functions from general ones.

#### Good Example - Currying and Partial Application
```java
// Curried function: (Rate) -> (Amount) -> Total
Function<Double, Function<BigDecimal, BigDecimal>> computeTax =
    rate -> amount -> amount.multiply(BigDecimal.valueOf(1 + rate));

// Partial application
var applyVAT = computeTax.apply(0.23);
BigDecimal finalPrice = applyVAT.apply(new BigDecimal("100.00"));
```


### 7. Lazy Evaluation

Defer computation until the value is actually needed. While Streams are lazy by default, apply the same principle to scalar values and control flow using `Supplier<T>` (*Functional Programming in Java*, ch. 9).

- Use `Supplier<T>` to wrap expensive operations.
- Always use `.orElseGet(Supplier)` or `.or(Supplier)` on `Optional` for alternative computations. Never use `.orElse(methodCall())`.

#### Good Example - Lazy Computation with Supplier
```java
// Supplier defers expensive computation; it is only executed if debug mode is active
Supplier<String> expensiveReport = () -> generateFullReport(data);

if (log.isDebugEnabled()) {
    log.debug("Report: {}", expensiveReport.get());
}

// Lazy alternative computation with Optional
Optional<Config> config = localConfig()
    .or(() -> remoteConfig())   // remoteConfig() called only if localConfig() is empty
    .or(() -> defaultConfig());
```

#### Bad Example - Eager Evaluation
```java
// Report is generated regardless of the debug mode flag
log.debug("Report: {}", generateFullReport(data));

// fetchRemoteConfig() is executed IMMEDIATELY, even if localConfig() returns a value
Config config = localConfig()
    .orElse(fetchRemoteConfig());
```

### 8. Recursion and Tail-Call Considerations

Java (as of JDK 25) does **not** support tail-call optimization (TCO) at the JVM level. Recursive algorithms risk `StackOverflowError` for deep call stacks. Prefer iterative alternatives or trampoline patterns for production code.

- **Avoid deep recursion**: Convert recursive algorithms to iterative using `Stream.iterate()`, `reduce()`, or explicit stacks.
- **Trampoline pattern**: For algorithms that are naturally recursive, use a trampoline to convert tail recursion into iteration.
- **No standard `@TailCall`**: Java has no standard `@TailCall` annotation (unlike Scala's `@tailrec`). Some libraries (e.g., Vavr) provide trampoline utilities, but pure Java requires manual conversion.

#### Good Example - Iterative Alternative to Recursion
```java
// Avoid: Deep recursion risks StackOverflowError
long factorialRecursive(long n) {
    if (n <= 1) return 1;
    return n * factorialRecursive(n - 1); // No TCO in JVM
}

// Good: Stream-based iterative approach
long factorial(long n) {
    return LongStream.rangeClosed(1, n).reduce(1, Math::multiplyExact);
}
```

#### Good Example - Trampoline Pattern for Safe Recursion
```java
// Trampoline converts tail recursion into heap-based iteration
sealed interface Trampoline<T> {
    record Done<T>(T value) implements Trampoline<T> {}
    record More<T>(Supplier<Trampoline<T>> next) implements Trampoline<T> {}

    default T evaluate() {
        Trampoline<T> current = this;
        while (current instanceof More<T>(var next)) {
            current = next.get();
        }
        return ((Done<T>) current).value;
    }
}

// Tail-recursive factorial using Trampoline
Trampoline<Long> factorialTrampoline(long n, long acc) {
    if (n <= 1) return new Trampoline.Done<>(acc);
    return new Trampoline.More<>(() -> factorialTrampoline(n - 1, n * acc));
}

// Usage: safe for arbitrarily large n
long result = factorialTrampoline(10_000, 1).evaluate();
```

#### Bad Example - Unbounded Recursion
```java
// StackOverflowError for large inputs — no JVM tail-call optimization
long fibonacci(long n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2); // Exponential time + stack overflow
}
```


### 9. Validation Styles
Choose the correct validation strategy based on the business requirement.

- **Use Monadic Validation** (`flatMap`) for short-circuiting logic (stop at the first error).
- **Use Applicative Validation** (accumulative) to collect all errors from multiple fields simultaneously.

#### Good Example - Accumulative Validation (JDK 21+)
```java
record ValidationResult<T>(T value, List<String> errors) {
    static <T> ValidationResult<T> combine(ValidationResult<T> a, ValidationResult<T> b, BinaryOperator<T> combiner) {
        var allErrors = Stream.concat(a.errors.stream(), b.errors.stream()).toList();
        return new ValidationResult<>(combiner.apply(a.value, b.value), allErrors);
    }
}
```

---

## Reactive and Concurrent Design

### 1. Virtual Threads (JDK 21+)

Use virtual threads for I/O-bound concurrent tasks. They provide reactive-like throughput without the complexity of `Mono` or `Flux` (*Reactive Systems in Java*, ch. 3).

- Virtual threads are lightweight — do **not** pool them.
- Prefer `Executors.newVirtualThreadPerTaskExecutor()`.

#### Good Example - Virtual Threads Execution
```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Response>> futures = urls.stream()
        .map(url -> executor.submit(() -> fetch(url)))
        .toList();

    // Process futures...
}
```

#### Bad Example - Thread Pooling for I/O
```java
// Platform thread pools block OS threads for I/O-bound work
ExecutorService pool = Executors.newFixedThreadPool(200);
```

### 2. Concurrent Fan-out Orchestration

When splitting a task into multiple concurrent sub-tasks, the approach strictly depends on the target JDK version.

#### Good Example - JDK 25 (StructuredTaskScope)
Use `StructuredTaskScope` (JEP 505) to ensure child threads do not outlive their parent scope, making error propagation explicit and preventing resource leaks.
```java
record UserPage(User user, List<Order> orders) {}

UserPage fetchUserPage(long userId) throws InterruptedException {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<User>        userTask   = scope.fork(() -> userService.findById(userId));
        Subtask<List<Order>> ordersTask = scope.fork(() -> orderService.findByUser(userId));

        scope.join().throwIfFailed(); // Cancels sibling tasks immediately on failure

        return new UserPage(userTask.get(), ordersTask.get());
    }
}
```

#### Good Example - JDK 21 (CompletableFuture + Virtual Threads)
For JDK 21, since `StructuredTaskScope` is in preview, combine `CompletableFuture` with a Virtual Thread Executor.
```java
record UserPage(User user, List<Order> orders) {}

UserPage fetchUserPage(long userId) {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        CompletableFuture<User> userFuture =
            CompletableFuture.supplyAsync(() -> userService.findById(userId), executor);

        CompletableFuture<List<Order>> ordersFuture =
            CompletableFuture.supplyAsync(() -> orderService.findByUser(userId), executor);

        return userFuture.thenCombine(ordersFuture, UserPage::new).join();
    }
}
```

#### Bad Example - Unstructured Fan-out (Avoid in all versions)
```java
// If userTask throws an exception, orderTask continues running in the background (resource leak)
CompletableFuture<User>        userTask  = CompletableFuture.supplyAsync(() -> fetchUser());
CompletableFuture<List<Order>> orderTask = CompletableFuture.supplyAsync(() -> fetchOrders());
```

### 3. Context Propagation

Propagating implicit context (like a security principal or request ID) requires different strategies based on the JDK version (*Functional and Reactive Domain Modeling*, ch. 6).

#### Good Example - JDK 25 (Scoped Values)
Use `ScopedValue` (JEP 506) to propagate immutable, read-only context across virtual threads without the mutability and leak risks of `ThreadLocal`.
```java
static final ScopedValue<Principal> PRINCIPAL = ScopedValue.newInstance();

void handleRequest(HttpRequest req) {
    ScopedValue.where(PRINCIPAL, authenticate(req))
               .run(() -> processRequest(req)); // PRINCIPAL is securely bound for this scope
}

void processRequest(HttpRequest req) {
    Principal p = PRINCIPAL.get(); // Immutable access
}
```

#### Good Example - JDK 21 (Explicit Parameter Passing)
Because `ScopedValue` is in preview in JDK 21, and `ThreadLocal` is dangerous with virtual threads, strictly prefer explicit parameter passing (the purely functional way).
```java
void handleRequest(HttpRequest req) {
    Principal principal = authenticate(req);
    processRequest(req, principal); // Explicit passing
}
```

#### Bad Example - ThreadLocal with Virtual Threads
```java
static final ThreadLocal<Principal> PRINCIPAL = new ThreadLocal<>();
// Mutable, easy to forget .remove(), leaks memory, and performs poorly with virtual threads
PRINCIPAL.set(principal);
```


### 4. Structured Concurrency (JDK 25)
Use `StructuredTaskScope` to manage subtask lifecycles.

- **Use `ShutdownOnFailure`** to ensure that if one subtask fails, siblings are cancelled immediately.
- **Avoid Orphan Threads**: Always use try-with-resources with `StructuredTaskScope`.

### 5. Scoped Values (JDK 25)
Use `ScopedValue` to propagate immutable context across threads.

- **Use over `ThreadLocal`**: Scoped values are more memory-efficient and safer for Virtual Threads.

#### Good Example - ScopedValue Context
```java
static final ScopedValue<TenantId> TENANT = ScopedValue.newInstance();

void handle(Request req) {
    ScopedValue.where(TENANT, extractId(req))
               .run(() -> process(req));
}
```

---

## Functor and Monad Patterns

In functional programming, **Functors** and **Monads** are design patterns for composing operations over wrapped values. Java implements these patterns through `Optional`, `Stream`, `CompletableFuture`, and custom sealed types like `Result<T, E>` (*Functional Programming in Java*, ch. 4–5).

### Functor: The `map` Operation

A **Functor** is any type that supports a `map` operation — transforming the inner value without changing the wrapper structure.

**Functor Laws** (these must hold for any correct `map` implementation):
1. **Identity**: `functor.map(x -> x)` must equal `functor` — mapping identity changes nothing.
2. **Composition**: `functor.map(f).map(g)` must equal `functor.map(f.andThen(g))` — chaining two maps equals one composed map.

#### Good Example - Functor with Optional and Stream
```java
// Optional as Functor: map transforms the inner value
Optional<String> name = findUser(id).map(User::name);

// Stream as Functor: map transforms each element
List<String> emails = users.stream().map(User::email).toList();

// Identity law verification
Optional<User> user = Optional.of(new User("Alice"));
assert user.map(Function.identity()).equals(user); // Identity law holds

// Composition law verification
Function<String, String> trim = String::trim;
Function<String, String> upper = String::toUpperCase;

Optional<String> viaChain    = user.map(User::name).map(trim).map(upper);
Optional<String> viaComposed = user.map(User::name).map(trim.andThen(upper));
assert viaChain.equals(viaComposed); // Composition law holds
```

### Monad: The `flatMap` Operation

A **Monad** extends Functor with `flatMap` (also called `bind`). It allows sequencing of operations that each produce a wrapped value, avoiding nested wrappers (`Optional<Optional<T>>`).

**Monad Laws**:
1. **Left Identity**: `Optional.of(a).flatMap(f)` must equal `f.apply(a)`.
2. **Right Identity**: `m.flatMap(Optional::of)` must equal `m`.
3. **Associativity**: `m.flatMap(f).flatMap(g)` must equal `m.flatMap(x -> f.apply(x).flatMap(g))`.

#### Good Example - Chaining with flatMap (Optional)
```java
// Each step may return empty — flatMap chains them without nesting
Optional<String> city = findUser(id)
    .flatMap(User::address)      // User → Optional<Address>
    .flatMap(Address::city)      // Address → Optional<String>
    .map(String::toUpperCase);   // String → String (Functor map)

// Without flatMap: nested Optionals — unusable
// Optional<Optional<Optional<String>>> nested = findUser(id).map(User::address)...
```

#### Good Example - Chaining with flatMap (Stream)
```java
// flatMap flattens nested collections into a single stream
List<String> allTags = articles.stream()
    .flatMap(article -> article.tags().stream()) // Stream<List<Tag>> → Stream<Tag>
    .map(Tag::name)
    .distinct()
    .toList();
```

#### Good Example - Chaining with flatMap (Result<T, E>)
```java
// Monadic chaining: each step may fail, short-circuiting on first error
Result<OrderConfirmation, OrderError> result = validateCart(cart)
    .flatMap(this::checkInventory)    // Result<Cart, OrderError>
    .flatMap(this::applyDiscount)     // Result<Order, OrderError>
    .map(this::toConfirmation);       // Result<OrderConfirmation, OrderError>

// Without flatMap: deeply nested switch statements
// switch (validateCart(cart)) { case Ok(var c) -> switch (checkInventory(c)) { ... } }
```

#### Bad Example - Imperative Null Checks Instead of flatMap
```java
// Deeply nested null checks — error-prone and non-compositional
User user = findUser(id);
if (user != null) {
    Address addr = user.getAddress();
    if (addr != null) {
        String city = addr.getCity();
        if (city != null) {
            return city.toUpperCase();
        }
    }
}
return null;
```

---

## Functional Domain Modeling

Model your domain with types, not just procedures (*Functional and Reactive Domain Modeling*, ch. 2). Push validation into the type system so invalid states are unrepresentable.

- Validate domain invariants inside record compact constructors.
- Never return `null` for expected absent or invalid values. Use `Optional<T>` or a sealed `Result<T, E>`.
- Isolate pure domain logic (calculations, rules) from infrastructure side effects (I/O, database, messaging).

#### Good Example - Type-safe Domain Invariants
```java
// Validation in the compact constructor; Email is always valid after construction
record Email(String value) {
    Email {
        if (value == null || !value.contains("@")) {
            throw new IllegalArgumentException("Invalid email: " + value);
        }
        value = value.strip().toLowerCase();
    }
}
```

#### Bad Example - Anemic and Unsafe Domain Model
```java
// Allows instantiation of invalid state; relies on external validation
class Email {
    public String value;
}
```

#### Good Example - Separating Pure Logic from I/O
```java
// Pure domain logic: No I/O, entirely testable in isolation
record Order(List<LineItem> items, Discount discount) {
    BigDecimal total() {
        return items.stream()
            .map(LineItem::subtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .multiply(BigDecimal.ONE.subtract(discount.rate()));
    }
}

// Application service: I/O happens at the edge
class OrderService {
    OrderConfirmation place(Order order) {
        var saved = repository.save(order);            // I/O
        eventBus.publish(new OrderPlaced(saved.id())); // I/O
        return new OrderConfirmation(saved.id(), saved.total());
    }
}
```

---

## Code Standards

Follow the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) as the baseline.
The rules below extend it with functional-first conventions specific to this instruction file.


### 1. Naming Conventions

Names are the primary communication channel between the author and the reader.
In a functional codebase, names must also signal **intent and purity**.

| Identifier | Style | Guidance |
|---|---|---|
| Class / Interface / Record / Enum | `UpperCamelCase` | Nouns: `OrderService`, `PaymentResult`, `Email` |
| Sealed error types | `UpperCamelCase` | Nouns describing the failure: `OutOfStock`, `InvalidCart` |
| Method | `lowerCamelCase` | Verbs: `calculateTotal`, `applyDiscount`, `toInvoice` |
| Record component | `lowerCamelCase` | Nouns without `get` prefix: `id`, `createdAt`, `totalAmount` |
| `Function` / `Predicate` variable | `lowerCamelCase` | Named by behavior: `isEligible`, `toInvoice`, `formatName` |
| Boolean method / predicate | `lowerCamelCase` | Phrased as a question: `isActive()`, `hasDiscount()`, `isEmpty()` |
| Constant (`static final`) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT`, `MIN_ORDER_AMOUNT` |
| Package | `lowercase` | `com.example.orders`, `com.example.payment` |
| Source file | `UpperCamelCase.java` | `OrderRepository.java`, `PaymentResult.java` |
| Test class | `UpperCamelCase` + suffix `Test` | `OrderServiceTest`, `PricingTest` |
| Test method | `lowerCamelCase` | `methodName_StateUnderTest_ExpectedBehavior` |
| Unnamed variable (JDK 22+) | `_` | Unused bindings in patterns or catch blocks. **Not available in JDK 21.** |

#### Naming Rules Specific to Functional Code

- **Name `Function` and `Predicate` variables by their behavior**, not their type.
  Copilot must use names that read naturally inside a pipeline.

```java
// Good — names read like prose inside the stream pipeline
Predicate<User> isActive   = User::isActive;
Predicate<User> isPremium  = u -> u.tier() == Tier.PREMIUM;
Predicate<User> isEligible = isActive.and(isPremium);

Function<Order, Invoice> toInvoice = order ->
    new Invoice(order.id(), order.total(), LocalDate.now());

List<Invoice> invoices = orders.stream()
    .filter(isEligible)
    .map(toInvoice)       // reads: "map each order to an invoice"
    .toList();

// Bad — type-oriented names obscure intent and break pipeline readability
Predicate<User> predicate1 = u -> u.isActive() && u.tier() == Tier.PREMIUM;
Function<Order, Invoice> function1 = order -> new Invoice(order.id(), order.total(), LocalDate.now());
```

- **Name pure methods as transformations**, not commands.
  A pure method produces a new value — its name should reflect that.

```java
// Good — transformation names signal no mutation
BigDecimal discountedPrice = applyDiscount(price, rate);
Order      confirmedOrder  = order.withStatus(CONFIRMED);
Email      normalizedEmail = email.normalize();

// Bad — command names imply mutation; misleading in a pure context
void processDiscount(BigDecimal price, double rate); // returns void — cannot be composed
void updateStatus(Order order);                      // implies mutation of the argument
```

- **Avoid abbreviations and generic names** that force the reader to guess context.

```java
// Good
UserRegistration registration = buildRegistration(name, email);
OrderConfirmation confirmation = service.placeOrder(cart);

// Bad
var r   = buildReg(n, e);
var res = svc.place(c);
```

---

### 2. `var` — Local Type Inference

Use `var` only when the inferred type is **immediately obvious** from the right-hand side.
In a functional codebase, type visibility is especially important: the type of a `Function`,
`Predicate`, or `Result` communicates the transformation contract to the reader.

```java
// Good — type is unambiguous from the constructor or factory
var users   = new ArrayList<User>();
var timeout = Duration.ofSeconds(30);
var scope   = new StructuredTaskScope.ShutdownOnFailure(); // JDK 25

// Good — var in lambda parameters to attach annotations (JDK 11+)
BiFunction<String, String, String> concat = (@NonNull var a, @NonNull var b) -> a + b;

// Bad — return type is not visible; reader must navigate to the method signature
var result       = userRepository.fetch();      // Optional<User>? List<User>? Result<User, ?>?
var confirmation = service.placeOrder(cart);    // what does this return?
```

---

### 3. Documentation (Javadoc)

Write Javadoc for all `public` and `protected` API members.
Document the **contract, invariants, and purity** — not the implementation.
The code already shows *what*; Javadoc must explain *why*, *when*, and *what is guaranteed*.

- Use `@param`, `@return`, and `@throws` consistently.
- Declare purity explicitly with `@implSpec` when a method is a pure function.
- Document thread-safety guarantees for types used in concurrent contexts.
- Use `@Deprecated(since = "...", forRemoval = true)` for planned removals,
  aligned with a major version increment to avoid breaking callers.

```java
/**
 * Applies a percentage discount to the given price.
 *
 * <p>This is a pure function: it does not mutate its arguments,
 * performs no I/O, and has no observable side effects.
 * The same inputs always produce the same output.
 *
 * @implSpec Pure function. Safe to use inside Stream pipelines and parallel contexts.
 * @param price the original price; must be non-null and non-negative
 * @param rate  the discount rate in [0.0, 1.0]
 * @return the discounted price, rounded to 2 decimal places (HALF_UP)
 * @throws IllegalArgumentException if {@code rate} is outside [0.0, 1.0]
 */
public static BigDecimal applyDiscount(BigDecimal price, double rate) { ... }

/**
 * Represents a validated, normalized email address.
 *
 * <p>Invariant: {@code value} is always non-null, non-blank, lowercase,
 * and contains exactly one {@code @} character. These constraints are
 * enforced at construction time and cannot be violated after instantiation.
 *
 * @param value the normalized email string
 */
record Email(String value) {
    Email {
        if (value == null || !value.contains("@"))
            throw new IllegalArgumentException("Invalid email: " + value);
        value = value.strip().toLowerCase();
    }
}
```

---

### 4. Annotations

- Use `@Override` on every method that overrides or implements a supertype member.
- Use `@Nullable` / `@NotNull` (JSR-305 or JetBrains) to assist static analysis tools
  and signal nullability intent explicitly — never rely on convention alone.
- Never suppress warnings without a comment explaining the specific and justified reason.

```java
// Good — @Override prevents silent mismatch when the supertype changes signature
@Override
public Result<Order, OrderError> placeOrder(Cart cart) { ... }

// Good — nullability is explicit; static analysis can enforce it
public Optional<User> findById(@NotNull String id) { ... }

// Bad — suppressing without justification hides real bugs from static analysis
@SuppressWarnings("unchecked")
List<Order> orders = (List<Order>) rawList;
```

---

### 5. Collection Standards

- Always declare collection variables using **interface types**: `List`, `Set`, `Map` —
  never `ArrayList`, `HashSet`, or `HashMap` (*Effective Java*, Item 64).
- Use `List.of()`, `Set.of()`, `Map.of()` for collections that must not change after creation.
- Use `Stream.toList()` (JDK 16+) as the default terminal collector — it returns an unmodifiable list.
- Apply **defensive copies** in compact constructors when accepting mutable collections.
- Never expose internal mutable collections through accessor methods.

```java
// Good — interface type, unmodifiable construction, defensive copy
record Config(List<String> hosts) {
    Config {
        hosts = List.copyOf(hosts); // snapshot at construction; caller mutations have no effect
    }
}

// Good — Stream.toList() returns unmodifiable; no explicit collector needed
List<String> activeNames = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();

// Bad — mutable result escapes; callers can modify the returned list
public List<Order> getOrders() {
    return orders; // internal state exposed directly
}

// Bad — Collectors.toList() returns a mutable list; misleadingly similar to toList()
.collect(Collectors.toList());
```

---

### 6. Resource Management

Use **try-with-resources** for every `AutoCloseable` type (files, sockets, JDBC connections,
`StructuredTaskScope`). Manual `close()` calls are not acceptable — they are silently skipped
when an exception is thrown before the call is reached.

```java
// Good — resource is always released, even if the body throws
try (var reader = new BufferedReader(new FileReader(path))) {
    return reader.readLine();
}

// Good — StructuredTaskScope is AutoCloseable; always use try-with-resources (JDK 25)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task = scope.fork(() -> fetchData());
    scope.join().throwIfFailed();
    return task.get();
}

// Bad — close() not reached if readLine() throws; resource leaks (Sonar S2095)
BufferedReader reader = new BufferedReader(new FileReader(path));
String line = reader.readLine();
reader.close();
```

For resources that are externally limited (e.g., database connections with a fixed pool size),
use a `Semaphore` to throttle concurrent virtual threads rather than a fixed thread pool.

```java
// Good — semaphore limits concurrent DB access without capping virtual thread count
private static final Semaphore DB_PERMITS = new Semaphore(20);

Response query(String sql) throws InterruptedException {
    DB_PERMITS.acquire();
    try {
        return db.execute(sql);
    } finally {
        DB_PERMITS.release();
    }
}
```

---

### 7. Static Analysis Compliance

All generated code must pass SonarQube rules without suppression.
Key rules that intersect with functional code:

| Sonar Rule | Description | Functional Mitigation |
|---|---|---|
| `S2095` | Resource not closed | Always use try-with-resources |
| `S4973` | Reference equality on objects | Use `.equals()` or `Objects.equals()` |
| `S2583` / `S2589` | Condition always true/false | Eliminate dead branches; use sealed exhaustiveness |
| `S3776` | Cognitive complexity too high | Extract named functions; flatten with early returns |
| `S1854` | Unused assignment | Remove; in patterns use `_` (JDK 22+) |

> If a Sonar rule and a guideline in this file conflict, **the Sonar rule takes precedence**
> to ensure CI/CD passes. Open a team issue to reconcile the conflict deliberately.



## Exception Handling

### Exception Handling: The Functional Approach

The core rule is strict (*Functional Programming in Java*, ch. 7):
**Expected business failures are values. Unexpected infrastructure errors are exceptions.**

This distinction is not stylistic — it is architectural. When a failure is modeled as a value,
the compiler forces every caller to handle it. When it is modeled as an exception, the compiler
enforces nothing, and the error can silently propagate or be swallowed anywhere in the call stack.

---

### The Fundamental Distinction

| Type | Definition | Examples | Model as |
|---|---|---|---|
| **Expected failure** | A predictable outcome that is part of the business domain. The system anticipates it. | Item out of stock, user not found, validation rejected | `Result<T, E>` or `Optional<T>` |
| **Exceptional error** | An unexpected, unrecoverable condition outside the domain's control. | Database unreachable, network timeout, programming bug | Unchecked exception |

> **Golden rule:** If you write a `catch` block to react to a business condition,
> that condition should have been modeled as `Result` or `Optional` instead.

---

### Strategy Priority

> The **functional-first (purista)** approach is the **default strategy** in this file:
> model failures as `Result<T, E>` values. Only fall back to checked or unchecked exceptions
> (the **conservative strategy**) when the functional approach is genuinely impractical.
>
> **Use `Result<T, E>` (default — always start here):**
> - Any expected business failure: validation errors, missing resources, violated domain rules
> - Whenever the compiler must force the caller to handle the error explicitly
> - All domain core and application service methods
>
> **Fall back to exceptions only when (use these criteria, not convenience):**
> - Wrapping infrastructure failures that are irrecoverable (database down, I/O error, network timeout)
> - Integrating with third-party APIs that throw checked exceptions you do not control
> - Writing adapter or controller layer code where a framework intercepts exceptions
>   (e.g., Spring `@ExceptionHandler`, JAX-RS `ExceptionMapper`) — throw domain-specific
>   exceptions **only at the adapter boundary**, never inside the functional core
> - Propagating `Result` would require refactoring 5+ caller layers with no meaningful gain in clarity
>
> See `java-improved.instructions.md` for the conservative exception handling guidelines.

---

### Rule 1 — `Result<T, E>` Is Unbounded: `E` Is a Value, Not an Exception

> ⚠️ **Critical:** Never declare `Result<T, E extends Exception>`.
> The bound `E extends Exception` forces domain errors to be `Exception` subclasses,
> directly contradicting the functional principle that **failures are values, not exceptions**.
> `E` must always be **unbounded** so that sealed domain error types — which do not extend
> `Exception` — can be used as the error parameter.

```java
// Correct — unbounded E: domain errors are plain sealed values, not exceptions
sealed interface Result<T, E> permits Result.Ok, Result.Err {
    record Ok<T, E>(T value)  implements Result<T, E> {}
    record Err<T, E>(E error) implements Result<T, E> {}

    // Functor: transform the success value without unwrapping
    default <U> Result<U, E> map(Function<T, U> f) {
        return switch (this) {
            case Ok(var v)  -> new Ok<>(f.apply(v));
            case Err(var e) -> new Err<>(e);
        };
    }

    // Monad: chain operations that may also fail; short-circuits on first Err
    default <U> Result<U, E> flatMap(Function<T, Result<U, E>> f) {
        return switch (this) {
            case Ok(var v)  -> f.apply(v);
            case Err(var e) -> new Err<>(e);
        };
    }

    static <T, E> Result<T, E> ok(T value)  { return new Ok<>(value); }
    static <T, E> Result<T, E> err(E error) { return new Err<>(error); }
}

// Wrong — E extends Exception forces domain errors to be throwable objects
// This binds your domain model to the exception hierarchy and breaks functional composition
sealed interface Result<T, E extends Exception> permits Result.Ok, Result.Err { ... }
```

---

### Rule 2 — Model Expected Failures as Sealed Domain Error Types

Domain errors are a **closed set of named variants** — exactly what sealed interfaces model.
Every variant carries the data needed to describe the failure precisely.
When a new variant is added, the compiler identifies every `switch` that must be updated.

```java
// Domain error type: a sealed value hierarchy, not an exception hierarchy
sealed interface OrderError permits OrderError.OutOfStock, OrderError.InvalidCart {
    record OutOfStock(List<Item> items) implements OrderError {}
    record InvalidCart(String reason)   implements OrderError {}
}

// Good — honest signature: returns an Order OR a typed, structured reason for failure
Result<Order, OrderError> placeOrder(Cart cart) {
    if (!inventory.has(cart.items()))
        return Result.err(new OrderError.OutOfStock(cart.items()));
    if (!cart.isValid())
        return Result.err(new OrderError.InvalidCart("Cart is empty"));
    return Result.ok(repository.save(new Order(cart)));
}

// The compiler enforces exhaustive handling — it is impossible to ignore the error case
String response = switch (service.placeOrder(cart)) {
    case Result.Ok(Order order)              -> "Placed: "  + order.id();
    case Result.Err(OrderError.OutOfStock e) -> "No stock for: " + e.items();
    case Result.Err(OrderError.InvalidCart e)-> "Invalid: " + e.reason();
    // JDK 25: use unnamed variable (_) to ignore a field you don't need:
    // case Result.Err(OrderError.OutOfStock _) -> "Out of stock";
};

// Monadic chaining — each step may fail; the pipeline short-circuits on the first Err
Result<OrderConfirmation, OrderError> confirm = validateCart(cart)
    .flatMap(this::checkInventory)
    .flatMap(this::applyDiscount)
    .map(this::toConfirmation);

// Bad — the signature lies; the compiler cannot enforce error handling at the call site
Order placeOrder(Cart cart) {
    if (!inventory.has(cart.items())) throw new OutOfStockException("Out of stock");
    return repository.save(new Order(cart));
}
// Callers can ignore the exception entirely — and the code still compiles
Order order = service.placeOrder(cart); // throws silently at runtime if stock is empty
```

---

### Rule 3 — Use `Optional<T>` for Simple Absence Without a Reason

`Optional<T>` is appropriate when the only question is "present or absent" and the caller
does not need to know *why* the value is absent (*Modern Java in Action*, ch. 11).
When the absence carries a reason, use `Result<T, E>` instead.

```java
// Good — absence is explicit in the signature; no null propagation
Optional<User> findById(String id) {
    return userRepository.findById(id);
}

// Functional chain — no manual unwrapping
String name = findById(id)
    .filter(User::isActive)
    .map(User::name)
    .orElse("User not found");

// Fail fast with a domain exception when absence is truly unexpected
User user = findById(id)
    .orElseThrow(() -> new UserNotFoundException(id));

// Lazy alternative — or() defers computation; remoteConfig() is only called if local is empty
Optional<Config> config = localConfig()
    .or(() -> remoteConfig())
    .or(() -> defaultConfig());

// Bad — null returned silently; NullPointerException surfaces at an unpredictable call site
User findById(String id) {
    return db.query(id); // null if not found
}

// Bad — imperative unwrapping defeats the purpose of Optional
Optional<User> opt = findById(id);
if (opt.isPresent()) {
    return opt.get().name(); // equivalent to a null check — not functional
}
return null;
```

---

### Rule 4 — Reserve Exceptions for Truly Exceptional Infrastructure Errors

Infrastructure failures — a database going down, a network timeout, a file system error —
are outside the domain's control and are not part of the expected business flow.
For these, exceptions are the correct tool. Always chain the original cause to preserve
the full stack trace for diagnosis.

```java
// Good — infrastructure failure wrapped in a domain-specific exception; cause preserved
Order save(Order order) {
    try {
        return db.insert(order);
    } catch (SQLException e) {
        // The original cause is chained: never discard it
        throw new DataAccessException("Failed to persist order id=" + order.id(), e);
    }
}

// Good — multiple infrastructure failure types handled specifically
Response call(HttpRequest request) {
    try {
        return httpClient.send(request, bodyHandler);
    } catch (IOException e) {
        throw new IntegrationException("External call failed: " + request.uri(), e);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt(); // restore the interrupt flag — always required
        throw new IntegrationException("Call interrupted: " + request.uri(), e);
    }
}

// Bad — generic exception loses all context; impossible to diagnose in production
throw new RuntimeException("Error");

// Bad — original cause discarded; the root stack trace is permanently lost
throw new DataAccessException("Failed to save"); // missing ", e"
```

---

### Rule 5 — Never Swallow Exceptions Silently

Catching an exception without acting on it hides real failures and makes the system
impossible to debug. Every catch block must do one of: rethrow with context, log and rethrow,
or handle the error with an explicit and intentional alternative value.

```java
// Good — failure logged and rethrown with context
try {
    return Files.readString(path);
} catch (IOException e) {
    throw new DataLoadException("Failed to read config: " + path, e);
}

// Bad — exception swallowed; the system silently continues in an incorrect state
try {
    return Files.readString(path);
} catch (IOException e) {
    return null; // caller cannot distinguish "file was empty" from "read failed"
}

// Bad — logged but not rethrown; flow continues as if nothing happened
try {
    return Files.readString(path);
} catch (IOException e) {
    log.error("Error", e);
    return ""; // caller receives a silent fallback with no indication of failure
}
```

---

### Rule 6 — Use Domain-Specific Exception Classes

Generic exceptions (`RuntimeException`, `IllegalStateException`) carry no domain context
and cannot be handled differently by upper layers. Define a sealed exception hierarchy
per domain so that adapters and error handlers can discriminate precisely.

```java
// Good — sealed exception hierarchy mirrors the domain structure
sealed class DomainException extends RuntimeException
    permits UserNotFoundException, OrderProcessingException {
    DomainException(String message)                  { super(message); }
    DomainException(String message, Throwable cause) { super(message, cause); }
}

// Thrown only at the adapter boundary — never inside the functional core
final class UserNotFoundException extends DomainException {
    UserNotFoundException(String userId) {
        super("User not found: " + userId);
    }
}

final class OrderProcessingException extends DomainException {
    OrderProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}

// Bad — generic exception; cannot be handled differently by framework error mappers
throw new RuntimeException("Processing failed");

// Bad — catches too broadly; captures JVM errors that should never be caught here
try {
    return processOrder(order);
} catch (Exception e) { // catches OutOfMemoryError indirectly via Exception subtype paths
    log.error("Error", e);
    return null;
}
```

---

### Decision Summary

```
Expected business failure              →  Result<T, E> or Optional<T>
  "user not found"                          honest signature
  "item out of stock"                       compiler enforces handling
  "validation rejected"                     composable via map / flatMap

Unexpected infrastructure error        →  Domain-specific unchecked exception
  "database unreachable"                    original cause always chained
  "network timeout"                         specific type, never RuntimeException
  "programming bug"                         never swallowed silently

E in Result<T, E>                      →  Always unbounded
  sealed OrderError                         NOT E extends Exception
  sealed ValidationError                    domain values, not throwables
  String, enum, record                      any type is valid as E
```
---

## Best Practices

### Records (JDK 16+)
Prefer Records for DTOs, value objects, and domain events. They are immutable by design, eliminate boilerplate, and integrate natively with Pattern Matching.

#### Good Example - Records for Data Carriers
```java
record UserCreated(String userId, Instant occurredAt) {}
```

#### Bad Example - Verbose Classes for Data Carriers
```java
class UserCreated {
    private final String userId;
    private final Instant occurredAt;
    // constructor, equals, hashCode, toString...
}
```

### Pattern Matching for `instanceof` (JDK 16+)
Eliminate manual casts and combine type checking with variable extraction.

#### Good Example - Pattern Matching with Guard
```java
if (shape instanceof Circle c && c.radius() > 0) {
    return Math.PI * c.radius() * c.radius();
}
```

#### Bad Example - Manual Casting
```java
if (shape instanceof Circle) {
    Circle c = (Circle) shape;
    if (c.radius() > 0) { ... }
}
```

### Text Blocks (JDK 15+)
Use text blocks for multiline SQL, JSON, or XML literals to improve readability and avoid concatenation noise.

#### Good Example - Text Blocks
```java
String query = """
        SELECT id, name
        FROM users
        WHERE active = true
        ORDER BY name
        """;
```

#### Bad Example - String Concatenation
```java
String query = "SELECT id, name\n" +
               "FROM users\n" +
               "WHERE active = true\n" +
               "ORDER BY name\n";
```

### Type Inference with `var` (JDK 10+)
Use `var` **only** when the type is immediately clear from the right-hand side of the assignment. If the method name does not make the return type obvious, declare the type explicitly to maintain readability.

#### Good Example - Obvious Type Inference
```java
var users = new ArrayList<User>();
var timeout = Duration.ofSeconds(30);

// In lambda parameters when annotations are needed
BiFunction<String, String, String> concat = (@NonNull var a, @NonNull var b) -> a + b;
```

#### Bad Example - Obscure Type Inference
```java
var result = userRepository.fetch(); // What type is result? Optional<User>? List<User>?
```

### Sequenced Collections (JDK 21+)
Prefer `SequencedCollection`, `SequencedSet`, or `SequencedMap` when encounter-order matters. It provides a unified API for accessing the first and last elements.

#### Good Example - Sequenced API
```java
SequencedCollection<String> items = new LinkedList<>(List.of("a", "b", "c"));
String first = items.getFirst();
String last  = items.getLast();
```

#### Bad Example - Legacy Index-based Access
```java
List<String> items = new LinkedList<>(List.of("a", "b", "c"));
String first = items.get(0);
String last  = items.get(items.size() - 1); // O(n) traversal on LinkedList!
```

### Primitive Patterns in switch (JDK 25)
When dispatching logic based on a primitive value (`int`, `long`, `double`), use pattern matching directly on the primitive type. This avoids unnecessary boxing to wrapper classes like `Integer`.

#### Good Example - Primitive Pattern Matching
```java
String describeStatus(int code) {
    return switch (code) {
        case 200 -> "OK";
        case 404 -> "Not Found";
        case 500 -> "Internal Server Error";
        case int c when c > 500 -> "Unknown Server Error (" + c + ")";
        default  -> "Unknown";
    };
}
```

#### Bad Example - Forcing Wrapper Types
```java
String describeStatus(Integer code) { ... } // Unnecessary boxing just to use advanced switch features
```

---

## Common Code Smells

### Deep Nesting
Replace deep nesting with early returns (guard clauses) or functional chains.

#### Good Example - Early Returns Flatten Nesting
```java
Optional<Discount> getDiscount(Order order) {
    if (!order.isEligible()) return Optional.empty();
    if (order.total().compareTo(MINIMUM_ORDER) < 0) return Optional.empty();
    return Optional.of(new Discount(DISCOUNT_RATE));
}
```

#### Bad Example - Arrow Anti-Pattern
```java
Optional<Discount> getDiscount(Order order) {
    if (order.isEligible()) {
        if (order.total().compareTo(MINIMUM_ORDER) >= 0) {
            return Optional.of(new Discount(DISCOUNT_RATE));
        }
    }
    return Optional.empty();
}
```

### Parameter Objects
Keep method parameter lists to **≤ 4 parameters**. Group related parameters into a record.

#### Good Example - Parameter Object
```java
record UserRegistration(String name, String email, String role, Locale locale) {}

void registerUser(UserRegistration registration) { ... }
```

#### Bad Example - Long Parameter List
```java
void registerUser(String name, String email, String role, Locale locale,
                  boolean sendWelcome, String referralCode) { ... }
```

---

## Architecture Guidelines

- Apply **Single Responsibility**: Each class has one reason to change.
- Depend on **interfaces**, not concrete implementations.
- Organize packages by **feature/domain** (`com.example.orders`) rather than by layer (`com.example.controllers`).
- Prefer **composition over inheritance**. Use functional abstractions (interfaces + lambdas) before creating deep class hierarchies.
- **Java Platform Module System (JPMS)**: In large codebases, use `module-info.java` to enforce strict dependency boundaries. Export only public API packages; keep internal implementation packages encapsulated. JPMS prevents accidental coupling between modules and enables reliable static analysis.

```java
// module-info.java — Functional domain module
module com.example.orders {
    requires java.base;         // implicit, shown for clarity
    exports com.example.orders.api;       // Public API: interfaces, records, Result types
    // com.example.orders.internal is NOT exported — encapsulated by default
}
```

## Anti-Patterns to Avoid

| Anti-Pattern | Reason | Solution |
| :--- | :--- | :--- |
| `System.currentTimeMillis()` | Non-deterministic | Pass `Instant` as an argument |
| `Optional.get()` | Throws exception | Use `orElseThrow()` or `map()` |
| `synchronized` | Pins Virtual Threads | Use `ReentrantLock` |
| Deep Recursion | Stack Overflow | Use `Stream.iterate()` or Trampoline |
| `default` in sealed switch | Hides missing cases | Remove `default` to let compiler check |
---

## Performance

### 1. Profile Before Optimizing
Use **Java Flight Recorder (JFR)** and **JMH** (Java Microbenchmark Harness). Never rely on `System.currentTimeMillis()` for benchmarks (*Effective Java, Item 67*).

### 2. Virtual Threads
For I/O-bound services, scale using Virtual Threads. Do not pool them. Use a `Semaphore` to throttle concurrent access to limited resources (e.g., database connections).

### 3. Primitive Streams
Prefer `IntStream`, `LongStream`, and `DoubleStream` for large numeric collections to avoid boxing overhead.
- **Primitive Pattern Matching (JDK 25)**: Dispatch directly on primitives in `switch` statements to avoid `Integer`/`Long` autoboxing.

### 4. Lazy Evaluation vs Eager Evaluation

Streams are **lazy by default** — intermediate operations (`map`, `filter`) do not execute until a terminal operation (`toList`, `reduce`, `forEach`) is invoked. This avoids processing elements that aren't needed.

```java
// Lazy: only processes elements until findFirst() succeeds
Optional<User> admin = users.stream()
    .filter(User::isActive)      // NOT executed until terminal op
    .filter(User::isAdmin)       // NOT executed until terminal op
    .findFirst();                // Terminal: triggers lazy evaluation

// Eager: processes ALL elements regardless of need
List<User> activeAdmins = users.stream()
    .filter(User::isActive)
    .filter(User::isAdmin)
    .toList();                   // Terminal: processes entire stream

// Supplier-based laziness for scalar values
Supplier<ExpensiveReport> report = () -> generateReport(data);
if (needsReport) {
    return report.get(); // Only computed when needed
}
```

> **Rule**: Always use lazy terminal operations (`findFirst`, `findAny`, `anyMatch`) when you don't need the entire result set. Use `Supplier<T>` for deferred scalar computations.

### 5. Memory Overhead: Streams vs Imperative Loops

Streams introduce object overhead (pipeline objects, lambda instances, spliterators). For **small collections** or **tight inner loops**, the overhead is measurable. For **large collections** or **complex transformations**, Streams are comparable or better due to JIT optimization.

```java
// Stream: allocates pipeline objects (Source + filter + map + collector)
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();
// Overhead: ~3-5 objects for the pipeline. JIT may inline for hot paths.

// Imperative: minimal object allocation
List<String> names = new ArrayList<>(users.size());
for (User u : users) {
    if (u.isActive()) {
        names.add(u.name());
    }
}
// Overhead: only the ArrayList + Iterator. Lower constant factor.

// Recommendation: Use Streams by default for clarity.
// Switch to imperative ONLY if JMH profiling shows measurable overhead in a hot path.
```

### 6. Garbage Collection Pressure from Lambdas and Closures

Lambdas that **capture local variables** (closures) create a new object instance on each invocation, increasing GC pressure. Non-capturing lambdas and method references are cached by the JVM as singletons.

```java
// Bad: Capturing lambda — creates a new object per invocation
BigDecimal threshold = BigDecimal.valueOf(100);
orders.stream()
    .filter(o -> o.total().compareTo(threshold) > 0)  // Closure captures 'threshold'
    .toList();

// Good: Method reference or non-capturing lambda — JVM-cached singleton
Predicate<Order> isHighValue = Order::isHighValue;  // Method ref: cached
orders.stream().filter(isHighValue).toList();

// Good: Extract predicate to a field/constant to avoid repeated closure creation
private static final Predicate<Order> HIGH_VALUE =
    o -> o.total().compareTo(HIGH_VALUE_THRESHOLD) > 0; // Created once
```

> **Rule**: In hot loops or high-throughput paths, extract capturing lambdas into `static final` fields or method references. Profile with JFR to identify excessive short-lived object allocation.

### 7. String Concatenation
Prefer `StringBuilder` or `StringJoiner` inside loops. For simple expressions, the `+` operator is optimized by `StringConcatFactory`.

---

## Testing Standards

Test pure functions in isolation — they require no mocks and no setup (*Functional Thinking*, ch. 9).

- Use **JUnit 5** (`@Test`, `@ParameterizedTest`).
- Use **AssertJ** for fluent assertions (`assertThat(x).isEqualTo(y)`).
- Follow **Arrange-Act-Assert (AAA)** structure.
- Use **Mockito** ONLY at integration boundaries (Repositories, HTTP clients). Do not mock pure domain records.
- **Testing Structured Concurrency (JDK 25)**: Test `StructuredTaskScope` fan-out by using real Virtual Threads and lightweight stubs. Do not mock the scope itself.

#### Good Example - Parameterized Pure Function Test
```java
class DiscountTest {

    @ParameterizedTest(name = "rate {1} on {0} -> {2}")
    @CsvSource({
        "100.00, 0.10, 90.00",
        "100.00, 0.00, 100.00",
        "100.00, 1.00, 0.00"
    })
    void applyDiscount_ReturnsExpectedPrice(BigDecimal price, double rate, BigDecimal expected) {
        // No mocks needed for pure functions
        assertThat(Pricing.applyDiscount(price, rate))
            .isEqualByComparingTo(expected);
    }
}
```

#### Good Example - Infrastructure Boundary Test with Mockito
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock OrderRepository repository;
    @InjectMocks OrderService orderService;

    @Test
    void placeOrder_WhenItemsAvailable_ReturnsConfirmedOrder() {
        var order = new Order(List.of(new Item("SKU-1", 2)));
        when(repository.save(order)).thenReturn(order.withStatus(CONFIRMED));

        var result = orderService.placeOrder(order);

        assertThat(result.status()).isEqualTo(CONFIRMED);
    }
}
```

#### Bad Example - Mocking Domain Objects
```java
// Do not mock records or value objects; instantiate them directly
Order mockOrder = mock(Order.class);
when(mockOrder.total()).thenReturn(BigDecimal.TEN);
```

---

## Build and Verification

After adding or modifying code, verify the build and all tests pass.

| Build Tool | Command |
|---|---|
| Maven | `mvn clean verify` |
| Gradle | `./gradlew build` |
| SonarScanner | `sonar-scanner -Dsonar.projectKey=<key>` |

Ensure the project declares the target Java version matching your environment:
- **Maven**: `<java.version>21</java.version>` or `<java.version>25</java.version>`
- **Gradle**: `sourceCompatibility = JavaVersion.VERSION_21` (or `25`)


---

## Additional Resources

- [JDK 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [JEP 444 — Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 441 — Pattern Matching for switch](https://openjdk.org/jeps/441)
- [JEP 431 — Sequenced Collections](https://openjdk.org/jeps/431)
- [JEP 409 — Sealed Classes](https://openjdk.org/jeps/409)
- [JEP 395 — Records](https://openjdk.org/jeps/395)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- *Becoming Functional* — Joshua Backfield
- *Functional and Reactive Domain Modeling* — Debasish Ghosh
- *Functional Thinking* — Neal Ford
- *Reactive Systems in Java* — Clement Escoffier & Ken Finnigan
- *Functional Programming in Java* — Pierre-Yves Saumont
- *Modern Java in Action* — Raoul-Gabriel Urma
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [AssertJ Documentation](https://assertj.github.io/doc/)
- [SonarQube Java Rules](https://rules.sonarsource.com/java/)
