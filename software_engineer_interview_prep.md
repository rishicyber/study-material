# Mid-Level Software Engineer Interview Prep
### Comprehensive Question & Answer Guide (3–6 Years Experience)

---

## Table of Contents
1. [Data Structures & Algorithms](#1-data-structures--algorithms)
2. [System Design (Mid-Level Scope)](#2-system-design-mid-level-scope)
3. [Object-Oriented Design & Programming Concepts](#3-object-oriented-design--programming-concepts)
4. [Databases & SQL](#4-databases--sql)
5. [APIs, Web & Networking](#5-apis-web--networking)
6. [Testing, Debugging & Code Quality](#6-testing-debugging--code-quality)
7. [Behavioral Questions (STAR Method)](#7-behavioral-questions-star-method)
8. [Questions to Ask Your Interviewer](#8-questions-to-ask-your-interviewer)
9. [Interview Day Checklist](#9-interview-day-checklist)

---

## 1. Data Structures & Algorithms

### Q1: When would you use a hash map vs. a balanced binary search tree (e.g., a TreeMap)?
**A:** A hash map gives average O(1) lookup, insert, and delete, but no ordering guarantee and no efficient range queries. A balanced BST (like a Red-Black tree) gives O(log n) for the same operations but maintains sorted order, so it supports range queries, "find nearest," and ordered iteration efficiently. Use a hash map when you only need fast key-based access; use a BST-backed structure when order or range operations matter.

### Q2: Explain the time and space complexity trade-offs between an array and a linked list.
**A:**
- **Array:** O(1) random access, cache-friendly (contiguous memory), but O(n) insertion/deletion in the middle and resizing costs when it grows past capacity.
- **Linked list:** O(1) insertion/deletion at a known node, but O(n) access time and poor cache locality due to scattered memory allocation, plus extra memory overhead for pointers.
- Choose arrays when you need fast random access and mostly append/read; choose linked lists when you have frequent insertions/deletions and don't need random access.

### Q3: How would you detect a cycle in a linked list?
**A:** Use Floyd's Cycle Detection (tortoise and hare): two pointers, one moving one step at a time, the other two steps. If there's a cycle, they will eventually meet. This runs in O(n) time and O(1) space, compared to a hash-set approach which is O(n) time but O(n) space.

### Q4: Walk through how you'd approach a problem like "find the k most frequent elements in an array."
**A:** First count frequencies with a hash map — O(n). Then, instead of fully sorting (O(n log n)), use a min-heap of size k, pushing each unique element and popping when the heap exceeds size k — O(n log k). For very large inputs where k is close to n, a bucket-sort approach (bucket index = frequency) achieves O(n). I'd clarify constraints (size of input, memory limits) before picking the approach, and start with the heap solution since it's a solid general-purpose answer.

### Q5: What's the difference between BFS and DFS, and when would you pick one over the other?
**A:** BFS explores level by level using a queue — ideal for finding the shortest path in an unweighted graph. DFS explores as deep as possible using a stack (or recursion) — better for exploring all paths, detecting cycles, or when memory is a concern for wide (but not deep) graphs, since its memory footprint is proportional to depth rather than breadth.

### Q6: How do you approach an unfamiliar coding problem in an interview?
**A:** I restate the problem in my own words, clarify edge cases and constraints (input size, duplicates, negative numbers), work through a small example by hand, then think out loud about brute-force first before optimizing. I mention time/space complexity at each stage, code incrementally, and test with edge cases (empty input, single element, duplicates) before declaring it done.

---

## 2. System Design (Mid-Level Scope)

> At mid-level, interviewers usually expect you to design a well-scoped component (not a full distributed system from scratch) and reason clearly about trade-offs.

### Q7: Design a URL shortener (e.g., bit.ly). Walk through your approach.
**A:**
1. **Clarify requirements:** Read-heavy or write-heavy? Custom aliases? Expiration? Analytics needed?
2. **Core flow:** `POST /shorten` takes a long URL, generates a short code, stores the mapping, returns the short URL. `GET /:code` looks up and redirects (301/302).
3. **ID generation:** Base62 encode an auto-incrementing ID, or use a hash of the URL with collision handling.
4. **Storage:** A key-value store (e.g., DynamoDB or Redis-backed) works well since lookups are by key.
5. **Scaling:** Since reads vastly outnumber writes, add a caching layer (Redis) in front of the database, and consider a CDN for redirect responses.
6. **Trade-offs:** Discuss consistency (is it okay if a newly created link takes a moment to propagate?) and how to handle custom aliases or collisions.

### Q8: How would you design a rate limiter for an API?
**A:** I'd discuss algorithm choices: **fixed window** (simple but bursty at boundaries), **sliding window log** (accurate but memory-heavy), **sliding window counter** (good balance), and **token bucket** (allows bursts up to a cap, smooths average rate). For a distributed system, I'd store counters in Redis with atomic increment + expiry (`INCR` + `EXPIRE`) to keep it consistent across multiple API servers. I'd also cover what happens when the limit is hit — return `429 Too Many Requests` with a `Retry-After` header.

### Q9: What's the difference between vertical and horizontal scaling, and how do you decide between them?
**A:** Vertical scaling adds more resources (CPU/RAM) to a single machine — simple but has a hard ceiling and creates a single point of failure. Horizontal scaling adds more machines and distributes load — more complex (needs load balancing, statelessness, data partitioning) but scales further and improves fault tolerance. In practice, most systems scale vertically first for simplicity, then move to horizontal scaling once they hit resource limits or need higher availability.

### Q10: How do you approach caching, and what are the common pitfalls?
**A:** I'd identify what's expensive to compute or fetch and cache that, choosing a TTL based on how stale data can tolerably be. Common strategies: cache-aside (app checks cache, falls back to DB, then populates cache), write-through, and write-behind. Pitfalls include **cache stampede** (many requests miss simultaneously and hammer the DB — mitigated with locks or request coalescing), **stale data** if invalidation isn't handled carefully, and **cache inconsistency** across multiple cache nodes.

---

## 3. Object-Oriented Design & Programming Concepts

### Q11: Explain SOLID principles with a practical example.
**A:**
- **S**ingle Responsibility: A class should have one reason to change (e.g., separate `OrderValidator` from `OrderRepository`).
- **O**pen/Closed: Open for extension, closed for modification — use interfaces/strategy pattern instead of editing existing code for new behavior.
- **L**iskov Substitution: Subclasses should be substitutable for their base class without breaking behavior.
- **I**nterface Segregation: Prefer many small, specific interfaces over one large one.
- **D**ependency Inversion: Depend on abstractions, not concrete implementations (e.g., inject a `PaymentGateway` interface rather than a concrete `StripeClient`).

I'd give a concrete example, like refactoring a `ReportGenerator` class that both fetches data and formats output into two classes to follow SRP.

### Q12: What's the difference between composition and inheritance, and when do you prefer one?
**A:** Inheritance models an "is-a" relationship and can lead to tight coupling and fragile hierarchies if overused. Composition models a "has-a" relationship — you build behavior by combining smaller objects, which is more flexible and easier to change at runtime. The general guideline is "favor composition over inheritance" unless there's a clear, stable hierarchy (e.g., `Shape -> Circle, Square`).

### Q13: Explain the difference between concurrency and parallelism.
**A:** Concurrency is about structuring a program to handle multiple tasks that may be in progress at the same time (interleaved, not necessarily simultaneous) — useful for I/O-bound work. Parallelism is about actually executing multiple computations at the same time, typically on multiple CPU cores — useful for CPU-bound work. A single-core machine can be concurrent but not parallel.

### Q14: What causes race conditions, and how do you prevent them?
**A:** Race conditions happen when multiple threads access shared mutable state without proper synchronization, and the outcome depends on timing. Prevention strategies: locks/mutexes, atomic operations, immutable data structures, thread-confinement (each thread owns its own data), or higher-level concurrency primitives (e.g., concurrent queues, actor models). I'd also mention the trade-off — locks prevent races but can introduce deadlocks or contention, so minimizing shared state is often the better long-term fix.

### Q15: What's the difference between an abstract class and an interface?
**A:** An abstract class can have shared implementation and state, and a class can only extend one. An interface (in most languages) defines a contract with no implementation (or default methods in some languages) and a class can implement multiple interfaces. Use an abstract class when subclasses share common behavior; use an interface when you just need to guarantee a set of capabilities across unrelated classes.

---

## 4. Databases & SQL

### Q16: What's the difference between SQL and NoSQL databases, and how do you choose?
**A:** SQL databases (Postgres, MySQL) enforce a fixed schema, support ACID transactions, and are strong for relational data with complex queries/joins. NoSQL databases (MongoDB, DynamoDB, Cassandra) offer flexible schemas and horizontal scalability, trading off strict consistency (often eventual consistency) for availability and partition tolerance. I'd choose SQL when data integrity and relationships matter (e.g., financial transactions) and NoSQL when I need massive scale, flexible schema, or very high write throughput (e.g., activity logs, session data).

### Q17: Explain database indexing — how does it work and what's the trade-off?
**A:** An index is typically a B-tree (or hash structure) built on one or more columns that allows the database to find rows without scanning the whole table, turning O(n) lookups into roughly O(log n). The trade-off is that indexes speed up reads but slow down writes (every insert/update/delete must also update the index) and consume additional storage. I'd index columns used frequently in `WHERE`, `JOIN`, and `ORDER BY` clauses, but avoid over-indexing tables with heavy write loads.

### Q18: What are ACID properties?
**A:**
- **Atomicity:** A transaction either fully completes or fully rolls back.
- **Consistency:** A transaction brings the database from one valid state to another, respecting constraints.
- **Isolation:** Concurrent transactions don't interfere with each other (governed by isolation levels like Read Committed, Repeatable Read, Serializable).
- **Durability:** Once committed, data survives crashes/failures.

### Q19: How would you optimize a slow SQL query?
**A:** I'd start by running `EXPLAIN ANALYZE` to see the query plan and identify full table scans or missing indexes. Common fixes: add an index on filtered/joined columns, avoid `SELECT *`, rewrite correlated subqueries as joins, ensure the query isn't doing implicit type conversions that block index use, and check whether the table needs partitioning if it's very large. I'd also verify whether the slowness is from the query itself or from lock contention/connection pool exhaustion.

### Q20: What's a database transaction isolation level trade-off you should know?
**A:** Higher isolation levels (like Serializable) prevent anomalies (dirty reads, non-repeatable reads, phantom reads) but reduce concurrency and throughput because they require more locking. Lower levels (like Read Committed) allow more concurrent throughput but risk certain anomalies. Most production systems default to Read Committed and use optimistic locking or explicit transactions only where correctness is critical.

---

## 5. APIs, Web & Networking

### Q21: What's the difference between REST and GraphQL, and when would you choose each?
**A:** REST exposes fixed endpoints per resource, is simple to cache (via HTTP semantics), and is well understood, but can lead to over-fetching or under-fetching data and multiple round trips for related resources. GraphQL lets clients request exactly the fields they need in a single query, reducing round trips, but adds complexity (query cost analysis, caching is harder, N+1 query risk on the backend). I'd pick REST for simple, resource-oriented APIs and GraphQL when clients have varied, nested data needs (e.g., a mobile app pulling data from many related resources at once).

### Q22: Explain what happens when you type a URL into a browser and hit enter.
**A:** Briefly: DNS resolution translates the domain to an IP address, the browser opens a TCP connection (and TLS handshake for HTTPS), sends an HTTP request, the server processes it (possibly hitting a database, cache, etc.) and returns a response, and the browser parses the HTML/CSS/JS and renders the page, making additional requests for assets along the way.

### Q23: What's the difference between HTTP status codes 401 and 403?
**A:** 401 Unauthorized means the request lacks valid authentication credentials — the client should authenticate. 403 Forbidden means the client is authenticated but doesn't have permission to access the resource — re-authenticating won't help.

### Q24: How do you design an idempotent API endpoint?
**A:** Idempotency means calling the same request multiple times has the same effect as calling it once. For `PUT` and `DELETE`, this is often natural. For `POST` (like creating a payment), I'd require an idempotency key from the client, store it server-side with the result of the first request, and return the cached result if the same key is seen again — this protects against duplicate charges from retries.

### Q25: What's CORS, and why does it exist?
**A:** CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts web pages from making requests to a different origin (domain/protocol/port) than the one that served the page, unless the server explicitly allows it via response headers like `Access-Control-Allow-Origin`. It exists to prevent malicious sites from silently making authenticated requests to other sites on a user's behalf.

---

## 6. Testing, Debugging & Code Quality

### Q26: What's the difference between unit, integration, and end-to-end tests?
**A:** Unit tests verify a single function/class in isolation (fast, mock dependencies). Integration tests verify multiple components work together correctly (e.g., service + real database). End-to-end tests verify the whole system behaves correctly from the user's perspective (slowest, most brittle, but highest confidence). A healthy test suite follows the "testing pyramid" — many unit tests, fewer integration tests, and a small number of E2E tests.

### Q27: How do you approach debugging a production issue you can't reproduce locally?
**A:** I'd start by gathering evidence: logs, error rates, metrics/dashboards, and recent deploys around the time the issue started. I'd check for correlation with specific inputs, traffic spikes, or infrastructure changes. If needed, I'd add more granular logging or tracing behind a feature flag, reproduce with production-like data in staging, and use techniques like bisecting recent commits to isolate the change that introduced the bug.

### Q28: What makes code "maintainable" to you?
**A:** Clear naming, small functions with single responsibilities, minimal duplication, meaningful tests that document intent, consistent style, and comments that explain *why* rather than *what*. I also value code that fails loudly and clearly (good error messages) rather than silently doing the wrong thing.

### Q29: How do you decide what to unit test vs. not?
**A:** I prioritize testing business logic, edge cases, and anything with complex branching. I'm more cautious about over-testing trivial getters/setters or framework glue code, since that adds maintenance cost without much value. I also make sure tests cover regressions for any bug I fix, so it can't silently reappear.

### Q30: Tell me about a time you introduced a bug and how you handled it.
**A (sample framing):** "In a previous role, I shipped a caching change that assumed cache keys were unique per user but missed a case where two users could share a session token during a migration. It caused a small number of users to briefly see each other's cached data. I noticed via an anomaly in our error monitoring, rolled back within 20 minutes, wrote a post-mortem, and added a test plus a monitoring alert specifically for that class of key collision. I also proposed a code review checklist item for cache key design going forward." *(Tailor this to a real experience — interviewers value authenticity and specific detail.)*

---

## 7. Behavioral Questions (STAR Method)

> **STAR = Situation, Task, Action, Result.** Keep answers to 1.5–3 minutes: enough detail to be credible, not so much you lose the thread. Always end with a concrete result or lesson learned.

### Q31: Tell me about a time you disagreed with a teammate or manager. How did you handle it?
**A (framework):** Describe the specific technical or process disagreement (Situation/Task), explain how you advocated for your position with data or reasoning while staying open to being wrong (Action), and share the outcome — whether you convinced them, they convinced you, or you reached a compromise (Result). Emphasize that you disagreed respectfully and the relationship stayed intact regardless of outcome.

### Q32: Describe a time you had to deliver difficult news or push back on a deadline.
**A (framework):** Set up the context of unrealistic scope or timeline (Situation/Task). Explain how you assessed the real risk, gathered data (e.g., "here's what we'd have to cut"), and communicated proactively rather than waiting until the deadline was missed (Action). Share the result — how the team adjusted scope, timeline, or resources, and what you learned about setting expectations earlier next time.

### Q33: Tell me about a project you're most proud of.
**A (framework):** Pick something with real technical or business impact, not just complexity. Explain the problem it solved, your specific contribution (be honest about what was you vs. the team), key technical decisions and trade-offs you made, and quantify the result if possible (latency improved by X%, saved Y hours, adopted by Z teams).

### Q34: Describe a time you failed. What did you learn?
**A (framework):** Choose a real failure with genuine stakes — not a humble-brag disguised as a failure. Own the mistake without excessive self-blame, explain the root cause, and focus most of your answer on the concrete change you made afterward (a new habit, process, or technical safeguard) to prevent it from happening again.

### Q35: How do you handle receiving critical feedback?
**A (framework):** Emphasize that you actively seek feedback rather than just tolerating it, that you separate the feedback from your ego, and give a specific example where feedback changed how you approached something — ideally showing a before/after in your work style or output.

### Q36: Tell me about a time you had to learn something new quickly to complete a project.
**A (framework):** Describe the unfamiliar technology/domain and the time pressure (Situation/Task), your approach to learning efficiently (reading docs, finding a mentor, building a small prototype first) (Action), and the outcome, including how you retained that skill afterward.

### Q37: How do you prioritize when you have multiple competing deadlines?
**A (framework):** Explain your framework — e.g., assessing impact vs. effort, communicating trade-offs to stakeholders early, and being transparent about what will slip rather than silently doing all of it poorly. A concrete example with a real prioritization call (and its outcome) is stronger than a general philosophy alone.

### Q38: Why are you leaving your current role / why do you want to switch jobs?
**A (framework):** Keep it forward-looking and positive — focus on what you're moving *toward* (growth, scope, technical challenge, mission alignment) rather than what you're running *from*. Avoid criticizing your current employer, manager, or team directly. Example structure: "I've grown a lot in my current role, particularly in [X], and I'm looking for [specific thing this new role offers] — which is why this opportunity stood out."

### Q39: Why do you want to work here specifically?
**A (framework):** This one rewards real research — reference something specific about the company's product, engineering culture, technical challenges, or mission that genuinely connects to your background or interests. Avoid generic answers ("great culture," "exciting growth") without specifics.

### Q40: Where do you see yourself in a few years?
**A (framework):** Show ambition that's plausible and aligned with the role — e.g., growing technical depth, taking on more ownership/scope, potentially mentoring, without over-committing to a rigid title or timeline. Tie it back to why this role is a good stepping stone.

---

## 8. Questions to Ask Your Interviewer

Asking good questions signals genuine interest and helps you evaluate the role too.

**About the role/team:**
- What does success look like in this role after 6 months?
- What's the biggest technical challenge the team is facing right now?
- How is the team structured, and how do you collaborate with product/design?

**About engineering culture:**
- What's the code review and deployment process like?
- How does the team balance shipping speed with technical debt?
- What does on-call look like, if applicable?

**About growth:**
- How do engineers grow from mid-level to senior here — is there a defined path?
- What does mentorship or feedback look like day-to-day?

**About the company:**
- What are the team's priorities for the next 6–12 months?
- What's changed most about the engineering org in the last year?

*(Avoid asking things easily found on the website. Pick 3–4 questions max, tailored to what you actually want to know.)*

---

## 9. Interview Day Checklist

- [ ] Research the company's product, recent news, and engineering blog if available
- [ ] Review your resume — be ready to speak to every bullet point in detail
- [ ] Prepare 4–5 strong STAR stories that can flex across multiple behavioral questions
- [ ] Practice explaining past projects clearly and concisely (elevator-pitch version + deep-dive version)
- [ ] Do a few timed coding problems in the days before (mediums are most common at mid-level)
- [ ] Prepare your questions for the interviewer (see Section 8)
- [ ] Test your tech setup if virtual (camera, mic, IDE/collaborative editor access)
- [ ] Get a good night's sleep — reasoning quality drops noticeably when tired
- [ ] Have water nearby and a notepad for jotting down clarifying questions during system design/coding

---

*Tip: Tailor the technical sections above to the specific tech stack in the job description before your interview — this guide covers general, language-agnostic concepts, but expect deeper follow-ups in whatever language/framework the role specifies.*
