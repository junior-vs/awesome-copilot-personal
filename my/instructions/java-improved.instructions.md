---
description: 'Guidelines for building high-quality Java applications targeting JDK 21 LTS, covering modern language features, architecture, testing, and static analysis'
applyTo: '**/*.java'
tools: ['search/codebase', 'edit/editFiles', 'search', 'web/fetch', 'execute/getTerminalOutput', 'execute/runInTerminal', 'read/terminalLastCommand', 'read/terminalSelection']
name: 'Java Development Guidelines (JDK 21 LTS)'
---

Guidelines for writing clean, maintainable, and modern Java code targeting **JDK 21 (LTS)**.
These rules apply to all `.java` source files and are grounded in:

- *Effective Java* — Joshua Bloch
- *Java Concurrency in Practice* — Brian Goetz
- *Modern Java in Action* — Raoul-Gabriel Urma
- *Modern Concurrency in Java (2025/2026)* - (A N M Bazlur Rahman)
- *Thinking in Java* — Bruce Eckel
- *Core Java Volumes I and II* - 13ª Edition — Cay S. Horstmann

> **Scope**: This is the **general/pragmatic** Java instruction. It covers modern Java development best practices using a balanced mix of OOP and functional idioms. For a stricter **functional-first (purista)** approach emphasizing immutability, pure functions, and algebraic data types, see `java-functional.instructions.md`.

---

## General Instructions

- **Prioritize Immutability**: Follow *Effective Java* (Item 17). Design classes to be immutable by default using `record`, `final` fields, and unmodifiable collections (`List.of`, `Map.of`).
- **Prefer Declarative over Imperative**: Use the Streams API and Lambdas for collection processing. Ensure functional pipelines are "side-effect free" (do not modify state outside the stream).
- **Embrace Modern Java Syntax**: Use Switch Expressions, Pattern Matching, and Records to reduce boilerplate and improve type safety.
- **Virtual Thread Awareness (Project Loom)**:
    - Design for high concurrency using Virtual Threads (`Executors.newVirtualThreadPerTaskExecutor()`).
    - **Avoid Pinning**: Do not use `synchronized` blocks or methods for long-running I/O operations; replace them with `ReentrantLock` to allow Virtual Thread unmounting.
- **Null Safety**: Never return `null` for methods returning sequences (return `List.of()`) or optional values (return `Optional.empty()`). Use `Objects.requireNonNull()` for mandatory arguments.
- **Logging Boundary**: Logging must happen at the **application layer** (services, controllers, adapters), never inside pure domain logic. A dedicated logging instruction will cover this topic in depth.
- **Composition over Inheritance**: Follow *Effective Java* (Item 18). Use `sealed` interfaces to define strict hierarchies and favor composition to keep the architecture flexible.
- **Static Analysis Compliance**:
    - All generated code must adhere to **SonarLint** and **Checkstyle** standards (e.g., avoiding cognitive complexity, proper resource management).
    - If a conflict arises between "clean code" and a specific Sonar rule (e.g., `S2095`), the Sonar rule takes precedence to ensure CI/CD passing.

---

### Example: Idiomatic Modern Java

#### Good Example
```java
// Uses Record for immutability, pattern matching, and functional pipeline
public record OrderProcessor(InventoryService inventory) {

    public List<String> getAvailableSkus(Order order) {
        return order.items().stream()
            .filter(item -> inventory.isAvailable(item.sku()))
            .map(Item::sku)
            .toList(); // JDK 16+ returns unmodifiable list
    }

    public double calculateDiscount(DiscountType type, double amount) {
        return switch (type) { // Exhaustive switch expression
            case PERCENTAGE(int p) -> amount * (p / 100.0);
            case FIXED(int f)      -> Math.min(f, amount);
        };
    }
}
```

#### Bad Example
```java
// Avoid: Boilerplate, mutability, and manual casting
public class OrderProcessor {
    private InventoryService inventory; // Mutable field

    public List<String> getAvailableSkus(Order order) {
        List<String> skus = new ArrayList<>(); // Mutable collection
        for (Item item : order.getItems()) {
            if (inventory.isAvailable(item.getSku())) {
                skus.add(item.getSku());
            }
        }
        return skus;
    }
}
```

---

### Key Improvements Rationale:

1.  **Immutability by Default**: Grounded in *Effective Java*. It reduces bugs in concurrent environments (crucial for JDK 21+ Virtual Threads).
2.  **Virtual Thread "Pinning" Warning**: This is a high-level requirement from *Modern Concurrency in Java*. If the AI generates `synchronized` blocks for I/O-bound code, it defeats the purpose of JDK 21's Virtual Threads.
3.  **Declarative Style**: Based on *Modern Java in Action*. It encourages shorter, more readable code that is easier for the compiler to optimize.
4.  **Exhaustive Switch & Records**: Replaces the old "General Instructions" boilerplate with the actual "Project Amber" features that define modern Java.
5.  **Refined Static Analysis**: Instead of telling the user how to configure a Sonar server, it tells the AI to **comply** with those rules during code generation.
6.  **Explicit JDK 16+ `toList()`**: Clarifies the difference between `Stream.toList()` (immutable) and `Collectors.toList()` (mutable), a common point of confusion.

---


## JDK 21 Feature Baseline

The table below summarises the key language and API features available as **stable** in JDK 21. Use them without hesitation — they are not preview features.

| Feature | JEP | Since (stable) |
|---|---|---|
| Records | JEP 395 | JDK 16 |
| Sealed Classes | JEP 409 | JDK 17 |
| Pattern Matching for `instanceof` | JEP 394 | JDK 16 |
| Pattern Matching for `switch` | JEP 441 | JDK 21 |
| Text Blocks | JEP 378 | JDK 15 |
| `var` (local type inference) | JEP 286 | JDK 10 |
| Virtual Threads | JEP 444 | JDK 21 |
| Sequenced Collections | JEP 431 | JDK 21 |
| `Stream.toList()` | — | JDK 16 |

> **Preview in JDK 21 (do not use in production):** Structured Concurrency (JEP 453), Scoped Values (JEP 446), Unnamed Variables (JEP 443), Unnamed Classes (JEP 445). These are finalized in later releases — upgrade when ready.

---

## Best Practices

### 1. Data Modeling with Records & Patterns
Use **Records** for transparent data carriers. Beyond simple DTOs, leverage **Record Patterns** (JDK 21+) for clean deconstruction.

-   **Avoid Manual Accessors**: Use deconstruction in `switch` and `instanceof`.
-   **Validation**: Use compact constructors for invariants (Effective Java, Item 50).

```java
// Good: Record deconstruction (JDK 21+)
if (obj instanceof Order(String id, Customer(String name), double total) && total > 1000) {
    log.info("High value order {} for {}", id, name);
}

// Good: Guarded patterns in switch
return switch (payment) {
    case CreditCard(var num, var expiry) when isExpired(expiry) -> throw new PaymentException("Expired card");
    case CreditCard(var num, _) -> processCredit(num);
    case DigitalWallet(var provider) -> processDigital(provider);
};
```

### 2. Sealed Hierarchies for Domain Modeling
Use `sealed` classes and interfaces to create **Algebraic Data Types (ADTs)**. This allows the compiler to ensure your domain logic handles every possible case.

-   **Rule**: Favor sealed hierarchies over open inheritance when the set of types is known and fixed (e.g., `Result<T, E>`, `UIState`, `Command`).
-   **JDK 25 Note**: Use **Unnamed Variables (`_`)** for components you don't need during deconstruction.

```java
// Modeling a Result type
sealed interface OperationResult<T> permits Success, Failure {}
record Success<T>(T data) implements OperationResult<T> {}
record Failure<T>(String error, Throwable cause) implements OperationResult<T> {}

// Exhaustive handling (No default branch!)
var message = switch (result) {
    case Success(var data) -> "Loaded: " + data;
    case Failure(var err, _) -> "Error: " + err; // JDK 25: case Failure(var err, _)
};
```

### 3. Modern Concurrency (Project Loom)
JDK 21/25 shifts the paradigm from thread pooling to **thread-per-task**.

-   **Virtual Threads**: Use `Executors.newVirtualThreadPerTaskExecutor()` for I/O-bound workloads. **Never pool virtual threads**.
-   **Avoid Pinning**: Do not use `synchronized` for long-running I/O. Use `ReentrantLock` to allow the carrier thread to unmount.
-   **Scoped Values (JDK 25 Stable)**: Replace `ThreadLocal` with `ScopedValue` for safer, immutable, and efficient context sharing across virtual threads.

```java
// JDK 25: Structured Concurrency & Scoped Values
private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

public void handleRequest(Request req) {
    ScopedValue.where(CURRENT_USER, authService.authenticate(req))
               .run(() -> {
                   try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
                       Subtask<Data> data = scope.fork(() -> fetchData());
                       scope.join().throwIfFailed();
                       process(data.get());
                   }
               });
}
```

### 4. Sequenced Collections (JDK 21+)
Use the `SequencedCollection` family (`List`, `Deque`, `LinkedHashSet`) when the order of elements is a first-class citizen.

-   **Avoid**: `list.get(0)` or `list.get(list.size() - 1)`.
-   **Use**: `list.getFirst()`, `list.getLast()`, and `list.reversed()`.

### 5. Functional Programming & Streams
-   **Immutability**: Use `Stream.toList()` (JDK 16+) to produce unmodifiable lists.
-   **Side Effects**: Ensure stream pipelines are pure. Avoid modifying external variables inside `.forEach()` or `.map()`.
-   **Primitive Streams**: Use `IntStream`, `LongStream`, or `DoubleStream` to avoid boxing overhead for large datasets (Effective Java, Item 45).

### 6. Robust Null Safety
-   **Optional for API Design**: Return `Optional<T>` only for return types where a value might be absent.
-   **Avoid Optional in Fields**: Do not use `Optional` for class fields or method parameters; use `@Nullable` or overloading instead.
-   **Fast-Fail**: Use `Objects.requireNonNull(val, "msg")` in constructors to prevent nulls from propagating.

### 7. Performance & Memory
-   **String Concatenation**: Use `.formatted()` or `Text Blocks` (JEP 378, stable since JDK 15) for complex multiline strings. Text Blocks are processed at compile-time and have no runtime overhead.
-   **Value-Based Classes**: Be aware that classes like `Optional`, `Duration`, and `LocalDate` are value-based. Avoid using them for synchronization; always use `.equals()` for comparison instead of identity checks (`==`).

### 8. Pragmatic Stream Usage

- **Favor Readability**: Use Streams only when the logic is clearer than an imperative loop. If a pipeline requires multi-line lambdas or complex state management, refactor to a loop or extract helper methods (*Effective Java*, Item 45).
- **Side Effects**: Limit side effects to terminal operations like `forEach`. Never modify external state inside `filter` or `map`.

#### Good Example - Clear Stream
```java
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .toList();
```

#### Bad Example - Over-functionalized Logic
```java
// Hard to debug and read
users.stream().collect(groupingBy(User::getDept,
    mapping(User::getName, filtering(n -> n.length() > 5, toList()))));
```


### 9. Advanced Enum Patterns

- **Enums over Constants**: Use Enums instead of `int` or `String` constants (*Effective Java*, Item 34).
- **Behavioral Enums**: Use constant-specific method implementations or internal functional fields instead of large `switch` blocks inside the Enum.

#### Good Example - Strategy Enum
```java
public enum Operation {
    PLUS  ((x, y) -> x + y),
    MINUS ((x, y) -> x - y);

    private final BinaryOperator<Double> operator;
    Operation(BinaryOperator<Double> op) { this.operator = op; }
    public double apply(double x, double y) { return operator.apply(x, y); }
}
```

### 10. Throttling with Virtual Threads

- **No Pooling**: Never use `FixedThreadPool` for Virtual Threads.
- **Resource Protection**: Use a `Semaphore` to limit the number of concurrent calls to fragile resources (databases, third-party APIs) to prevent exhaustion.

#### Good Example - Semaphore Throttling
```java
public class ExternalService {
    private static final Semaphore LIMITER = new Semaphore(50); // Max 50 concurrent calls

    public Response call() throws InterruptedException {
        LIMITER.acquire();
        try {
            return httpClient.send(request, handler); // Virtual thread blocks here safely
        } finally {
            LIMITER.release();
        }
    }
}
```

### 11. Defensive API Design

- **Defensive Copies**: Return unmodifiable views or copies of internal mutable collections (*Effective Java*, Item 50).
- **Optional vs Null**: Use `Optional` only as a return type to indicate "no result." Never use `Optional` for method parameters or class fields.
- **Validation**: Validate all public API arguments using `Objects.requireNonNull()` or custom guard clauses immediately.

#### Good Example - Defensive Return
```java
public record Department(String name, List<Employee> employees) {
    public Department {
        employees = List.copyOf(employees); // Defensive copy
    }
    public List<Employee> employees() {
        return employees; // Already unmodifiable
    }
}
```



---

### Comparison: JDK 21 vs JDK 25 Best Practices

| Feature | JDK 21 (LTS) | JDK 25 |
| :--- | :--- | :--- |
| **Concurrency** | Virtual Threads (Stable), Structured Concurrency (Preview) | `StructuredTaskScope` (Stable), `ScopedValue` (Stable) |
| **Patterns** | Record Patterns & Switch (Stable) | Unnamed Patterns `_` and Variables (Stable) |
| **String Handling** | Use `.formatted()` or Text Blocks (JEP 378) | Use `.formatted()` or Text Blocks |
| **Main Method** | Standard `public static void main` | Unnamed Classes & Instance Main (Stable) |

---

### Rationale from the Literature:
1.  **Deconstruction (Amber)**: Cay Horstmann emphasizes that pattern matching isn't just "shorter code," it's about **totality**—ensuring the compiler catches unhandled states.
2.  **Pinning (Loom)**: Based on *Modern Concurrency in Java* (Bazlur Rahman). Pinning is the #1 performance killer in migration to Virtual Threads.
3.  **Scoped Values**: Brian Goetz (Java Architect) advocates for Scoped Values over `ThreadLocal` because they are bounded by scope and immutable, preventing the "leaky context" bugs described in *Java Concurrency in Practice*.
4.  **Exhaustiveness**: Joshua Bloch's *Effective Java* principles on Enums are now extended to Sealed Classes—compile-time safety over runtime `default` exceptions.


## Code Standards

### 1. Naming Conventions & Semantic Clarity
Follow the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) with modern additions for Records and Threads.

| Identifier | Style | Guidance |
| :--- | :--- | :--- |
| **Classes / Records** | `UpperCamelCase` | Nouns (e.g., `OrderService`, `UserRecord`). |
| **Methods** | `lowerCamelCase` | Verbs (e.g., `calculateTotal`, `isAvailable`). |
| **Record Components** | `lowerCamelCase` | Nouns (e.g., `id`, `createdAt`). Avoid `get` prefix. |
| **Variables / `var`** | `lowerCamelCase` | Short but descriptive. Avoid `list1`, `data`. |
| **Virtual Threads** | `lower-hyphen` | Use descriptive names for debugging (e.g., `worker-pool-1`). |
| **Unnamed Vars (JDK 22+)** | `_` | Use a single underscore for unused variables in patterns/catch blocks. **Not available in JDK 21** (Preview via JEP 443). Stable since JDK 22 (JEP 456). |

-   **Rule on `var`**: Use local variable type inference only when the type is **obvious** from the assignment (e.g., `var list = new ArrayList<String>();`). Avoid `var` when the return type of a method is not immediately clear.

### 2. Modern Exception Handling

> **Strategy Priority**: Prefer the **functional approach** (modeling failures as sealed `Result<T, E>` values) as the primary strategy. Use checked/unchecked exceptions as a **fallback** when the functional approach is impractical. See `java-functional.instructions.md` for the full purista exception handling guide.

-   **Prefer Unchecked Exceptions**: Use `RuntimeException` for programming errors. Use checked exceptions only for truly recoverable business conditions (*Effective Java, Item 70*).
-   **Specific Catching**: Never catch `Throwable` or `Exception`. Catch the most specific subtype.
-   **No Swallowing**: Catch blocks must either log the stack trace, rethrow, or handle the error.
-   **Structured Failure**: When using `StructuredTaskScope` (JDK 25), always use `.throwIfFailed()` to propagate subtask exceptions correctly.

```java
// Good: Resource management + Specific exception
try (var stream = Files.lines(path)) {
    return stream.map(this::parse).toList();
} catch (IOException e) {
    throw new UncheckedIOException("Critical failure reading config: " + path, e);
}

// Good: JDK 25 Unnamed Catch
try {
    Integer.parseInt(input);
} catch (NumberFormatException _) { // Underscore indicates the exception is intentionally ignored
    return 0;
}
```

### 3. Documentation (Javadoc) & Modern Annotations
-   **Document the "Why"**: Don't describe the code logic; describe the **contract**, **invariants**, and **thread-safety** (*Effective Java, Item 56*).
-   **Standard Tags**: Use `@param`, `@return`, and `@throws`.
-   **Text Blocks in Javadoc**: Use HTML5-compliant Javadoc with snippets.
-   **Annotations**:
    -   Use `@Override` religiously.
    -   Use `@Nullable` / `@NotNull` (from JSR-305 or JetBrains) to assist static analysis.
    -   Use `@Deprecated(since="...", forRemoval=true)` for planned removals. **Note**: Respect Semantic Versioning; when `forRemoval=true`, plan removal in a major version increment (e.g., v2.0.0) to minimize breaking changes for consumers.

### 4. Boilerplate Reduction
-   **Records**: Prefer records for data carriers to eliminate manual `equals()`, `hashCode()`, and `toString()` (*Effective Java, Item 10, 11*).
-   **Compact Constructors**: Use them for validation to keep the record definition clean.

```java
/**
 * Represents a validated money amount.
 * @param amount the numerical value, must be positive.
 * @param currency the ISO currency code.
 */
public record Money(BigDecimal amount, String currency) {
    public Money { // Compact constructor
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.signum() < 0) throw new IllegalArgumentException("Amount cannot be negative");
    }
}
```

### 5. Collection Standards
-   **Prefer Interfaces**: Always declare variables as `List`, `Set`, or `Map`, never `ArrayList` or `HashMap` (*Effective Java, Item 64*).
-   **Immutability**: Use `List.of()` or `Stream.toList()` for collections that should not change.
-   **Defensive Copies**: When a record or class accepts a mutable collection in its constructor, store a defensive copy: `this.items = List.copyOf(items);`.

### 6. Resource Management
-   **Try-with-Resources**: Mandatory for all `AutoCloseable` types (Files, Sockets, JDBC).
-   **Virtual Threads**: If a resource (like a DB connection) is limited, use a `Semaphore` rather than a fixed thread pool to throttle virtual threads.

---

### Comparison: JDK 21 vs JDK 25 Standards

| Area | JDK 21 (LTS) | JDK 25 |
| :--- | :--- | :--- |
| **Variables** | Named variables required in all catch/patterns. | Use `_` for unused variables (JEP 456). |
| **Concurrency** | Manual management of `Thread.ofVirtual()`. | Use `StructuredTaskScope` for parent-child task logic. |
| **Main Method** | `public static void main(String[] args)` | Support for Unnamed Classes (instance main). |

---

### Rationale from the Literature:
1.  **Unnamed Variables**: Cay Horstmann emphasizes this reduces "cognitive load" by signaling to the reader that a value is irrelevant.
2.  **Effective Exceptions**: Joshua Bloch argues that checked exceptions should be rare because they clutter the API; modern Java idioms favor `RuntimeException` for infrastructure errors and sealed `Result` types for business failures.
3.  **Defensive Copying**: A core tenet of *Effective Java* (Item 50). Even with Records, if you pass an `ArrayList`, the record isn't truly immutable unless you copy it into an unmodifiable list.
4.  **Interface-based Programming**: A fundamental principle from *Thinking in Java* (Bruce Eckel) that ensures decoupling from implementation details.

---

## Common Bug Patterns

### 1. Virtual Thread Pinning (Project Loom)
**Bug:** Using `synchronized` blocks or methods around long-running I/O operations.
**Why:** In JDK 21/25, this "pins" the virtual thread to its carrier (platform) thread, preventing the JVM from re-scheduling other tasks and potentially leading to thread starvation or memory exhaustion.

-   **Fix:** Replace `synchronized` with `java.util.concurrent.locks.ReentrantLock` for long-running I/O.
-   **Fix:** Keep `synchronized` only for very fast, in-memory operations.

```java
// Avoid: Pins the carrier thread during I/O
synchronized (lock) {
    return httpClient.send(request, bodyHandler);
}

// Good: ReentrantLock allows the virtual thread to unmount
lock.lock();
try {
    return httpClient.send(request, bodyHandler);
} finally {
    lock.unlock();
}
```

### 2. Identity-Sensitive Operations on Value-Based Classes
**Bug:** Synchronizing on, or using identity equality (`==`) with value-based classes like `Optional`, `Duration`, `LocalDate`.
**Why:** Value-based classes are designed to be transparent wrappers around their values. Synchronizing on them can throw exceptions or cause unpredictable deadlocks.

-   **Rule:** Never use `synchronized` on `Optional` or date-time classes. Always use `.equals()` for comparison instead of identity checks (`==`).

### 3. Missing Defensive Copies in Records
**Bug:** Assuming a `record` is fully immutable when it contains mutable components (e.g., a `List` or `Date`).
**Why:** While the record's fields are `final`, the *contents* of the objects they point to can still be changed by the caller (*Effective Java, Item 50*).

-   **Fix:** Use the **Compact Constructor** to create unmodifiable copies.

```java
// Avoid: Caller can still modify the internal list
public record Order(List<String> items) {}

// Good: Defensive copy ensures true immutability
public record Order(List<String> items) {
    public Order {
        items = List.copyOf(items); // JDK 10+ creates an unmodifiable copy
    }
}
```

### 4. Non-Exhaustive Pattern Matching
**Bug:** Using `if (obj instanceof Subtype)` instead of a `switch` expression for sealed hierarchies.
**Why:** If a new subtype is added to a `sealed` interface later, the `if` block will silently ignore it, whereas a `switch` expression will fail to compile, forcing a proper update (*Modern Java in Action*).

```java
// Avoid: Silent failure if a new Shape is added
if (shape instanceof Circle) { ... }
else if (shape instanceof Square) { ... }

// Good: Compiler enforces exhaustiveness
return switch (shape) {
    case Circle c -> ...
    case Square s -> ...
    // No default needed if all sealed types are covered
};
```

### 5. Side-Effecting Stream Pipelines
**Bug:** Modifying external state (e.g., a shared list or counter) inside a `.map()` or `.filter()`.
**Why:** Streams are designed to be functional. Side effects make code thread-unsafe and prevent safe transition to `parallelStream()` (*Effective Java, Item 48*).

-   **Fix:** Use `Collectors` or `reduce()` to accumulate results.

```java
// Avoid: Side effect in stream
List<String> results = new ArrayList<>();
users.stream().filter(User::isActive).forEach(u -> results.add(u.name()));

// Good: Pure functional pipeline
List<String> results = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();
```

### 6. The `Optional.get()` Without `isPresent()`
**Bug:** Calling `.get()` directly on an `Optional`.
**Why:** It defeats the purpose of `Optional` and throws a `NoSuchElementException`, essentially acting like a `NullPointerException`.

-   **Fix:** Use `.orElse()`, `.orElseGet()`, or `.ifPresent()`.

### 7. Incorrect `SequencedCollection` Access
**Bug:** Using `list.get(0)` on a `LinkedList`.
**Why:** On a `LinkedList`, this is an $O(n)$ operation.
-   **Fix:** Use `list.getFirst()` from the **Sequenced Collections** API (JDK 21+), which clarifies intent and is optimized for the specific collection type.

---

### Comparison: Bug Prevention in JDK 21 vs JDK 25

| Bug Type | JDK 21 Prevention | JDK 25 Prevention |
| :--- | :--- | :--- |
| **Concurrency** | Detection of Pinning via JFR events. | **Structured Concurrency** prevents orphan threads. |
| **Logic Errors** | Pattern Matching exhaustiveness. | **Unnamed Patterns (`_`)** prevent unused variable clutter. |
| **Resource Leaks** | Standard Try-with-resources. | **Scoped Values** replace risky `ThreadLocal` inheritance. |

---

### Rationale from Literature:
1.  **Defensive Copying**: A core theme in *Effective Java*. Even with modern Records, the "immutability" is shallow by default.
2.  **Stream Purity**: *Modern Java in Action* argues that the power of Streams lies in their ability to be parallelized, which is impossible if they have side effects.
3.  **Loom Performance**: *Modern Concurrency in Java* (2025) highlights **Pinning** as the most common anti-pattern for developers moving from platform threads to virtual threads.
4.  **Identity-less Objects**: Cay Horstmann's *Core Java* (13th Edition) warns that identity-based operations on value-based classes are deprecated in preparation for Project Valhalla.

---

## Common Code Smells

### 1. Primitive Obsession
**The Smell:** Using primitive types (String, int, double) to represent domain concepts like `Email`, `Money`, or `Coordinate`.
**The Modern Cure:** Use **Java Records**. They are lightweight, immutable, and provide semantic meaning with zero boilerplate (*Effective Java, Item 62*).

```java
// Avoid: Passing raw strings that require constant validation
void process(String email, double amount) { ... }

// Good: Meaningful domain types via Records
record Email(String value) {
    public Email { Objects.requireNonNull(value); /* add regex check */ }
}
void process(Email email, Money amount) { ... }
```

### 2. Deep Nesting (Arrow Code)
**The Smell:** Multiple levels of `if`, `for`, and `while` blocks that push code far to the right.
**The Modern Cure:**
-   **Guard Clauses**: Return early to flatten the logic.
-   **Pattern Matching**: Use `switch` expressions to handle complex branching in a single flat block.
-   **Functional Pipelines**: Use `.filter()` and `.flatMap()` to process data without nested loops (*Modern Java in Action*).

### 3. High Cognitive Complexity (Method Size)
**The Smell:** Methods longer than 20–30 lines or containing high "Cyclomatic Complexity" (too many branches).
**The Modern Cure:**
-   **Extract Method**: Split logic into private helper methods.
-   **Decomposition**: If a method handles multiple steps, consider a `record` to encapsulate the intermediate state.

### 4. Over-reliance on `synchronized` (Loom Context)
**The Smell:** Frequent use of `synchronized` keywords in high-concurrency applications.
**The Modern Cure:**
-   In the age of **Virtual Threads**, `synchronized` can lead to **Pinning**.
-   Use `ReentrantLock` or `java.util.concurrent` classes (`ConcurrentHashMap`, `AtomicReference`).
-   Shift toward **Immutability** to avoid the need for locks entirely (*Java Concurrency in Practice*).

### 5. Imperative "How" instead of Functional "What"
**The Smell:** Manually managing loop counters, temporary lists, and state transformations.
**The Modern Cure:** Use **Streams**. Focus on what should be done with the data, not how to iterate over it (*Effective Java, Item 45*).

```java
// Avoid: Imperative noise
List<String> activeNames = new ArrayList<>();
for (User u : users) {
    if (u.status() == Status.ACTIVE) {
        activeNames.add(u.name());
    }
}

// Good: Declarative intent
List<String> activeNames = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();
```

### 6. The "Return Null" Habit
**The Smell:** Returning `null` to indicate an empty result or a missing value.
**The Modern Cure:**
-   **Collections**: Always return `List.of()`, `Set.of()`, or `Map.of()` instead of `null` (*Effective Java, Item 54*).
-   **Single Values**: Return `Optional<T>` to force the caller to handle the absence of a value.

### 7. Inheritance Abuse (Fragile Base Class)
**The Smell:** Using `extends` to reuse code rather than modeling a "is-a" relationship.
**The Modern Cure:**
-   **Composition over Inheritance**: Favor using interfaces and holding references to other classes (*Effective Java, Item 18*).
-   **Sealed Classes**: If you must use inheritance, use `sealed` to strictly control the hierarchy.

### 8. Unused Variables and Parameters
**The Smell:** Keeping variables, parameters, or catch-block exceptions that are never used.
**The Modern Cure (JDK 25):** Use the **Unnamed Variable (`_`)**. It explicitly signals to the reader (and the compiler) that the value is intentionally ignored, reducing clutter.

```java
// JDK 25: Explicitly ignoring an unused variable
try {
    var data = repository.fetch();
} catch (DataException _) { // No need to name the exception if not used
    log.error("Fetch failed");
}
```

---

### Comparison: Code Smell Cures (JDK 21 vs JDK 25)

| Smell | JDK 21 Cure | JDK 25 Cure |
| :--- | :--- | :--- |
| **Complexity** | Pattern Matching & Guards. | **Unnamed Patterns** to simplify complex deconstruction. |
| **Thread Leaks** | Manual `executor.shutdown()`. | **`StructuredTaskScope`** (Stable) handles lifecycle automatically. |
| **Boilerplate** | Records & Text Blocks. | **Unnamed Classes** (for simple scripts/main entries). |

---

### Rationale from Literature:
1.  **Immutability/Records**: Joshua Bloch argues that classes should be immutable unless there is a very good reason to make them mutable. Records make this the "path of least resistance."
2.  **Cognitive Complexity**: *Thinking in Java* (Eckel) emphasizes that code should be readable as a narrative. High nesting and long methods break that narrative.
3.  **Loom Migration**: *Modern Concurrency in Java* (Rahman) identifies that the biggest "smell" in legacy code moving to JDK 21+ is the assumption that threads are expensive (leading to pooling and complex reactive code). With Virtual Threads, the code should be **simple and blocking**.
4.  **Null Handling**: Horstmann’s *Core Java* highlights that `Optional` is a tool for API design, not a general-purpose "null-fixer," but it is vastly superior to returning `null` for individual items.


---

## Architecture Guidelines

### 1. Functional Domain Modeling (Algebraic Data Types)
Shift from complex class hierarchies to **Algebraic Data Types (ADTs)** using `sealed` interfaces and `record` classes. This makes the domain model explicit and ensures that business logic is exhaustive.

-   **Rule**: Use `sealed` interfaces to define a closed set of types and `records` to hold the data.
-   **Benefits**: Compiler-enforced handling of all business cases in `switch` expressions, leading to fewer "unhandled state" bugs.

```java
// Example: Modeling a Payment Domain
public sealed interface PaymentMethod permits CreditCard, PayPal, Crypto {}

public record CreditCard(String number, String vaultId) implements PaymentMethod {}
public record PayPal(String email) implements PaymentMethod {}
public record Crypto(String walletAddress, String currency) implements PaymentMethod {}
```

### 2. Concurrency: Thread-per-Task (Project Loom)
JDK 21/25 architecture favors **simplicity and blocking I/O** over complex reactive or asynchronous frameworks.

-   **Rule**: For I/O-bound services, use **Virtual Threads** to handle concurrent requests. Avoid the complexity of `Mono`/`Flux` (Project Reactor) unless you require backpressure across network boundaries.
-   **Structured Concurrency (JDK 25 Stable)**: Use `StructuredTaskScope` to treat groups of related tasks as a single unit of work. This ensures that if a parent task is cancelled, all subtasks are cleanly shut down (*Modern Concurrency in Java, 2025*).

```java
// JDK 25 Architecture: Structured Concurrency
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> user = scope.fork(userRepo::fetch);
    Subtask<Orders> orders = scope.fork(orderRepo::fetch);

    scope.join().throwIfFailed(); // Propagates errors correctly
    return new Dashboard(user.get(), orders.get());
}
```

### 3. Encapsulation and Access Control
Enforce strict boundaries to reduce the surface area of your API (*Effective Java, Item 15*).

-   **Final by Default**: Use `final` for classes unless they are designed for inheritance.
-   **Sealed for Extension**: Use `sealed` to allow extension only within the same module or package.
-   **Package-Private**: Keep implementation classes package-private; expose only interfaces or records.
-   **JPMS (Modules)**: For large systems, use `module-info.java` to explicitly define which packages are exported and which are internal.

### 4. Dependency Inversion and Composition
-   **Interface-Driven**: Depend on abstractions (interfaces) rather than implementations. This is crucial for testability and swapping I/O layers (*Effective Java, Item 64*).
-   **Favor Composition**: Build complex behavior by combining simple objects rather than creating deep inheritance chains (*Effective Java, Item 18*).

### 5. Service Layer Design
-   **Stateless Services**: Design service-layer components to be stateless to ensure they are thread-safe and easily scalable.
-   **Record DTOs**: Use records for data transfer between layers (Controller → Service → Repository). This prevents accidental mutation of data as it flows through the system.

### 6. Error Handling Strategy
-   **Predictable Failures**: For expected business failures (e.g., `UserNotFound`, `InsufficientFunds`), **prefer** using **Sealed Results** (`Result<T, E>`) instead of throwing exceptions. This makes the failure a first-class part of the API and the compiler enforces handling.
-   **Unrecoverable Failures**: Use unchecked exceptions for infrastructure or programming errors.
-   **Fallback Strategy**: When `Result<T, E>` is impractical (e.g., deep infrastructure layers, third-party API integration), use unchecked exceptions with proper cause chaining.

```java
// Architectural Pattern: Result Object
public sealed interface OrderResult {
    record Success(Order order) implements OrderResult {}
    record Failure(String reason, ErrorCode code) implements OrderResult {}
}
```

---

### Comparison: Architectural Shifts (JDK 21 vs JDK 25)

| Category | JDK 21 (LTS) Approach | JDK 25 Approach |
| :--- | :--- | :--- |
| **Concurrency** | Virtual Thread Executors (Standard). Project Reactor for complex backpressure. | **StructuredTaskScope** for task hierarchies. Simpler, thread-per-task model. |
| **Context** | `ThreadLocal` (Use with caution). | **ScopedValue** (Immutable, efficient context). |
| **Integration** | JNI (Complex, unsafe). | **Foreign Function & Memory API** (Safe, high-perf). |

---

### Rationale from Literature:
1.  **Algebraic Data Types**: *Modern Java in Action* explains that combining `sealed` and `records` provides the same safety as functional languages like Haskell or Scala, making the code "correct by construction."
2.  **Loom Architecture**: Bazlur Rahman argues in *Modern Concurrency in Java* that the "Reactive" era was a workaround for expensive threads. Virtual Threads allow us to return to the simpler "thread-per-request" model without sacrificing scalability.
3.  **Encapsulation**: Joshua Bloch (*Effective Java*) notes that every class or member should be as inaccessible as possible. `sealed` classes provide a middle ground between `public` and `final` that was missing for decades.
4.  **Immutability**: Cay Horstmann emphasizes that in a multi-threaded world (especially with thousands of virtual threads), shared mutable state is the primary enemy. Records are the architectural solution to this problem.

---

## Performance

This section details how to achieve maximum throughput and efficiency in **JDK 21** and **JDK 25**. Performance in modern Java is less about micro-optimizing loops and more about **memory locality**, **reducing contention**, and effectively leveraging **Project Loom**.

### 1. The Golden Rule: Profile Before Optimizing
Following *Effective Java (Item 67)*: "Adhere to generally accepted design principles to build a robust system, then profile it."
-   **Java Flight Recorder (JFR)**: Use `-XX:StartFlightRecording` in production. It has near-zero overhead and provides deep insights into JVM internals.
-   **JMH (Java Microbenchmark Harness)**: Never rely on `System.currentTimeMillis()` for benchmarks. Use JMH to account for JIT warm-up and dead-code elimination.

### 2. Virtual Thread Throughput vs. Latency
Virtual threads provide **high throughput**, not lower latency.
-   **Don't Pool Virtual Threads**: Creating a virtual thread is as cheap as creating a `String`. Pooling them adds unnecessary synchronization overhead.
-   **Throttling**: If you need to limit concurrency (e.g., to avoid overwhelming a database), use a `Semaphore` instead of a fixed-size `ExecutorService`.
-   **Carrier Thread Pinning**: Monitor JFR events for `jdk.VirtualThreadPinned`. Pinning occurs when a virtual thread cannot be unmounted during I/O (usually due to `synchronized`). This forces the JVM to spawn more OS threads, increasing memory pressure.

### 3. Minimize Boxing and Object Overhead
Object headers and pointers waste cache space. *Modern Java in Action* and *Effective Java (Item 61)* warn against the performance tax of wrappers.
-   **Primitive Streams**: Use `IntStream`, `LongStream`, and `DoubleStream` to avoid boxing `int` to `Integer`.
-   **Records for Data**: Use Records and immutable collections (`List.of()`, `Map.of()`) which have better memory locality and are more cache-efficient than their mutable counterparts.

```java
// Avoid: Boxes 1 million integers
List<Integer> list = IntStream.range(0, 1_000_000).boxed().toList();

// Good: Keeps data in primitive arrays
int[] array = IntStream.range(0, 1_000_000).toArray();
```

### 4. Efficient Collection Usage
-   **Initial Capacity**: Always specify initial capacity for `ArrayList` or `HashMap` if the size is known, avoiding expensive resizing/rehashing.
-   **Sequenced Collections (JDK 21+)**: Use `getFirst()`/`getLast()`. For `LinkedList`, these are $O(1)$ at the boundaries, but remember that for random access, `ArrayList` is almost always faster due to CPU cache efficiency.
-   **Immutability**: `List.of()` and `Map.of()` are not just for safety; they are more memory-efficient than their mutable counterparts.

### 5. String Manipulation
-   **Concatenation**: Use `StringBuilder` only inside loops. For simple multi-part strings, the `+` operator is optimized by the compiler using `StringConcatFactory` (*Core Java, Vol I*).
-   **Text Blocks**: Use Text Blocks for large multiline strings; they are processed at compile-time and do not add runtime overhead.
-   **Compact Strings**: Be aware that Java internally uses `byte[]` instead of `char[]` for Latin-1 strings, reducing heap usage by 50% for most text.

### 6. Foreign Function & Memory API (JDK 22+ / 25 Stable)
If your application handles massive datasets or interacts with native libraries (C/C++):
-   **Move away from JNI**: Use **Project Panama** (`java.lang.foreign`). It provides safer and significantly faster access to off-heap memory, bypassing GC overhead for large buffers.

### 7. Modern GC Selection
-   **G1GC**: The reliable default for most applications.
-   **ZGC (Generational)**: Use `-XX:+UseZGC -XX:+ZGenerational` (fully stable in JDK 21+). It maintains sub-millisecond pause times even with multi-terabyte heaps, making it ideal for low-latency virtual thread applications.

---

### Comparison: Performance Features (JDK 21 vs JDK 25)

| Feature | JDK 21 (LTS) Status | JDK 25 Status |
| :--- | :--- | :--- |
| **Virtual Threads** | Stable. Requires `synchronized` awareness. | More resilient; better JFR tooling for pinning. |
| **Off-heap Memory** | Foreign Linker/Memory (Preview). | **Project Panama** (Stable/Final). |
| **String Handling** | Text Blocks (JEP 378, Stable). | Text Blocks + enhanced `.formatted()` methods. |

---

### Rationale from Literature:
1.  **Effective Java (Item 67)**: Bloch reminds us that "fast" is often the enemy of "correct." Focus on clean architecture (Records, Interfaces) first; the JIT compiler is excellent at optimizing well-structured code.
2.  **Java Concurrency in Practice**: Goetz highlights that **contention** (many threads fighting for one lock) is the biggest performance killer. Virtual threads amplify this; hence the move toward `ReentrantLock` and Scoped Values.
3.  **Modern Concurrency in Java (2025)**: Bazlur Rahman emphasizes that because virtual threads are so numerous, the memory used by `ThreadLocal` variables can quickly crash a heap. **Scoped Values** (JDK 25) solve this performance bottleneck.
4.  **Core Java (Horstmann)**: Emphasizes that the move toward `Stream.toList()` and immutable collections allows the JVM to make assumptions that lead to better JIT optimizations.



---

## Testing Standards

### 1. Modern Tooling Stack
-   **Test Framework**: **JUnit 5** (Jupiter). Utilize `@ParameterizedTest`, `@Nested`, and `@DisplayName`.
-   **Assertions**: **AssertJ**. Use fluent assertions for readability. Avoid `junit.jupiter.api.Assertions`.
-   **Mocking**: **Mockito**. Use `@Mock` and `@InjectMocks` with the `MockitoExtension`.
-   **Concurrency Testing**: Use **Awaitility** for testing asynchronous or virtual-thread-based logic.

### 2. Naming and Structure: AAA Pattern
Follow the **Arrange-Act-Assert (AAA)** pattern to ensure tests are self-documenting.
-   **Naming**: `methodName_Scenario_ExpectedBehavior` (e.g., `withdraw_InsufficientFunds_ThrowsException`).
-   **Isolation**: Tests must not share mutable state. Use `@BeforeEach` to reset data.
-   **Readability**: Use `@DisplayName` to describe the business requirement in plain English.

### 3. Testing Records and Sealed Classes
-   **Records**: Do not test auto-generated methods (`equals`, `hashCode`, `toString`) unless you have provided a custom implementation (*Effective Java, Item 10*). Focus on **compact constructor validation**.
-   **Sealed Classes**: Use `switch` expressions in tests to ensure all permitted subtypes are covered.

```java
// Testing a Record's invariants
@Test
void constructor_NegativeAmount_ThrowsException() {
    assertThatThrownBy(() -> new Money(new BigDecimal("-1.00"), "USD"))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("cannot be negative");
}
```

### 4. Testing Concurrency (Project Loom)
Testing **Virtual Threads** requires shifting from "thread-blocking" tests to "throughput/logical" tests.
-   **Virtual Thread Execution**: Use `Executors.newVirtualThreadPerTaskExecutor()` in tests to ensure logic works under Loom.
-   **Avoid Fixed Delays**: Never use `Thread.sleep()`. Use **Awaitility** to poll for conditions.
-   **Timeout Handling**: Always wrap concurrent tests in a `assertTimeoutPreemptively` or use the JUnit 5 `@Timeout` annotation to prevent hanging builds.

```java
@Test
void asyncTask_CompletesSuccessfully_WithVirtualThreads() {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        var future = executor.submit(() -> "Done");

        // Use Awaitility for non-blocking verification
        await().atMost(Duration.ofSeconds(2))
               .untilAsserted(() -> assertThat(future.get()).isEqualTo("Done"));
    }
}
```

### 5. Fluent Assertions with AssertJ
Maximize the use of AssertJ’s domain-specific assertions to improve failure messages.
-   **Collections**: Use `containsExactly()`, `hasSize()`, or `allSatisfy()`.
-   **Optionals**: Use `isPresent()`, `contains()`, or `isEmpty()`.
-   **Exceptions**: Use `assertThatThrownBy()` and verify the cause chain.

### 6. Parameterized Testing
Avoid duplicated test logic by using `@ParameterizedTest`. This is the preferred way to test boundary conditions (Effective Java, Item 42).

```java
@ParameterizedTest
@CsvSource({
    "10, 2, 5",
    "20, 4, 5",
    "100, 10, 10"
})
void divide_ValidInputs_ReturnsExpected(int a, int b, int expected) {
    assertThat(calculator.divide(a, b)).isEqualTo(expected);
}
```

### 7. Structured Concurrency Testing (JDK 25)
When testing logic using `StructuredTaskScope`, verify that failures in subtasks propagate correctly and that the scope closes as expected.

```java
// JDK 25: Testing StructuredTaskScope
@Test
void fetchDetails_SubtaskFails_ThrowsExecutionException() {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        scope.fork(() -> { throw new RuntimeException("Fail"); });

        assertThatThrownBy(() -> scope.join().throwIfFailed())
            .isInstanceOf(ExecutionException.class);
    }
}
```

---

### Comparison: Testing Evolution (JDK 21 vs JDK 25)

| Feature | JDK 21 (LTS) Strategy | JDK 25 Strategy |
| :--- | :--- | :--- |
| **Mocking** | Standard Mockito. | Mockito works natively with Virtual Threads. |
| **Async Tests** | `CompletableFuture` + `join()`. | **`StructuredTaskScope`** (Stable) for simpler lifecycle tests. |
| **Data Setup** | Records as DTOs. | **Unnamed Variables (`_`)** in tests to ignore irrelevant components. |
| **Timeout** | `@Timeout` annotation. | Better `StructuredTaskScope` timeout integration. |

---

### Common Issues & Solutions

| Issue | Solution | Pattern |
| :--- | :--- | :--- |
| **Carrier Thread Pinning** | Avoid `synchronized` for I/O | Use `ReentrantLock` |
| **Expensive Resizing** | Pre-size Collections | `new ArrayList<>(expectedSize)` |
| **Leaky Context** | Replace `ThreadLocal` | Use `ScopedValue` (JDK 25) |
| **Boolean Hell** | Use Enum/Sealed types | `switch(status)` |
| **Deep Inheritance** | Favor Composition | Use private fields + Interface delegation |

---

### Rationale from Literature:
1.  **Effective Java (Item 10-12)**: Bloch notes that manual `equals/hashCode` are a frequent source of bugs. By using Records and trusting the compiler, we shift testing focus to **Business Logic**.
2.  **Core Java (Horstmann)**: Emphasizes that unit tests should be "fast and repeatable." Virtual Threads make it possible to run thousands of "concurrent" tests in milliseconds without the overhead of platform thread pools.
3.  **Modern Concurrency in Java (Rahman)**: Argues that testing for **Pinning** should be part of the performance suite using JFR, while unit tests focus on the functional correctness of the virtual threads.
4.  **JUnit 5 User Guide**: Recommends `@Nested` tests to group behavior by state (e.g., `WhenAccountIsLocked`, `WhenBalanceIsZero`), creating a specification-like test suite.

---

## Build and Verification

After adding or modifying code, verify the project continues to build and all tests pass.

| Build Tool | Command |
|---|---|
| Maven | `mvn clean install` |
| Gradle (macOS/Linux) | `./gradlew build` |
| Gradle (Windows) | `gradlew.bat build` |
| SonarScanner | `sonar-scanner -Dsonar.projectKey=<key>` |

Ensure the project declares `<java.version>21</java.version>` (Maven) or `sourceCompatibility = JavaVersion.VERSION_21` (Gradle). A green build with failing static analysis is not acceptable for merge.

---


## Additional Resources

- [JDK 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [JEP 444 — Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 441 — Pattern Matching for switch](https://openjdk.org/jeps/441)
- [JEP 431 — Sequenced Collections](https://openjdk.org/jeps/431)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Effective Java, 3rd Edition — Joshua Bloch](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [AssertJ Documentation](https://assertj.github.io/doc/)
- [SonarQube Java Rules](https://rules.sonarsource.com/java/)
