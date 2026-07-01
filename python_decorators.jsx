import { useState } from "react";

const sections = [
  {
    id: "s1",
    title: "01 — What IS a Decorator?",
    subtitle: "Functions are first-class objects",
    color: "#ff6b35",
    content: `# The Core Idea
A decorator is just a **function that takes a function and returns a (usually modified) function**.
That's it. Everything else is built on this.

Python functions are "first-class objects" — they can be:
- Passed as arguments
- Returned from functions
- Assigned to variables`,
    code: `# Functions are objects — assign them to variables
def greet():
    return "Hello, World!"

say_hi = greet          # No parentheses — we're passing the function itself
print(say_hi())         # Hello, World!

# Pass a function as an argument
def run_twice(func):
    func()
    func()

def wink():
    print("😉")

run_twice(wink)
# 😉
# 😉

# Return a function from a function
def get_multiplier(n):
    def multiplier(x):
        return x * n          # 'n' is captured from the outer scope
    return multiplier         # return the inner function itself

double = get_multiplier(2)
triple = get_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15`,
  },
  {
    id: "s2",
    title: "02 — Building a Decorator by Hand",
    subtitle: "The wrapper pattern",
    color: "#7c3aed",
    content: `# The Wrapper Pattern
A decorator wraps a function inside another function (called a **wrapper**).
The wrapper runs extra code *before* and/or *after* the original function.

This is the fundamental decorator skeleton — memorize this shape.`,
    code: `# The canonical decorator skeleton
def my_decorator(func):          # 1. Accept a function
    def wrapper(*args, **kwargs): # 2. Define a wrapper
        print("Before the call")
        result = func(*args, **kwargs)  # 3. Call the original
        print("After the call")
        return result            # 4. Return its result
    return wrapper               # 5. Return the wrapper

# Apply manually (no @ syntax yet)
def add(a, b):
    return a + b

decorated_add = my_decorator(add)
print(decorated_add(3, 4))
# Before the call
# After the call
# 7

# *args, **kwargs lets the wrapper handle ANY function signature
def greet(name, excited=False):
    msg = f"Hello, {name}"
    return msg + "!" if excited else msg

decorated_greet = my_decorator(greet)
decorated_greet("Alice", excited=True)
# Before the call
# After the call`,
  },
  {
    id: "s3",
    title: "03 — The @ Syntax",
    subtitle: "Syntactic sugar for decoration",
    color: "#0891b2",
    content: `# @ is Just Shorthand
\`@decorator\` above a function is **exactly** equivalent to:
\`func = decorator(func)\`

Python applies the decorator at *definition time*, not at call time.
This is pure syntactic sugar — the two forms are identical.`,
    code: `# Without @ syntax
def bold(func):
    def wrapper(*args, **kwargs):
        return "<b>" + func(*args, **kwargs) + "</b>"
    return wrapper

def greet(name):
    return f"Hello, {name}"

greet = bold(greet)          # manual decoration
print(greet("Alice"))        # <b>Hello, Alice</b>

# ─────────────────────────────────────────────

# WITH @ syntax — same thing, cleaner!
def bold(func):
    def wrapper(*args, **kwargs):
        return "<b>" + func(*args, **kwargs) + "</b>"
    return wrapper

@bold                        # equivalent to: greet = bold(greet)
def greet(name):
    return f"Hello, {name}"

print(greet("Alice"))        # <b>Hello, Alice</b>

# ─────────────────────────────────────────────

# A timer decorator using @ syntax
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_square(n):
    time.sleep(0.1)
    return n * n

print(slow_square(9))
# slow_square took 0.1001s
# 81`,
  },
  {
    id: "s4",
    title: "04 — functools.wraps",
    subtitle: "Preserving identity",
    color: "#059669",
    content: `# The Identity Problem
When you wrap a function, you *replace* it with the wrapper.
This breaks introspection: \`__name__\`, \`__doc__\`, \`help()\` all show wrapper's info instead.

**Always use \`@functools.wraps(func)\`** inside your decorator.
It copies the original function's metadata onto the wrapper.`,
    code: `import functools

# WITHOUT @wraps — broken metadata
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def calculate(x):
    """Multiply x by 2."""
    return x * 2

print(calculate.__name__)   # wrapper   ← WRONG
print(calculate.__doc__)    # None      ← WRONG

# ─────────────────────────────────────────────

# WITH @wraps — metadata preserved ✓
def good_decorator(func):
    @functools.wraps(func)       # ← this line fixes everything
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def calculate(x):
    """Multiply x by 2."""
    return x * 2

print(calculate.__name__)   # calculate ✓
print(calculate.__doc__)    # Multiply x by 2. ✓

# This matters for:
# - Debugging (tracebacks show the right name)
# - Docs generation (Sphinx, pydoc)
# - Testing frameworks
# - Any code that inspects function metadata`,
  },
  {
    id: "s5",
    title: "05 — Decorators with Arguments",
    subtitle: "The factory pattern",
    color: "#d97706",
    content: `# Parameterized Decorators
Sometimes you need to configure a decorator, e.g. \`@retry(times=3)\`.
The trick: add **one more layer of nesting** — a factory function that
*returns* a decorator.

\`@retry(times=3)\` means: call \`retry(times=3)\` first (returns a decorator),
then apply *that* decorator to the function.`,
    code: `import functools

# A decorator factory — returns a decorator
def repeat(times):               # outer: accepts config
    def decorator(func):         # middle: accepts function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # inner: does the work
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator             # return the real decorator

@repeat(times=3)
def say(message):
    print(message)

say("Hello!")
# Hello!
# Hello!
# Hello!

# ─────────────────────────────────────────────

# Retry decorator with configurable attempts
def retry(max_attempts=3, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3, exceptions=(ValueError,))
def risky_parse(data):
    return int(data)   # raises ValueError for bad input`,
  },
  {
    id: "s6",
    title: "06 — Class-Based Decorators",
    subtitle: "Using __call__ for stateful decoration",
    color: "#db2777",
    content: `# Decorators as Classes
Any callable works as a decorator — including class instances.
Use \`__call__\` to make the instance callable.

Class decorators are great when you need **state** (e.g., call counts,
caches, rate limiters) because classes manage state naturally.`,
    code: `import functools

# A class-based call counter
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)  # preserve metadata
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"Call #{self.call_count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def add(a, b):
    return a + b

add(1, 2)   # Call #1 to add
add(3, 4)   # Call #2 to add
add(5, 6)   # Call #3 to add
print(add.call_count)   # 3  ← state lives on the instance!

# ─────────────────────────────────────────────

# A simple cache using a class
class Memoize:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if args not in self.cache:
            self.cache[args] = self.func(*args)
        return self.cache[args]

@Memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))   # 55  (computed efficiently with caching)`,
  },
  {
    id: "s7",
    title: "07 — Stacking Multiple Decorators",
    subtitle: "Order matters — bottom up, then top down",
    color: "#dc2626",
    content: `# Stacking Order
Multiple decorators are applied **bottom-up** at definition time,
but they execute **top-down** at call time.

\`\`\`
@A        →  func = A(B(C(D(func))))
@B
@C
@D
def func(): ...
\`\`\`

Think of it like wrapping gifts: innermost wrapper goes on first.
When you open (call) it, you remove the outermost layer first.`,
    code: `import functools, time, logging

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s: %(message)s")

# ── 5 reusable decorators ─────────────────────

def log_call(func):
    """Logs every call with its arguments."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper

def timer(func):
    """Measures execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} took {time.perf_counter()-t0:.4f}s")
        return result
    return wrapper

def validate_positive(func):
    """Ensures all numeric args are > 0."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg <= 0:
                raise ValueError(f"Expected positive number, got {arg}")
        return func(*args, **kwargs)
    return wrapper

def retry(times=3):
    """Retries on exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Retry {attempt}/{times}: {e}")
                    if attempt == times: raise
        return wrapper
    return decorator

def cache_result(func):
    """Caches results in a dict."""
    _cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in _cache:
            _cache[args] = func(*args)
            logging.info(f"Cache MISS for {args}")
        else:
            logging.info(f"Cache HIT  for {args}")
        return _cache[args]
    return wrapper

# ── Stack all 5 on one function ───────────────

@log_call           # ← outermost: runs FIRST on call
@timer              # ← runs second
@validate_positive  # ← validates before hitting cache
@retry(times=2)     # ← retries if anything below fails
@cache_result       # ← innermost: closest to real function
def compute(x, y):
    """Returns x raised to the power of y."""
    return x ** y

# Definition expanded to:
# compute = log_call(timer(validate_positive(retry(2)(cache_result(compute)))))

compute(2, 10)   # Cache MISS → computes 1024
compute(2, 10)   # Cache HIT  → returns 1024 instantly
compute(3, 5)    # Cache MISS → computes 243

# The name is preserved thanks to @functools.wraps
print(compute.__name__)   # compute
print(compute.__doc__)    # Returns x raised to the power of y.`,
  },
  {
    id: "s8",
    title: "08 — stdlib Decorators",
    subtitle: "Battle-tested decorators in the standard library",
    color: "#4f46e5",
    content: `# Python's Built-in Decorators
The standard library ships several production-ready decorators you should know.
These cover the most common use-cases: caching, properties, class methods.`,
    code: `from functools import lru_cache, cached_property, wraps
from dataclasses import dataclass

# ── @lru_cache — memoization with LRU eviction ─

@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

print(fib(50))          # 12586269025 (instant!)
print(fib.cache_info()) # CacheInfo(hits=48, misses=51, ...)

# ── @property — computed attribute ─────────────

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):                  # accessed as c.area, not c.area()
        return 3.14159 * self._radius ** 2

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be non-negative")
        self._radius = value

c = Circle(5)
print(c.area)     # 78.53975  — no () needed
c.radius = 10
print(c.area)     # 314.159

# ── @staticmethod and @classmethod ─────────────

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @staticmethod
    def validate(value):             # no self, no cls — pure function
        return isinstance(value, (int, float))

    @classmethod
    def from_fahrenheit(cls, f):     # receives the class, not instance
        return cls((f - 32) * 5 / 9)

t = Temperature.from_fahrenheit(212)
print(t.celsius)                     # 100.0
print(Temperature.validate(37.5))    # True

# ── @cached_property — compute once, cache forever ─

class DataProcessor:
    def __init__(self, data):
        self.data = data

    @cached_property
    def summary(self):               # computed once on first access
        print("Computing...")
        return {"count": len(self.data), "sum": sum(self.data)}

dp = DataProcessor([1,2,3,4,5])
print(dp.summary)  # Computing... {'count': 5, 'sum': 15}
print(dp.summary)  # {'count': 5, 'sum': 15}  ← cached, no print`,
  },
];

const CodeBlock = ({ code }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };
  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={handleCopy}
        style={{
          position: "absolute",
          top: 12,
          right: 12,
          background: copied ? "#16a34a" : "rgba(255,255,255,0.08)",
          border: "1px solid rgba(255,255,255,0.15)",
          color: copied ? "#fff" : "#94a3b8",
          borderRadius: 6,
          padding: "4px 12px",
          fontSize: 11,
          fontFamily: "'JetBrains Mono', monospace",
          cursor: "pointer",
          transition: "all 0.2s",
          letterSpacing: "0.05em",
          zIndex: 2,
        }}
      >
        {copied ? "✓ copied" : "copy"}
      </button>
      <pre
        style={{
          background: "#0d1117",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 12,
          padding: "20px 20px 20px 20px",
          overflowX: "auto",
          margin: 0,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontSize: 13,
          lineHeight: 1.7,
          color: "#e2e8f0",
        }}
      >
        <code>{colorize(code)}</code>
      </pre>
    </div>
  );
};

function colorize(code) {
  const lines = code.split("\n");
  return lines.map((line, i) => {
    const isComment = line.trim().startsWith("#");
    const isDecorator = line.trim().startsWith("@");
    const isDef = /^\s*(def |class )/.test(line);
    let color = "#e2e8f0";
    if (isComment) color = "#6b7280";
    else if (isDecorator) color = "#f59e0b";
    else if (isDef) color = "#93c5fd";
    return (
      <span key={i} style={{ color, display: "block" }}>
        {line || " "}
      </span>
    );
  });
}

const MarkdownContent = ({ text }) => {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return (
    <p style={{ color: "#94a3b8", lineHeight: 1.8, margin: "0 0 16px 0", fontSize: 15 }}>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**"))
          return <strong key={i} style={{ color: "#e2e8f0", fontWeight: 600 }}>{part.slice(2, -2)}</strong>;
        if (part.startsWith("`") && part.endsWith("`"))
          return <code key={i} style={{ background: "#1e2938", color: "#f59e0b", padding: "1px 6px", borderRadius: 4, fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}>{part.slice(1, -1)}</code>;
        return <span key={i}>{part}</span>;
      })}
    </p>
  );
};

const parseContent = (content) => {
  const lines = content.split("\n").filter(l => l.trim());
  const result = [];
  let currentBlock = [];
  
  lines.forEach(line => {
    if (line.startsWith("# ")) {
      if (currentBlock.length) result.push({ type: "text", lines: currentBlock });
      result.push({ type: "heading", text: line.slice(2) });
      currentBlock = [];
    } else if (line.trim()) {
      currentBlock.push(line);
    }
  });
  if (currentBlock.length) result.push({ type: "text", lines: currentBlock });
  return result;
};

export default function PythonDecorators() {
  const [active, setActive] = useState("s1");
  const section = sections.find(s => s.id === active);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#070d19",
      fontFamily: "'Inter', system-ui, sans-serif",
      display: "flex",
      flexDirection: "column",
    }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "28px 32px 24px",
        background: "linear-gradient(180deg, #0a1628 0%, #070d19 100%)",
      }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 6 }}>
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            color: "#f59e0b",
            fontSize: 12,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
          }}>Python</span>
          <span style={{ color: "rgba(255,255,255,0.12)", fontSize: 12 }}>—</span>
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            color: "rgba(255,255,255,0.3)",
            fontSize: 12,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
          }}>Deep Dive</span>
        </div>
        <h1 style={{
          color: "#fff",
          fontSize: 28,
          fontWeight: 700,
          margin: 0,
          letterSpacing: "-0.02em",
        }}>
          Decorators
        </h1>
        <p style={{ color: "#475569", margin: "6px 0 0", fontSize: 14 }}>
          From first principles to stacking 5 decorators on a single function
        </p>
      </div>

      {/* Nav tabs */}
      <div style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "0 24px",
        display: "flex",
        gap: 4,
        overflowX: "auto",
        background: "#070d19",
      }}>
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => setActive(s.id)}
            style={{
              background: "none",
              border: "none",
              borderBottom: active === s.id ? `2px solid ${s.color}` : "2px solid transparent",
              color: active === s.id ? "#fff" : "#475569",
              padding: "12px 14px",
              cursor: "pointer",
              fontSize: 12,
              fontFamily: "'JetBrains Mono', monospace",
              whiteSpace: "nowrap",
              transition: "all 0.15s",
              letterSpacing: "0.03em",
            }}
          >
            {s.id}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, padding: "28px 28px", maxWidth: 900, width: "100%", margin: "0 auto", boxSizing: "border-box" }}>
        {/* Section header */}
        <div style={{ marginBottom: 28 }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            marginBottom: 10,
          }}>
            <span style={{
              width: 10, height: 10, borderRadius: "50%",
              background: section.color,
              display: "inline-block",
              boxShadow: `0 0 12px ${section.color}88`,
            }} />
            <span style={{
              fontFamily: "'JetBrains Mono', monospace",
              color: section.color,
              fontSize: 12,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}>{section.subtitle}</span>
          </div>
          <h2 style={{
            color: "#fff",
            fontSize: 24,
            fontWeight: 700,
            margin: 0,
            letterSpacing: "-0.02em",
          }}>{section.title}</h2>
        </div>

        {/* Text content */}
        <div style={{
          background: "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.06)",
          borderRadius: 12,
          padding: "20px 24px",
          marginBottom: 20,
        }}>
          {parseContent(section.content).map((block, i) => {
            if (block.type === "heading") return (
              <h3 key={i} style={{
                color: "#e2e8f0",
                fontSize: 15,
                fontWeight: 600,
                margin: i === 0 ? "0 0 12px 0" : "20px 0 12px 0",
                letterSpacing: "-0.01em",
              }}>{block.text}</h3>
            );
            return block.lines.map((line, j) => {
              if (line.startsWith("- ")) {
                return (
                  <div key={`${i}-${j}`} style={{ display: "flex", gap: 10, marginBottom: 6 }}>
                    <span style={{ color: section.color, flexShrink: 0, marginTop: 2 }}>▸</span>
                    <MarkdownContent text={line.slice(2)} />
                  </div>
                );
              }
              return <MarkdownContent key={`${i}-${j}`} text={line} />;
            });
          })}
        </div>

        {/* Code block */}
        <CodeBlock code={section.code} />

        {/* Navigation */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: 28,
          gap: 12,
        }}>
          {sections.findIndex(s => s.id === active) > 0 ? (
            <button
              onClick={() => setActive(sections[sections.findIndex(s => s.id === active) - 1].id)}
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.1)",
                color: "#94a3b8",
                borderRadius: 8,
                padding: "10px 20px",
                cursor: "pointer",
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                transition: "all 0.15s",
              }}
            >← prev</button>
          ) : <span />}
          {sections.findIndex(s => s.id === active) < sections.length - 1 && (
            <button
              onClick={() => setActive(sections[sections.findIndex(s => s.id === active) + 1].id)}
              style={{
                background: section.color,
                border: "none",
                color: "#fff",
                borderRadius: 8,
                padding: "10px 24px",
                cursor: "pointer",
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                fontWeight: 600,
                transition: "all 0.15s",
                boxShadow: `0 0 20px ${section.color}44`,
              }}
            >next →</button>
          )}
        </div>
      </div>
    </div>
  );
}
