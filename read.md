# FastAPI Agents

## Setup Commands

Create virtual env:

```bash
python -m venv venv
```

Install FastAPI:

```bash
pip install "fastapi[standard]"
```

Run server:

```bash
uvicorn main:app --reload
```

## QnA

**Q: Why is session yielded here instead of returned?**

A: `session` is yielded because `get_session()` is used as a FastAPI dependency. Using `yield` turns the function into a dependency generator that manages the session lifecycle:

1. FastAPI enters the `with` block and creates a database session
2. Pauses at `yield` and provides that session to the route function
3. Runs the route function while the session is still open
4. Resumes execution after `yield`, allowing the `with` block to close the session automatically

This ensures:

- The session stays open during the entire request lifecycle
- The session is properly closed after the request completes
- No resource leaks occur

If you used `return` instead, the `with` block would exit immediately and close the session before the endpoint receives it, making the session unusable.

```python
# ✓ Correct - session stays open during request
def get_session():
    with Session(engine) as session:
        yield session

# ✗ Wrong - session closes before endpoint uses it
def get_session():
    with Session(engine) as session:
        return session
```

---

**Q: Why is `yield` used in the lifespan function instead of `return` or other approaches?**

A: `yield` creates a **pause-resume** pattern that allows code to run before and after the application's lifecycle. Without `yield`, you can't execute cleanup code.

**Why not `return`?**

```python
# ✗ Doesn't work
async def lifespan(app: FastAPI):
    print("Starting up...")
    return  # ← Function exits here!
    print("Shutting down...")  # ← Never runs!
```

Once you `return`, the function ends immediately. Cleanup code never executes.

**Why not just normal code?**

```python
# ✗ Doesn't work
async def lifespan(app: FastAPI):
    print("Starting up...")
    # ← How does FastAPI know when startup ends?
    print("Shutting down...")
```

Without `yield`, there's no pause point for FastAPI to know when to start and stop the application.

**How `yield` helps:**

`yield` creates a **two-phase execution**:

1. Code **before `yield`** runs → startup completes
2. Function **pauses** at `yield` → app runs normally
3. When app shuts down, function **resumes** → cleanup runs

```python
async def lifespan(app: FastAPI):
    print("Starting up...")      # Phase 1: Startup
    yield                        # ← Pause point
    print("Shutting down...")    # Phase 2: Shutdown (guaranteed to run)
```

This ensures:

- Setup always happens before the app starts
- Cleanup always happens when the app shuts down (like try/finally behavior)
- Resources are properly released (database connections, file handles, etc.)

---

**Q: How does `yield` work from scratch? What's happening under the hood?**

A: When Python sees `yield` in a function, it converts the function into a **generator function**. Here's what happens:

1. **Generator Function**: A function with `yield` is a generator function
2. **Generator Object**: Calling a generator function returns a generator object (doesn't execute code yet!)
3. **Lazy Execution**: Code runs only when you call `next()` on the generator
4. **Pause & Resume**: Each `yield` pauses execution, and the next `next()` resumes it

Example execution:

```python
def my_gen():
    print("A")      # Line 1
    yield 1         # Line 2 - Pause #1
    print("B")      # Line 3
    yield 2         # Line 4 - Pause #2
    print("C")      # Line 5

gen = my_gen()      # Generator object created, NO code runs yet!

next(gen)           # Runs Lines 1-2, prints "A", returns 1, PAUSES
# Output: A

next(gen)           # Resumes at Line 3, prints "B", Runs Lines 3-4, returns 2, PAUSES
# Output: B

next(gen)           # Resumes at Line 5, prints "C", raises StopIteration (end reached)
# Output: C
```

**Key difference from normal functions:**

- Normal function: Executes all the way through immediately
- Generator function: Pauses at each yield, waiting for `next()` call

---

**Q: How would you implement yield behavior WITHOUT using yield?**

A: You'd need to manually build a **state machine** class. Here's how it's done:

```python
# WITHOUT YIELD - Manual State Machine
class ManualGenerator:
    def __init__(self):
        self.state = 0  # Track where we are

    def __iter__(self):
        return self

    def __next__(self):
        if self.state == 0:
            print("Step 1")
            self.state = 1
            return "First value"
        elif self.state == 1:
            print("Step 2")
            self.state = 2
            return "Second value"
        elif self.state == 2:
            print("Step 3")
            self.state = 3
            return "Third value"
        else:
            raise StopIteration  # Signal end

# Usage:
gen = ManualGenerator()
print(next(gen))  # Step 1, returns "First value"
print(next(gen))  # Step 2, returns "Second value"
print(next(gen))  # Step 3, returns "Third value"
# next(gen)       # Raises StopIteration
```

**WITH YIELD - Simple and Clean:**

```python
def my_gen():
    print("Step 1")
    yield "First value"
    print("Step 2")
    yield "Second value"
    print("Step 3")
    yield "Third value"

# Usage - same result with less code!
gen = my_gen()
print(next(gen))  # Step 1, returns "First value"
print(next(gen))  # Step 2, returns "Second value"
print(next(gen))  # Step 3, returns "Third value"
```

**Comparison:**

- Without `yield`: Complex state machine, error-prone, hard to maintain
- With `yield`: Python handles the state machine for you, clean and readable

---

**Q: Why is `yield` better for resource cleanup than returning a value?**

A: `yield` ensures cleanup happens automatically, while `return` requires manual cleanup (which is easy to forget or skip on errors).

**WITHOUT YIELD - Manual cleanup (error-prone):**

```python
class Database:
    def connect(self):
        print("✓ Connected")

    def disconnect(self):
        print("✗ Disconnected")

def get_db_manual():
    db = Database()
    db.connect()
    return db  # ← Returns immediately, function ends

# Usage:
db = get_db_manual()
try:
    # Use database
    pass
finally:
    db.disconnect()  # ← Cleanup is manual, easy to forget!
    # What if error occurs before you get here?
```

**WITH YIELD - Automatic cleanup (guaranteed):**

```python
def get_db():
    db = Database()
    db.connect()
    try:
        yield db  # ← Pause here, caller uses db
    finally:
        db.disconnect()  # ← Guaranteed to run, even if error occurs!

# Usage:
with get_db() as db:
    # Use database
    pass
# Cleanup automatically runs here, no exceptions can prevent it
```

**Why `yield` with `try/finally` is safer:**

- `finally` block **always** runs, even if an exception occurs
- No way to forget cleanup—it's guaranteed
- Exception-safe by design
- Function controls both setup AND teardown

---

**Q: How does `yield` work in FastAPI dependencies vs lifespan?**

A: Both use `yield`, but at different scopes:

**Request-level (Dependencies) - `yield` per request:**

```python
def get_session():
    session = Session(engine)  # Create per request
    try:
        yield session  # Pause: endpoint uses session
    finally:
        session.close()  # Cleanup after each request

# In endpoint:
@app.get("/items")
def read_items(session: Session = Depends(get_session)):
    # session is automatically opened here
    items = session.query(Item).all()
    # session is automatically closed after endpoint returns
    return items
```

**Application-level (Lifespan) - `yield` once at startup/shutdown:**

```python
async def lifespan(app: FastAPI):
    # Setup once at startup
    print("Starting up...")
    database = setup_database()
    yield  # Pause: app runs normally
    # Cleanup once at shutdown
    print("Shutting down...")
    database.close()

app = FastAPI(lifespan=lifespan)
```

**Key differences:**
| Aspect | Dependencies | Lifespan |
|--------|---|---|
| Scope | Per request | Per application |
| Frequency | Many times (each request) | Once (startup & shutdown) |
| Use case | Database sessions, auth | Database pools, caches, configs |
| When `yield` pauses | During endpoint execution | While app is running |

---

**Q: What happens if you don't use `try/finally` with `yield`?**

A: Cleanup code after `yield` might not run if an exception occurs.

```python
# ✗ DANGEROUS - cleanup might be skipped
def get_db_dangerous():
    db = Database()
    db.connect()
    yield db
    db.disconnect()  # ← Won't run if exception occurs in endpoint!

# ✓ SAFE - cleanup always runs
def get_db_safe():
    db = Database()
    db.connect()
    try:
        yield db
    finally:
        db.disconnect()  # ← Always runs, exception or not!
```

**Why it matters:**

- Without `try/finally`, exceptions in the endpoint skip cleanup
- Database connections stay open → resource leak
- With `try/finally`, cleanup is guaranteed no matter what

---

**Q: Why do we need `session.add()` before `session.commit()`? Why can't we just commit directly?**

A: `commit()` on its own doesn't know what to write. SQLAlchemy/SQLModel uses the **Unit of Work** pattern — the `Session` acts as a change tracker. `session.add()` registers the object so the session knows it needs an `INSERT`. When you call `session.commit()`, it flushes all tracked objects in a single transaction.

```python
# ✗ Wrong - commit has nothing to write, the session doesn't know about db_review
session.commit()

# ✓ Correct - add() tells the session to track db_review, then commit() writes it
session.add(db_review)
session.commit()
```

**Why the two-step approach is intentional:**

The separation lets you add multiple objects and commit them all atomically in one transaction:

```python
session.add(review1)
session.add(review2)
session.add(review3)
session.commit()  # all 3 inserted atomically — if one fails, all roll back
```

This ensures:

- All-or-nothing writes (atomicity)
- If any insert fails, none of them persist (no partial data)
- One round-trip to the database instead of three
