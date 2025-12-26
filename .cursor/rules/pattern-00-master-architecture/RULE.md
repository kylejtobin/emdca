---
description: EMDCA architectural rules for AI-assisted development
globs: ["**/*.py"]
alwaysApply: true
---

# 🪞 THE MIRROR

An architectural scanner runs **automatically after every file edit** via hooks. It writes findings to `.cursor/mirror-feedback.md`.

**You should also run it yourself** to see violations directly:

```bash
python3 .cursor/hooks/mirror.py <path/to/file.py>
```

Check the mirror output. Fix violations before proceeding. This is your feedback loop — use it.

---

## 🚨 CRITICAL (Most Violated Rules)

**1. No `try/except`** — Models parse data, they don't catch exceptions.
```python
# ❌ WRONG: Catching exceptions in Domain
try:
    result = client.send()
except SmtpError as e:
    return Failure(str(e))

# ✅ RIGHT: Let Infrastructure crash or return Result types
raw: RawSmtpResult = ...  # Service gets this
outcome = raw.to_foreign().to_domain()  # Pure data transformation
```

**2. No default values** — Explicit at construction, always.
```python
# ❌ WRONG: Defaults hide business rules
kind: Literal["email_sent"] = "email_sent"
timeout: float = 5.0

# ✅ RIGHT: Caller must be explicit
kind: Literal[EmailResultKind.SENT]  # No default
timeout: TimeoutSeconds  # No default
```

**3. No standalone functions** — Logic lives in Containers.
```python
# ❌ WRONG: Standalone function
def execute(intent: Intent, raw: RawResult) -> Result:
    ...

# ✅ RIGHT (Domain): Method on Model
class User(BaseModel):
    def decide(self) -> Intent: ...

# ✅ RIGHT (Service): Method on Service Class
class Executor:
    def execute(self, intent: Intent) -> Result: ...
```

---

## ⚖️ The 10 Mandates

1.  **Construction:** Parse, don't validate. ([Rule](.cursor/rules/pattern-01-factory-construction/RULE.md))
2.  **State:** Sum Types. Make invalid states unrepresentable. ([Rule](.cursor/rules/pattern-02-state-sum-types/RULE.md))
3.  **Control Flow:** Railway Oriented. No exceptions for logic. ([Rule](.cursor/rules/pattern-03-railway-control-flow/RULE.md))
4.  **Execution:** Intent as Contract. ([Rule](.cursor/rules/pattern-04-execution-intent/RULE.md))
5.  **Configuration:** EnvVars as Foreign Reality. ([Rule](.cursor/rules/pattern-05-config-injection/RULE.md))
6.  **Storage:** DB as Foreign Reality. ([Rule](.cursor/rules/pattern-06-storage-foreign-reality/RULE.md))
7.  **Translation:** Foreign Models with `to_domain()`. ([Rule](.cursor/rules/pattern-07-acl-translation/RULE.md))
8.  **Coordination:** Dumb Orchestrator. ([Rule](.cursor/rules/pattern-08-orchestrator-loop/RULE.md))
9.  **Workflow:** State Machine. ([Rule](.cursor/rules/pattern-09-workflow-state-machine/RULE.md))
10. **Infrastructure:** Capability as Data. ([Rule](.cursor/rules/pattern-10-infrastructure-capability/RULE.md))

---

## Building Blocks (Use These Types)
- Smart Enums: `class Status(StrEnum)` with `@property` methods
- Value Objects: Use Pydantic built-ins (`EmailStr`, `PositiveInt`) — no hand-rolled validators
- Aggregates: Frozen Pydantic models with decision methods returning Intents OR new state
- State Transitions: Methods on source state returning target state (e.g., `PendingOrder.ship() -> ShippedOrder`)
- Commands: Inbound ADTs (what the caller wants)
- Intents: Outbound ADTs (what should happen)
- Events: Domain facts (what happened)
- Results: `Success | Failure` discriminated unions
- Foreign Models: Pydantic models mirroring external reality with `to_domain()` method
- Capability Models: Pydantic models mirroring infrastructure CONFIGURATION (Data), not INTERFACES (Methods)
- Clock: Frozen Pydantic model for time injection (not Protocol)
- Stores: **Service Classes** that handle DB I/O (injected into orchestrators)
- Orchestrators: **Service Classes** with **injected dependencies** (stores, gateways, executors)
- Executors: **Service Classes** that compose Intent + RawResult → DomainOutcome

## Implementation Order
1. Smart enums and value objects
2. Aggregates (pure decision logic with transition methods)
3. Commands / Intents / Events / Results
4. Foreign Models (external → domain translation)
5. Orchestrators (Service classes with coordination methods)
6. Executors (Service classes at infrastructure edge)

**Note:** Composition root (`main.py`) is the ONE place where standalone wiring code exists—it instantiates and connects the models.

---

## LLM Rules (When Generating Code)
- ALWAYS: Domain Objects are frozen Pydantic models
- ALWAYS: **Business Logic** is methods on Domain Models
- ALWAYS: **Wiring Logic** is methods on Service Classes
- ALWAYS: Orchestrators/Executors are **Service Classes** (Plain Python Classes)
- ALWAYS: `type` only for Discriminated Unions (Sum Types)
- ALWAYS: Dispatch via `match/case`
- ALWAYS: Foreign Model chain: `raw.to_foreign().to_domain()`
- ALWAYS: Transitions are methods on source state
- NEVER: `try/except` in domain logic
- NEVER: Default values on fields (especially `kind` discriminator)
- NEVER: Standalone functions
- NEVER: `raise` for control flow
- NEVER: `| None` for mutually exclusive states
- NEVER: Implicit `return` (use explicit `NotFound`, `NoOp` types)
- NEVER: Hand-rolled `AfterValidator` when Pydantic has built-in types
- NEVER: `typing.Protocol` (Use Data Specs / Intents)
- NEVER: Business logic in orchestrators or executors
- NEVER: `os.environ` access outside composition root

---

## 🧠 The EMDCA Discriminator (How to Decide)

1.  **Identity Check (Data vs Behavior)**
    - Does it *hold state* and *calculate*? -> **Domain Model** (`BaseModel`)
    - Does it *hold config* and *execute*? -> **Service Class** (`class`)

2.  **Mechanism Check (Structural vs Logic)**
    - Is the input *impossible* (e.g. negative age)? -> **Structure**. Enforce via Type/Field. Crash on failure.
    - Is the outcome *unfortunate* (e.g. insufficient funds)? -> **Logic**. Enforce via Method. Return Result.

3.  **Context Check (Explicit vs Implicit)**
    - Does it need the world (Time, DB)?
        - **Domain:** Pass the **Value** (`datetime`, `list[Order]`).
        - **Service:** Inject the **Provider** (`Clock`, `Repo`).

---

## LLM Failure Modes (Resist These)
- **"Simpler" is not an excuse** — If you're skipping explicit modeling, you're cutting corners, not being wise
- **Stateless orchestrators** — If your orchestrator has no fields, you're hiding dependencies. Inject them.
- **"Just one check" in Shell** — No. Business logic belongs in domain models. Always.
- **Copy principles, not syntax** — `tuple[str, ...]` in an example doesn't mean use raw strings. Think: should this be a Smart Enum?
- **Explicit modeling > fewer lines** — Deleting models isn't "clean," it's losing semantic precision
- **"Robust" try/except is hiding invalid states** — Make them unrepresentable instead
- **"Special case" is avoidance** — If it's hard to model correctly, you're avoiding the work
- **Fix violations NOW** — Don't note for later. Don't hope no one notices. Fix it.
- **Raise violations even if not asked** — See a problem? Say it. Always.
- **Read code, don't assume from paths** — File location doesn't guarantee compliance. Check.
- **Think before typing** — Pause. Understand fully. Then respond.

---

## Reference
- Pattern rules: .cursor/rules/pattern-01 through pattern-10
- Master rule: .cursor/rules/pattern-00-master-architecture/RULE.md
