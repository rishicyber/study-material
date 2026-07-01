"""
============================================================
  PYTHON THREADING & LOCKS: A COMPREHENSIVE DEEP DIVE
============================================================

Topics covered:
  1.  Thread Basics & Lifecycle
  2.  Daemon vs Non-Daemon Threads
  3.  Thread Communication via Events
  4.  Race Conditions (demonstrated)
  5.  threading.Lock
  6.  threading.RLock (Reentrant Lock)
  7.  threading.Semaphore & BoundedSemaphore
  8.  threading.Condition
  9.  threading.Barrier
  10. threading.Timer
  11. Thread-Local Storage
  12. threading.Event for signaling
  13. Producer-Consumer with Queue
  14. Reader-Writer Lock (custom implementation)
  15. Deadlock: causes & avoidance
  16. Lock ordering to prevent deadlock
  17. Priority Queue with threading
  18. Thread Pool (manual implementation)
  19. concurrent.futures.ThreadPoolExecutor
  20. Thread-safe Singleton
  21. Thread-safe Counter
  22. Thread-safe Cache (LRU)
  23. Pipeline pattern
  24. Fan-out / Fan-in pattern
  25. Timeout-based locking
  26. Context manager locks
  27. Monitoring & Debugging threads
  28. Performance benchmarks

Author  : Deep Dive Series
Python  : 3.8+
"""

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
import threading
import time
import random
import queue
import logging
import functools
import collections
import itertools
import sys
import os
import traceback
import weakref
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# LOGGING SETUP  (thread-name included in every log line)
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-20s] %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DIVIDER = "=" * 60


def section(title: str) -> None:
    """Print a visible section header."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ─────────────────────────────────────────────────────────────
# 1. THREAD BASICS & LIFECYCLE
# ─────────────────────────────────────────────────────────────
section("1. THREAD BASICS & LIFECYCLE")


def simple_worker(name: str, duration: float) -> None:
    """A basic worker function run inside a thread."""
    log.debug("Worker '%s' starting (will sleep %.1fs)", name, duration)
    time.sleep(duration)
    log.debug("Worker '%s' finished", name)


def demo_thread_basics() -> None:
    threads = []
    for i in range(4):
        t = threading.Thread(
            target=simple_worker,
            args=(f"W{i}", random.uniform(0.1, 0.4)),
            name=f"BasicWorker-{i}",
        )
        threads.append(t)

    log.info("Starting %d threads", len(threads))
    for t in threads:
        t.start()

    log.info("All threads started; waiting for completion …")
    for t in threads:
        t.join()
    log.info("All threads joined")

    # Thread attributes
    t = threading.Thread(target=lambda: None, name="InspectMe")
    log.info(
        "Before start → ident=%s, is_alive=%s", t.ident, t.is_alive()
    )
    t.start()
    t.join()
    log.info(
        "After join  → ident=%s, is_alive=%s", t.ident, t.is_alive()
    )


demo_thread_basics()


# ─────────────────────────────────────────────────────────────
# 2. SUBCLASSING THREAD
# ─────────────────────────────────────────────────────────────
section("2. SUBCLASSING threading.Thread")


class CounterThread(threading.Thread):
    """Thread subclass that counts to N and stores the result."""

    def __init__(self, n: int, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.result: int = 0

    def run(self) -> None:
        log.debug("Counting to %d", self.n)
        total = 0
        for i in range(self.n):
            total += i
            time.sleep(0)          # yield voluntarily
        self.result = total
        log.debug("Done. Sum(0..%d-1) = %d", self.n, self.result)


def demo_subclass() -> None:
    workers = [CounterThread(n=100_000, name=f"Counter-{i}") for i in range(3)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    for w in workers:
        log.info("Thread %s result: %d", w.name, w.result)


demo_subclass()


# ─────────────────────────────────────────────────────────────
# 3. DAEMON THREADS
# ─────────────────────────────────────────────────────────────
section("3. DAEMON vs NON-DAEMON THREADS")


def background_heartbeat(interval: float) -> None:
    """Runs forever; won't block process exit because it's a daemon."""
    count = 0
    while True:
        count += 1
        log.debug("Heartbeat #%d", count)
        time.sleep(interval)


def demo_daemon() -> None:
    daemon = threading.Thread(
        target=background_heartbeat,
        args=(0.15,),
        name="Heartbeat",
        daemon=True,          # ← key flag
    )
    daemon.start()
    log.info("Daemon thread started (daemon=%s)", daemon.daemon)
    time.sleep(0.5)
    log.info(
        "Main thread finishing — daemon will be killed automatically"
    )
    # No need to join(); process exits cleanly.


demo_daemon()


# ─────────────────────────────────────────────────────────────
# 4. RACE CONDITIONS (INTENTIONAL BUG — educational)
# ─────────────────────────────────────────────────────────────
section("4. RACE CONDITIONS (intentional)")

UNSAFE_COUNTER = 0


def unsafe_increment(iterations: int) -> None:
    global UNSAFE_COUNTER
    for _ in range(iterations):
        # Read-modify-write is NOT atomic → race condition
        tmp = UNSAFE_COUNTER
        time.sleep(0)           # force context switch
        UNSAFE_COUNTER = tmp + 1


def demo_race_condition() -> None:
    global UNSAFE_COUNTER
    UNSAFE_COUNTER = 0
    n_threads, iters = 5, 1_000
    threads = [
        threading.Thread(target=unsafe_increment, args=(iters,))
        for _ in range(n_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    expected = n_threads * iters
    log.warning(
        "Race result: got %d, expected %d, LOST %d increments",
        UNSAFE_COUNTER, expected, expected - UNSAFE_COUNTER,
    )


demo_race_condition()


# ─────────────────────────────────────────────────────────────
# 5. threading.Lock  — THE FUNDAMENTAL PRIMITIVE
# ─────────────────────────────────────────────────────────────
section("5. threading.Lock")


class SafeCounter:
    """Wraps an integer with a Lock for thread-safe increments."""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:           # acquire → body → release
            self._value += 1

    def decrement(self) -> None:
        with self._lock:
            self._value -= 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    def __repr__(self) -> str:
        return f"SafeCounter({self.value})"


def demo_lock() -> None:
    counter = SafeCounter()
    n_threads, iters = 5, 1_000

    def worker():
        for _ in range(iters):
            counter.increment()

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = n_threads * iters
    log.info(
        "Lock result: got %d, expected %d — correct=%s",
        counter.value, expected, counter.value == expected,
    )


demo_lock()


# Low-level acquire/release (explicit)
def demo_lock_explicit() -> None:
    lock = threading.Lock()
    lock.acquire()
    try:
        log.debug("Inside explicit lock")
    finally:
        lock.release()   # ALWAYS release in finally

    # Non-blocking attempt
    acquired = lock.acquire(blocking=False)
    if acquired:
        log.debug("Got non-blocking lock")
        lock.release()

    # Timeout
    lock.acquire()
    acquired = lock.acquire(timeout=0.1)
    log.debug("Timed out? %s", not acquired)
    lock.release()


demo_lock_explicit()


# ─────────────────────────────────────────────────────────────
# 6. threading.RLock  (Reentrant Lock)
# ─────────────────────────────────────────────────────────────
section("6. threading.RLock (Reentrant Lock)")


class TreeNode:
    """Binary tree with reentrant locking for safe recursive ops."""

    def __init__(self, value: int):
        self.value = value
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None
        self._rlock = threading.RLock()

    def insert(self, val: int) -> None:
        """Recursive insert — acquires the SAME rlock multiple times."""
        with self._rlock:                    # first acquisition
            if val < self.value:
                if self.left is None:
                    self.left = TreeNode(val)
                else:
                    self.left.insert(val)    # recursive, same thread
            else:
                if self.right is None:
                    self.right = TreeNode(val)
                else:
                    self.right.insert(val)

    def inorder(self) -> List[int]:
        with self._rlock:
            result = []
            if self.left:
                result.extend(self.left.inorder())
            result.append(self.value)
            if self.right:
                result.extend(self.right.inorder())
            return result


def demo_rlock() -> None:
    root = TreeNode(50)
    values = [30, 70, 20, 40, 60, 80, 10, 25, 35, 45]

    def inserter(vals):
        for v in vals:
            root.insert(v)

    half = len(values) // 2
    t1 = threading.Thread(target=inserter, args=(values[:half],))
    t2 = threading.Thread(target=inserter, args=(values[half:],))
    t1.start(); t2.start()
    t1.join();  t2.join()

    log.info("Inorder traversal: %s", root.inorder())


demo_rlock()


# ─────────────────────────────────────────────────────────────
# 7. threading.Semaphore & BoundedSemaphore
# ─────────────────────────────────────────────────────────────
section("7. Semaphore & BoundedSemaphore")


class ConnectionPool:
    """
    Simulates a DB connection pool limited to MAX_CONNS simultaneous
    connections using a BoundedSemaphore.
    """

    MAX_CONNS = 3

    def __init__(self):
        self._sem = threading.BoundedSemaphore(self.MAX_CONNS)
        self._active = 0
        self._lock = threading.Lock()
        self._peak = 0

    @contextmanager
    def connection(self):
        self._sem.acquire()
        with self._lock:
            self._active += 1
            self._peak = max(self._peak, self._active)
        log.debug("Acquired connection (active=%d)", self._active)
        try:
            yield
        finally:
            with self._lock:
                self._active -= 1
            log.debug("Released connection (active=%d)", self._active)
            self._sem.release()

    @property
    def peak_usage(self) -> int:
        return self._peak


def demo_semaphore() -> None:
    pool = ConnectionPool()

    def use_db(worker_id: int) -> None:
        with pool.connection():
            time.sleep(random.uniform(0.05, 0.2))

    threads = [
        threading.Thread(target=use_db, args=(i,), name=f"DB-{i}")
        for i in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log.info(
        "Peak concurrent connections: %d (limit=%d)",
        pool.peak_usage, ConnectionPool.MAX_CONNS,
    )
    assert pool.peak_usage <= ConnectionPool.MAX_CONNS


demo_semaphore()


# ─────────────────────────────────────────────────────────────
# 8. threading.Condition
# ─────────────────────────────────────────────────────────────
section("8. threading.Condition")


class BoundedBuffer:
    """
    Classic bounded-buffer (producer–consumer) using Condition.
    Demonstrates wait() / notify() / notify_all().
    """

    def __init__(self, capacity: int):
        self._buf: collections.deque = collections.deque()
        self._capacity = capacity
        self._cond = threading.Condition()

    def put(self, item: Any) -> None:
        with self._cond:
            while len(self._buf) >= self._capacity:
                log.debug("Buffer full (%d); producer waiting", self._capacity)
                self._cond.wait()           # releases lock; sleeps
            self._buf.append(item)
            log.debug("Produced %r (buf size=%d)", item, len(self._buf))
            self._cond.notify_all()         # wake all waiting consumers

    def get(self) -> Any:
        with self._cond:
            while not self._buf:
                log.debug("Buffer empty; consumer waiting")
                self._cond.wait()
            item = self._buf.popleft()
            log.debug("Consumed %r (buf size=%d)", item, len(self._buf))
            self._cond.notify_all()         # wake waiting producers
            return item


def demo_condition() -> None:
    buf = BoundedBuffer(capacity=3)
    sentinel = object()

    def producer():
        for i in range(8):
            buf.put(f"item-{i}")
            time.sleep(random.uniform(0.01, 0.05))
        buf.put(sentinel)

    def consumer(cid: int):
        while True:
            item = buf.get()
            if item is sentinel:
                buf.put(sentinel)   # re-add for other consumers
                break
            log.info("Consumer-%d got %r", cid, item)

    p = threading.Thread(target=producer, name="Producer")
    consumers = [
        threading.Thread(target=consumer, args=(i,), name=f"Consumer-{i}")
        for i in range(2)
    ]
    p.start()
    for c in consumers:
        c.start()
    p.join()
    for c in consumers:
        c.join()
    log.info("Condition demo complete")


demo_condition()


# ─────────────────────────────────────────────────────────────
# 9. threading.Event
# ─────────────────────────────────────────────────────────────
section("9. threading.Event")


def demo_event() -> None:
    ready = threading.Event()
    stop  = threading.Event()

    def data_loader():
        log.info("Loading data …")
        time.sleep(0.3)
        log.info("Data ready — signalling")
        ready.set()
        stop.wait()          # block until stop is signalled
        log.info("Loader shutting down")

    def processor():
        log.info("Processor waiting for data …")
        ready.wait()         # block until ready is set
        log.info("Processing data now!")
        time.sleep(0.2)
        log.info("Processor done — signalling stop")
        stop.set()

    t1 = threading.Thread(target=data_loader, name="Loader")
    t2 = threading.Thread(target=processor,   name="Processor")
    t1.start(); t2.start()
    t1.join();  t2.join()

    # Event with timeout
    timeout_evt = threading.Event()
    result = timeout_evt.wait(timeout=0.05)
    log.info("Timeout event result (expected False): %s", result)


demo_event()


# ─────────────────────────────────────────────────────────────
# 10. threading.Barrier
# ─────────────────────────────────────────────────────────────
section("10. threading.Barrier")


def demo_barrier() -> None:
    N = 4
    barrier = threading.Barrier(N, action=lambda: log.info(">>> All threads at barrier — proceeding <<<"))

    def phase_worker(wid: int) -> None:
        # Phase 1
        log.info("W%d: Phase-1 work", wid)
        time.sleep(random.uniform(0.05, 0.25))
        log.info("W%d: waiting at barrier", wid)
        barrier.wait()
        # Phase 2 — only runs after ALL threads cleared the barrier
        log.info("W%d: Phase-2 work", wid)
        time.sleep(random.uniform(0.05, 0.15))
        log.info("W%d: done", wid)

    threads = [
        threading.Thread(target=phase_worker, args=(i,), name=f"BW-{i}")
        for i in range(N)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Broken barrier example
    broken_barrier = threading.Barrier(3, timeout=0.1)

    def late_worker():
        try:
            broken_barrier.wait()
        except threading.BrokenBarrierError:
            log.warning("Barrier broken — thread cleaned up gracefully")

    t = threading.Thread(target=late_worker, name="LateWorker")
    t.start()
    t.join()


demo_barrier()


# ─────────────────────────────────────────────────────────────
# 11. threading.Timer
# ─────────────────────────────────────────────────────────────
section("11. threading.Timer")


def demo_timer() -> None:
    def alarm(msg: str) -> None:
        log.info("TIMER FIRED: %s", msg)

    t = threading.Timer(0.3, alarm, args=("hello from timer",))
    t.name = "AlarmTimer"
    t.start()

    # Cancel before it fires
    t2 = threading.Timer(1.0, alarm, args=("this should NOT fire",))
    t2.start()
    t2.cancel()
    log.info("Cancelled t2 before it could fire")

    t.join()
    log.info("Timer demo done")


demo_timer()


# ─────────────────────────────────────────────────────────────
# 12. THREAD-LOCAL STORAGE
# ─────────────────────────────────────────────────────────────
section("12. Thread-Local Storage (threading.local)")

_local = threading.local()


def set_local_context(user_id: str, role: str) -> None:
    _local.user_id = user_id
    _local.role    = role


def do_work_with_context() -> None:
    uid  = getattr(_local, "user_id", "anonymous")
    role = getattr(_local, "role",    "none")
    log.debug("Working as user=%s role=%s", uid, role)
    time.sleep(random.uniform(0.01, 0.05))
    log.debug("Done as user=%s", uid)


def demo_thread_local() -> None:
    users = [("alice", "admin"), ("bob", "reader"), ("carol", "writer")]

    def session(user_id, role):
        set_local_context(user_id, role)
        for _ in range(3):
            do_work_with_context()

    threads = [
        threading.Thread(target=session, args=u, name=f"Session-{u[0]}")
        for u in users
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("Thread-local demo complete — each thread kept its own context")


demo_thread_local()


# ─────────────────────────────────────────────────────────────
# 13. PRODUCER-CONSUMER WITH queue.Queue
# ─────────────────────────────────────────────────────────────
section("13. Producer-Consumer with queue.Queue")


def demo_queue_producer_consumer() -> None:
    task_queue: queue.Queue = queue.Queue(maxsize=5)
    results: List[str] = []
    results_lock = threading.Lock()

    def producer(n_items: int) -> None:
        for i in range(n_items):
            task_queue.put(f"task-{i}")
            log.debug("Enqueued task-%d (qsize=%d)", i, task_queue.qsize())
        # Signal end with sentinel per consumer
        for _ in range(N_CONSUMERS):
            task_queue.put(None)
        log.info("Producer done")

    def consumer(cid: int) -> None:
        while True:
            item = task_queue.get()
            if item is None:
                task_queue.task_done()
                break
            time.sleep(random.uniform(0.01, 0.05))
            result = f"result-of-{item}-by-C{cid}"
            with results_lock:
                results.append(result)
            task_queue.task_done()
        log.info("Consumer-%d exiting", cid)

    N_CONSUMERS = 3
    p = threading.Thread(target=producer, args=(10,), name="QueueProducer")
    consumers = [
        threading.Thread(target=consumer, args=(i,), name=f"QueueConsumer-{i}")
        for i in range(N_CONSUMERS)
    ]

    p.start()
    for c in consumers:
        c.start()
    p.join()
    for c in consumers:
        c.join()

    task_queue.join()   # blocks until all task_done() called
    log.info("Produced %d results", len(results))


demo_queue_producer_consumer()


# ─────────────────────────────────────────────────────────────
# 14. CUSTOM READER-WRITER LOCK
# ─────────────────────────────────────────────────────────────
section("14. Custom Reader-Writer Lock")


class ReadWriteLock:
    """
    Allows multiple concurrent readers OR one exclusive writer.
    Writers are preferred to prevent starvation.
    """

    def __init__(self):
        self._read_ready  = threading.Condition(threading.Lock())
        self._readers     = 0
        self._writers_waiting = 0
        self._writing     = False

    @contextmanager
    def read(self):
        with self._read_ready:
            while self._writing or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1
        try:
            yield
        finally:
            with self._read_ready:
                self._readers -= 1
                if self._readers == 0:
                    self._read_ready.notify_all()

    @contextmanager
    def write(self):
        with self._read_ready:
            self._writers_waiting += 1
            while self._readers > 0 or self._writing:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writing = True
        try:
            yield
        finally:
            with self._read_ready:
                self._writing = False
                self._read_ready.notify_all()


def demo_rw_lock() -> None:
    rw = ReadWriteLock()
    shared_data: Dict[str, int] = {"value": 0}
    read_counts:  List[int] = []
    write_counts: List[int] = []
    counts_lock = threading.Lock()

    def reader(rid: int) -> None:
        for _ in range(5):
            with rw.read():
                v = shared_data["value"]
                log.debug("Reader-%d saw value=%d", rid, v)
                time.sleep(0.02)
            with counts_lock:
                read_counts.append(v)
            time.sleep(random.uniform(0.01, 0.03))

    def writer(wid: int) -> None:
        for _ in range(3):
            time.sleep(random.uniform(0.05, 0.1))
            with rw.write():
                shared_data["value"] += 1
                new_val = shared_data["value"]
                log.debug("Writer-%d set value=%d", wid, new_val)
                time.sleep(0.03)
            with counts_lock:
                write_counts.append(new_val)

    threads  = [threading.Thread(target=reader, args=(i,), name=f"Rdr-{i}") for i in range(4)]
    threads += [threading.Thread(target=writer, args=(i,), name=f"Wtr-{i}") for i in range(2)]
    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log.info(
        "RW Lock demo done — final value=%d, writes=%d, reads=%d",
        shared_data["value"], len(write_counts), len(read_counts),
    )


demo_rw_lock()


# ─────────────────────────────────────────────────────────────
# 15. DEADLOCK: CAUSES & DETECTION
# ─────────────────────────────────────────────────────────────
section("15. Deadlock (simulated with timeout)")


def demo_deadlock_attempt() -> None:
    """
    Classic AB-BA deadlock: two threads acquire two locks in opposite order.
    We use try-acquire with timeout to detect and break out.
    """
    lock_A = threading.Lock()
    lock_B = threading.Lock()
    deadlock_detected = threading.Event()

    def thread1():
        lock_A.acquire()
        log.debug("T1 holds A, wants B …")
        time.sleep(0.1)
        got_b = lock_B.acquire(timeout=0.3)
        if got_b:
            log.debug("T1 got B")
            lock_B.release()
        else:
            log.warning("T1: DEADLOCK detected — releasing A and giving up")
            deadlock_detected.set()
        lock_A.release()

    def thread2():
        lock_B.acquire()
        log.debug("T2 holds B, wants A …")
        time.sleep(0.1)
        got_a = lock_A.acquire(timeout=0.3)
        if got_a:
            log.debug("T2 got A")
            lock_A.release()
        else:
            log.warning("T2: DEADLOCK detected — releasing B and giving up")
            deadlock_detected.set()
        lock_B.release()

    t1 = threading.Thread(target=thread1, name="T1-AB")
    t2 = threading.Thread(target=thread2, name="T2-BA")
    t1.start(); t2.start()
    t1.join();  t2.join()
    log.info("Deadlock detected and resolved: %s", deadlock_detected.is_set())


demo_deadlock_attempt()


# ─────────────────────────────────────────────────────────────
# 16. LOCK ORDERING TO PREVENT DEADLOCK
# ─────────────────────────────────────────────────────────────
section("16. Lock Ordering — Deadlock Prevention")


def acquire_ordered(*locks) -> None:
    """Acquire multiple locks in a consistent global order by id()."""
    for lk in sorted(locks, key=id):
        lk.acquire()


def release_all(*locks) -> None:
    for lk in locks:
        lk.release()


def demo_lock_ordering() -> None:
    lock_A = threading.Lock()
    lock_B = threading.Lock()

    def safe_thread1():
        acquire_ordered(lock_A, lock_B)
        try:
            log.debug("ST1 holds A and B safely")
            time.sleep(0.05)
        finally:
            release_all(lock_A, lock_B)

    def safe_thread2():
        acquire_ordered(lock_A, lock_B)   # same order → no deadlock
        try:
            log.debug("ST2 holds A and B safely")
            time.sleep(0.05)
        finally:
            release_all(lock_A, lock_B)

    t1 = threading.Thread(target=safe_thread1, name="Safe-T1")
    t2 = threading.Thread(target=safe_thread2, name="Safe-T2")
    t1.start(); t2.start()
    t1.join();  t2.join()
    log.info("Lock ordering demo: no deadlock")


demo_lock_ordering()


# ─────────────────────────────────────────────────────────────
# 17. PRIORITY QUEUE WITH THREADING
# ─────────────────────────────────────────────────────────────
section("17. Priority Queue with threading")


@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task_id: str = field(compare=False)
    payload: Any = field(compare=False)


def demo_priority_queue() -> None:
    pq: queue.PriorityQueue = queue.PriorityQueue()

    def producer():
        tasks = [
            PrioritizedTask(3, "low-1",  "cleanup"),
            PrioritizedTask(1, "high-1", "critical_alert"),
            PrioritizedTask(2, "med-1",  "process_order"),
            PrioritizedTask(1, "high-2", "critical_patch"),
            PrioritizedTask(3, "low-2",  "logging"),
        ]
        for task in tasks:
            pq.put(task)
            log.debug("Enqueued %s (priority=%d)", task.task_id, task.priority)
        pq.put(None)  # sentinel

    def consumer():
        while True:
            item = pq.get()
            if item is None:
                pq.task_done()
                break
            log.info(
                "Processing [P%d] %s: %s",
                item.priority, item.task_id, item.payload,
            )
            time.sleep(0.05)
            pq.task_done()

    p = threading.Thread(target=producer, name="PQ-Producer")
    c = threading.Thread(target=consumer, name="PQ-Consumer")
    p.start(); c.start()
    p.join();  c.join()
    pq.join()


demo_priority_queue()


# ─────────────────────────────────────────────────────────────
# 18. MANUAL THREAD POOL
# ─────────────────────────────────────────────────────────────
section("18. Manual Thread Pool")


class ThreadPool:
    """
    A simple thread pool backed by a work queue.
    Demonstrates the mechanics before using concurrent.futures.
    """

    def __init__(self, n_workers: int):
        self._q: queue.Queue = queue.Queue()
        self._workers: List[threading.Thread] = []
        self._lock = threading.Lock()
        self._shutdown = False

        for i in range(n_workers):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"PoolWorker-{i}",
                daemon=True,
            )
            t.start()
            self._workers.append(t)

    def _worker_loop(self) -> None:
        while True:
            item = self._q.get()
            if item is None:
                self._q.task_done()
                break
            func, args, kwargs, future_result = item
            try:
                result = func(*args, **kwargs)
                future_result["result"] = result
            except Exception as exc:
                future_result["error"] = exc
            finally:
                future_result["done"].set()
                self._q.task_done()

    def submit(self, func: Callable, *args, **kwargs) -> Dict:
        future = {"done": threading.Event(), "result": None, "error": None}
        self._q.put((func, args, kwargs, future))
        return future

    def shutdown(self, wait: bool = True) -> None:
        for _ in self._workers:
            self._q.put(None)
        if wait:
            for t in self._workers:
                t.join()

    def map(self, func: Callable, iterable) -> List:
        futures = [self.submit(func, item) for item in iterable]
        results = []
        for f in futures:
            f["done"].wait()
            if f["error"]:
                raise f["error"]
            results.append(f["result"])
        return results


def demo_thread_pool() -> None:
    def square(n: int) -> int:
        time.sleep(random.uniform(0.01, 0.05))
        return n * n

    pool = ThreadPool(n_workers=4)
    inputs = list(range(10))
    results = pool.map(square, inputs)
    pool.shutdown()
    expected = [x * x for x in inputs]
    log.info("Pool results: %s", results)
    assert results == expected, "Mismatch!"
    log.info("Thread pool results verified ✓")


demo_thread_pool()


# ─────────────────────────────────────────────────────────────
# 19. concurrent.futures.ThreadPoolExecutor
# ─────────────────────────────────────────────────────────────
section("19. concurrent.futures.ThreadPoolExecutor")


def fetch_url_mock(url: str) -> Tuple[str, int]:
    """Simulate an I/O-bound HTTP request."""
    time.sleep(random.uniform(0.05, 0.2))
    status = random.choice([200, 200, 200, 404, 500])
    return url, status


def demo_executor() -> None:
    urls = [f"https://example.com/page/{i}" for i in range(12)]

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="HTTP") as executor:
        futures = {executor.submit(fetch_url_mock, url): url for url in urls}

        ok = err = 0
        for future in as_completed(futures):
            url, status = future.result()
            if status == 200:
                ok += 1
            else:
                err += 1
            log.debug("%-40s → %d", url, status)

    log.info("Executor: %d OK, %d errors out of %d requests", ok, err, len(urls))

    # executor.map preserves input order
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch_url_mock, urls[:4]))
    log.info("map() results (ordered): %s", [r[1] for r in results])


demo_executor()


# ─────────────────────────────────────────────────────────────
# 20. THREAD-SAFE SINGLETON
# ─────────────────────────────────────────────────────────────
section("20. Thread-safe Singleton")


class Singleton:
    _instance: Optional["Singleton"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:           # first check (no lock)
            with cls._lock:
                if cls._instance is None:   # second check (with lock)
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.creation_thread = threading.current_thread().name
            self._initialized = True


def demo_singleton() -> None:
    instances = []
    lock = threading.Lock()

    def create():
        s = Singleton()
        with lock:
            instances.append(id(s))

    threads = [threading.Thread(target=create) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique = set(instances)
    log.info(
        "Singleton: %d threads, %d unique instances — correct=%s",
        len(instances), len(unique), len(unique) == 1,
    )
    log.info("Created by thread: %s", Singleton().creation_thread)


demo_singleton()


# ─────────────────────────────────────────────────────────────
# 21. THREAD-SAFE LRU CACHE
# ─────────────────────────────────────────────────────────────
section("21. Thread-safe LRU Cache")


class ThreadSafeLRUCache:
    """LRU cache safe for concurrent reads and writes."""

    def __init__(self, capacity: int):
        self._cap   = capacity
        self._cache: collections.OrderedDict = collections.OrderedDict()
        self._lock  = threading.RLock()
        self.hits   = 0
        self.misses = 0

    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            self._cache.move_to_end(key)
            self.hits += 1
            return self._cache[key]

    def put(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self._cap:
                self._cache.popitem(last=False)

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


def demo_lru_cache() -> None:
    cache = ThreadSafeLRUCache(capacity=5)

    def worker(wid: int) -> None:
        for _ in range(20):
            key = random.randint(0, 7)
            val = cache.get(key)
            if val is None:
                time.sleep(random.uniform(0.005, 0.02))  # simulate fetch
                cache.put(key, f"value-{key}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log.info(
        "LRU Cache — size=%d, hits=%d, misses=%d, hit_rate=%.1f%%",
        len(cache), cache.hits, cache.misses, cache.hit_rate * 100,
    )


demo_lru_cache()


# ─────────────────────────────────────────────────────────────
# 22. PIPELINE PATTERN
# ─────────────────────────────────────────────────────────────
section("22. Pipeline Pattern")


def pipeline_stage(
    in_q: queue.Queue,
    out_q: queue.Queue,
    transform: Callable,
    name: str,
) -> None:
    """Generic pipeline stage: read from in_q, transform, write to out_q."""
    while True:
        item = in_q.get()
        in_q.task_done()
        if item is None:
            out_q.put(None)
            log.debug("%s: sentinel forwarded", name)
            break
        result = transform(item)
        log.debug("%s: %r → %r", name, item, result)
        out_q.put(result)


def demo_pipeline() -> None:
    q0: queue.Queue = queue.Queue()   # raw numbers
    q1: queue.Queue = queue.Queue()   # squared
    q2: queue.Queue = queue.Queue()   # string form

    # Stage functions
    square_fn  = lambda x: x * x
    stringify  = lambda x: f"result={x}"

    s1 = threading.Thread(target=pipeline_stage, args=(q0, q1, square_fn,  "Stage1-Square"),    name="Stage1")
    s2 = threading.Thread(target=pipeline_stage, args=(q1, q2, stringify,  "Stage2-Stringify"), name="Stage2")
    s1.start(); s2.start()

    # Feed data
    for i in range(6):
        q0.put(i)
    q0.put(None)   # sentinel

    s1.join(); s2.join()

    # Drain results
    outputs = []
    while not q2.empty():
        item = q2.get()
        if item is not None:
            outputs.append(item)
    log.info("Pipeline outputs: %s", outputs)


demo_pipeline()


# ─────────────────────────────────────────────────────────────
# 23. FAN-OUT / FAN-IN
# ─────────────────────────────────────────────────────────────
section("23. Fan-out / Fan-in Pattern")


def demo_fan_out_fan_in() -> None:
    def expensive_compute(item: int) -> int:
        time.sleep(random.uniform(0.02, 0.1))
        return item ** 2

    inputs = list(range(10))
    results: List[int] = [0] * len(inputs)
    threads = []

    # Fan-out: one thread per input
    def compute_and_store(idx: int, val: int) -> None:
        results[idx] = expensive_compute(val)

    for i, v in enumerate(inputs):
        t = threading.Thread(target=compute_and_store, args=(i, v), name=f"Fan-{i}")
        threads.append(t)
        t.start()

    # Fan-in: wait for all
    for t in threads:
        t.join()

    log.info("Fan-out/in results: %s", results)
    assert results == [x ** 2 for x in inputs]
    log.info("Fan-out/in verified ✓")


demo_fan_out_fan_in()


# ─────────────────────────────────────────────────────────────
# 24. LOCK WITH TIMEOUT (try_lock context manager)
# ─────────────────────────────────────────────────────────────
section("24. Timeout-based Locking")


@contextmanager
def try_lock(lock: threading.Lock, timeout: float):
    """Context manager that raises TimeoutError if lock not acquired in time."""
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"Could not acquire {lock!r} within {timeout}s")
    try:
        yield
    finally:
        lock.release()


def demo_try_lock() -> None:
    lock = threading.Lock()
    errors = []

    def greedy_holder():
        with lock:
            time.sleep(0.5)

    def impatient():
        try:
            with try_lock(lock, timeout=0.1):
                log.debug("Impatient got the lock")
        except TimeoutError as e:
            log.warning("Impatient: %s", e)
            errors.append(str(e))

    t1 = threading.Thread(target=greedy_holder, name="GreedyHolder")
    t2 = threading.Thread(target=impatient,     name="Impatient")
    t1.start()
    time.sleep(0.05)   # ensure t1 holds lock first
    t2.start()
    t1.join(); t2.join()

    log.info("Try-lock demo: %d timeout(s) occurred", len(errors))


demo_try_lock()


# ─────────────────────────────────────────────────────────────
# 25. EXCEPTION HANDLING IN THREADS
# ─────────────────────────────────────────────────────────────
section("25. Exception Handling in Threads")


class ExceptionCapturingThread(threading.Thread):
    """Thread that stores any exception instead of silently dropping it."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception: Optional[BaseException] = None

    def run(self) -> None:
        try:
            super().run()
        except Exception as exc:
            self.exception = exc
            log.error("Thread %s raised: %s", self.name, exc)
            log.error(traceback.format_exc())

    def join(self, timeout=None):
        super().join(timeout=timeout)
        if self.exception:
            raise self.exception


def demo_exception_in_thread() -> None:
    def buggy():
        time.sleep(0.1)
        raise ValueError("Something went wrong inside the thread!")

    t = ExceptionCapturingThread(target=buggy, name="BuggyThread")
    t.start()
    try:
        t.join()
    except ValueError as e:
        log.info("Main caught re-raised exception: %s", e)


demo_exception_in_thread()


# ─────────────────────────────────────────────────────────────
# 26. LOCK DECORATOR
# ─────────────────────────────────────────────────────────────
section("26. Lock Decorator (synchronized)")


def synchronized(lock: Optional[threading.Lock] = None):
    """
    Decorator factory. If no lock supplied, creates one per function.
    Ensures only one thread executes the decorated function at a time.
    """
    if lock is None:
        lock = threading.Lock()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


_shared_lock = threading.Lock()


@synchronized(_shared_lock)
def critical_section(tid: int) -> str:
    log.debug("Thread %d inside critical section", tid)
    time.sleep(0.05)
    return f"done-{tid}"


def demo_lock_decorator() -> None:
    results = []
    lock = threading.Lock()

    def worker(tid):
        r = critical_section(tid)
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("Lock decorator results: %s", results)


demo_lock_decorator()


# ─────────────────────────────────────────────────────────────
# 27. MONITORING ACTIVE THREADS
# ─────────────────────────────────────────────────────────────
section("27. Monitoring Active Threads")


def demo_thread_monitoring() -> None:
    def long_task(n: int) -> None:
        time.sleep(n * 0.1)

    threads = [
        threading.Thread(target=long_task, args=(i,), name=f"LongTask-{i}")
        for i in range(5)
    ]
    for t in threads:
        t.start()

    # Poll active threads
    for _ in range(3):
        active = threading.active_count()
        names  = [t.name for t in threading.enumerate()]
        log.info("Active=%d  threads=%s", active, names)
        time.sleep(0.15)

    for t in threads:
        t.join()

    log.info("Main thread: %s", threading.main_thread().name)
    log.info("Current thread: %s", threading.current_thread().name)


demo_thread_monitoring()


# ─────────────────────────────────────────────────────────────
# 28. PERFORMANCE BENCHMARK: Lock overhead vs no-lock
# ─────────────────────────────────────────────────────────────
section("28. Performance Benchmark")


def benchmark(label: str, func: Callable, iterations: int = 500_000) -> float:
    start = time.perf_counter()
    func(iterations)
    elapsed = time.perf_counter() - start
    log.info("%-30s: %.4f s  (%d iterations)", label, elapsed, iterations)
    return elapsed


def no_lock_increment(n: int) -> None:
    x = 0
    for _ in range(n):
        x += 1


_bench_lock = threading.Lock()


def lock_increment(n: int) -> None:
    x = 0
    for _ in range(n):
        with _bench_lock:
            x += 1


def demo_benchmark() -> None:
    t_no_lock = benchmark("No-lock counter",   no_lock_increment)
    t_lock    = benchmark("Lock counter",       lock_increment)
    overhead  = (t_lock / t_no_lock - 1) * 100
    log.info("Lock overhead vs no-lock: +%.1f%%", overhead)


demo_benchmark()


# ─────────────────────────────────────────────────────────────
# 29. ADVANCED: Recursive Task Graph with Barrier Synchronisation
# ─────────────────────────────────────────────────────────────
section("29. Task Graph with Barrier Synchronisation")


def demo_task_graph() -> None:
    """
    Simulates a computation graph:
        [A, B, C] → barrier → [D, E] → barrier → [F]
    Each wave waits for the previous wave to complete.
    """

    results: Dict[str, Any] = {}
    rlock = threading.Lock()

    def run_task(name: str, deps: List[str], work_fn: Callable) -> None:
        dep_vals = {d: results.get(d) for d in deps}
        output   = work_fn(dep_vals)
        with rlock:
            results[name] = output
        log.info("Task %s → %r", name, output)

    # Wave 1
    wave1_barrier = threading.Barrier(3)
    def make_wave1(name):
        def fn(deps):
            time.sleep(random.uniform(0.05, 0.15))
            wave1_barrier.wait()
            return f"{name}_done"
        return fn

    # Wave 2 (depends on wave 1)
    wave2_barrier = threading.Barrier(2)
    def make_wave2(name):
        def fn(deps):
            assert all(v for v in deps.values()), "Dependency not satisfied"
            time.sleep(random.uniform(0.05, 0.1))
            wave2_barrier.wait()
            return f"{name}_done({list(deps.keys())})"
        return fn

    # Wave 3
    def wave3_fn(deps):
        return f"FINAL({list(deps.keys())})"

    wave1 = [
        threading.Thread(target=run_task, args=("A", [], make_wave1("A")), name="Task-A"),
        threading.Thread(target=run_task, args=("B", [], make_wave1("B")), name="Task-B"),
        threading.Thread(target=run_task, args=("C", [], make_wave1("C")), name="Task-C"),
    ]
    wave2 = [
        threading.Thread(target=run_task, args=("D", ["A","B"], make_wave2("D")), name="Task-D"),
        threading.Thread(target=run_task, args=("E", ["B","C"], make_wave2("E")), name="Task-E"),
    ]
    wave3 = [
        threading.Thread(target=run_task, args=("F", ["D","E"], wave3_fn), name="Task-F"),
    ]

    for t in wave1:
        t.start()
    for t in wave1:
        t.join()

    for t in wave2:
        t.start()
    for t in wave2:
        t.join()

    for t in wave3:
        t.start()
    for t in wave3:
        t.join()

    log.info("Task graph result: %s", results.get("F"))


demo_task_graph()


# ─────────────────────────────────────────────────────────────
# 30. ADVANCED: Throttled Worker (rate-limiter with Semaphore)
# ─────────────────────────────────────────────────────────────
section("30. Rate-Limited Worker (Semaphore + Token Bucket)")


class TokenBucket:
    """
    Thread-safe token bucket rate limiter.
    Allows `rate` operations per second with a burst of `capacity`.
    """

    def __init__(self, rate: float, capacity: int):
        self._rate     = rate
        self._capacity = capacity
        self._tokens   = float(capacity)
        self._last     = time.monotonic()
        self._lock     = threading.Lock()

    def consume(self, n: float = 1.0, block: bool = True) -> bool:
        while True:
            with self._lock:
                now      = time.monotonic()
                elapsed  = now - self._last
                self._tokens = min(
                    self._capacity,
                    self._tokens + elapsed * self._rate,
                )
                self._last = now

                if self._tokens >= n:
                    self._tokens -= n
                    return True

            if not block:
                return False
            time.sleep(1.0 / self._rate)


def demo_rate_limiter() -> None:
    limiter   = TokenBucket(rate=10.0, capacity=5)  # 10 ops/sec, burst 5
    completed = []
    lock      = threading.Lock()

    def rate_limited_task(tid: int) -> None:
        limiter.consume()   # blocks until a token is available
        with lock:
            completed.append((tid, time.monotonic()))
        log.debug("Task %d executed", tid)

    start = time.monotonic()
    threads = [
        threading.Thread(target=rate_limited_task, args=(i,), name=f"RLTask-{i}")
        for i in range(15)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    elapsed = time.monotonic() - start
    log.info(
        "Rate limiter: %d tasks in %.2fs (%.1f ops/sec)",
        len(completed), elapsed, len(completed) / elapsed,
    )


demo_rate_limiter()


# ─────────────────────────────────────────────────────────────
# 31. ADVANCED: Publish-Subscribe with threading
# ─────────────────────────────────────────────────────────────
section("31. Publish-Subscribe (Event Bus)")


class EventBus:
    """
    Thread-safe publish-subscribe bus.
    Subscribers receive events in their own dedicated queue.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[queue.Queue]] = collections.defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, topic: str) -> queue.Queue:
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._subscribers[topic].append(q)
        return q

    def publish(self, topic: str, message: Any) -> int:
        with self._lock:
            queues = list(self._subscribers.get(topic, []))
        for q in queues:
            q.put(message)
        return len(queues)

    def unsubscribe(self, topic: str, q: queue.Queue) -> None:
        with self._lock:
            subs = self._subscribers.get(topic, [])
            if q in subs:
                subs.remove(q)


def demo_event_bus() -> None:
    bus = EventBus()

    received: Dict[str, List] = collections.defaultdict(list)
    recv_lock = threading.Lock()
    stop_evt  = threading.Event()

    def subscriber(name: str, topic: str) -> None:
        q = bus.subscribe(topic)
        while not stop_evt.is_set():
            try:
                msg = q.get(timeout=0.05)
                if msg is None:
                    break
                with recv_lock:
                    received[name].append(msg)
                log.debug("%s received on '%s': %r", name, topic, msg)
            except queue.Empty:
                continue

    # Subscribers
    subs = [
        threading.Thread(target=subscriber, args=("Sub-A", "orders"),  name="Sub-A"),
        threading.Thread(target=subscriber, args=("Sub-B", "orders"),  name="Sub-B"),
        threading.Thread(target=subscriber, args=("Sub-C", "alerts"),  name="Sub-C"),
    ]
    for s in subs:
        s.start()

    time.sleep(0.05)

    # Publisher
    for i in range(5):
        bus.publish("orders", {"order_id": i, "amount": random.randint(10, 100)})
        time.sleep(0.03)
    bus.publish("alerts", {"level": "WARN", "msg": "disk > 80%"})

    time.sleep(0.2)
    stop_evt.set()
    for s in subs:
        s.join()

    for name, msgs in received.items():
        log.info("%-8s received %d messages", name, len(msgs))


demo_event_bus()


# ─────────────────────────────────────────────────────────────
# 32. ADVANCED: Work-Stealing Queue (simplified)
# ─────────────────────────────────────────────────────────────
section("32. Work-Stealing Queue (simplified)")


class WorkStealingPool:
    """
    Each worker has a local deque. Idle workers steal from others.
    Demonstrates the work-stealing paradigm used by Java's ForkJoinPool.
    """

    def __init__(self, n_workers: int):
        self._deques: List[collections.deque] = [collections.deque() for _ in range(n_workers)]
        self._locks : List[threading.Lock]    = [threading.Lock()    for _ in range(n_workers)]
        self._done   = threading.Event()
        self._total  = threading.Semaphore(0)
        self._workers: List[threading.Thread] = []
        self.completed: List[Any] = []
        self._clist_lock = threading.Lock()

        for i in range(n_workers):
            t = threading.Thread(target=self._run, args=(i,), name=f"WSW-{i}", daemon=True)
            t.start()
            self._workers.append(t)

    def submit(self, func: Callable, *args) -> None:
        idx = random.randrange(len(self._deques))
        with self._locks[idx]:
            self._deques[idx].append((func, args))
        self._total.release()

    def _steal(self, worker_id: int) -> Optional[Tuple]:
        n = len(self._deques)
        for offset in range(1, n):
            victim = (worker_id + offset) % n
            with self._locks[victim]:
                if self._deques[victim]:
                    return self._deques[victim].popleft()
        return None

    def _run(self, wid: int) -> None:
        while not self._done.is_set():
            task = None
            with self._locks[wid]:
                if self._deques[wid]:
                    task = self._deques[wid].pop()   # LIFO from own

            if task is None:
                task = self._steal(wid)

            if task is None:
                self._total.acquire(timeout=0.05)
                continue

            func, args = task
            result = func(*args)
            with self._clist_lock:
                self.completed.append(result)

    def shutdown(self) -> None:
        self._done.set()
        for t in self._workers:
            t.join()


def demo_work_stealing() -> None:
    pool = WorkStealingPool(n_workers=4)

    def task(x):
        time.sleep(random.uniform(0.005, 0.02))
        return x * x

    N = 20
    for i in range(N):
        pool.submit(task, i)

    # Wait for all tasks to complete
    deadline = time.monotonic() + 3.0
    while len(pool.completed) < N and time.monotonic() < deadline:
        time.sleep(0.05)

    pool.shutdown()
    log.info(
        "Work-stealing: submitted=%d, completed=%d",
        N, len(pool.completed),
    )


demo_work_stealing()


# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
section("SUMMARY")

summary = """
PYTHON THREADING & LOCKS — KEY TAKEAWAYS
─────────────────────────────────────────
Primitive           | Use case
────────────────────|──────────────────────────────────────────────────
threading.Lock      | Mutual exclusion (most common, simplest)
threading.RLock     | Reentrant lock for recursive code paths
threading.Semaphore | Limit concurrency (connection pools, rate limits)
threading.Condition | Complex wait/notify signalling (bounded buffers)
threading.Event     | One-shot or repeating binary signal between threads
threading.Barrier   | Synchronize N threads at a checkpoint
threading.Timer     | Delayed one-shot execution
threading.local     | Per-thread isolated state (request contexts, etc.)
queue.Queue         | Thread-safe FIFO; simplest producer-consumer glue
queue.PriorityQueue | Priority-based task scheduling
ThreadPoolExecutor  | High-level thread pool with Future support
────────────────────|──────────────────────────────────────────────────

GOLDEN RULES
  1. Always release locks in `finally` blocks (or use `with`).
  2. Acquire multiple locks in a CONSISTENT global order.
  3. Keep critical sections SHORT.
  4. Prefer higher-level abstractions (Queue, Executor) over raw locks.
  5. Avoid sharing mutable state when possible (immutability = no race).
  6. Use `threading.local` for per-thread context.
  7. Python's GIL helps with CPython interpreter internals but does NOT
     protect your own compound operations — you still need locks.
  8. For CPU-bound work, use multiprocessing or concurrent.futures.ProcessPoolExecutor.
"""

print(summary)
log.info("Deep dive complete — all %d sections executed.", 32)
