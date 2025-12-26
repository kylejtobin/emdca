# EMDCA: Explicitly Modeled Data-Centric Architecture

[![Architecture: EMDCA](https://img.shields.io/badge/Architecture-EMDCA-blueviolet)](ref/arch.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**A rigorous architectural standard for building correct-by-construction, AI-native software systems.**

EMDCA eliminates "conceptual fragmentation" by enforcing strict co-location of logic and data, utilizing algebraic data types, and separating decision-making (Functional Core) from execution (Imperative Shell).

---

## 🎯 Why EMDCA?

Software systems fail from **scattered truth**. The rules governing an "Order" are often distributed across services, validators, and database constraints. EMDCA fixes this by making the Type System the engine of the application.

1.  **Behavioral Types (Smart Enums):** Enums are not just labels; they are **State Engines**. They know their legal transitions and properties. The Type System defines the workflow graph, driving automation naturally.
2.  **Co-location of Logic:** The Pydantic Model answers the question, not an external service. Logic lives with Data.
3.  **Correctness by Construction:** Invalid states are unrepresentable. Validation happens once, at the boundary.
4.  **Explicit Context:** No magic globals. No hidden I/O. Dependencies are explicit; Time is data.

---

## ⚖️ The 10 Mandates

1.  **Construction:** Parse, don't validate. Factory methods on frozen Pydantic models.
2.  **State:** Sum Types (Discriminated Unions). **Smart Enums drive the lifecycle.** Make invalid states unrepresentable.
3.  **Control Flow:** Railway Oriented Logic. Structural failures crash; Business failures return Results.
4.  **Execution:** Intents as Contracts. The Domain decides; the Service executes.
5.  **Configuration:** EnvVars as Foreign Reality. Pydantic Settings as Domain Schema.
6.  **Storage:** DB as Foreign Reality. Stores are **Service Classes** (Executors) that run Load Intents.
7.  **Translation:** Foreign Models with `.to_domain()`. Explicit boundaries.
8.  **Coordination:** Orchestrators are **Service Classes** (Runtimes) that drive the loop.
9.  **Workflow:** Process as State Machine. Transitions are Pure Functions.
10. **Infrastructure:** Capability as Data. Model the configuration, not the interface.

**→ Read the [Architecture Spec](ref/arch.md) for the principles, then the [Patterns](ref/patterns/) for implementation.**

---

## 🧱 Building Blocks

*   **Smart Enums:** `StrEnum` with methods. The "Brain" of the state machine.
*   **Domain Models:** Frozen Pydantic models with **Business Logic**. The "Smart Core."
*   **Service Classes:** Plain Python classes with **Wiring Logic**. The "Dumb Shell."
*   **Intents & Results:** Data packets that cross the boundary.
*   **Foreign Models:** Mirrors of external APIs/DBs.

---

## 🔧 Cursor Agent Architecture

The `.cursor/` directory implements active enforcement for AI agents working in this codebase.

*   **Rules:** `pattern-*/RULE.md` define the laws.
*   **Mirror:** `hooks/mirror.py` runs AST analysis to detect violations (e.g., `try/except` in Domain).
*   **Feedback:** The system writes violations to `mirror-feedback.md` automatically.

**→ Read [Cursor Agent Architecture](ref/cursor_arch.md) for details on the enforcement system.**

---

## 📚 Documentation

| Document | What It Is |
| :--- | :--- |
| **[Manifesto](manifesto.md)** | The **Philosophy**. Why explicit modeling matters. |
| **[Architecture Spec](ref/arch.md)** | The **Laws**. The 10 mandates in detail. |
| **[Patterns Library](ref/patterns/)** | The **Blueprints**. Idiomatic Python implementations. |
| **[Structure Guide](ref/structure.md)** | The **Map**. Vertical slice file organization. |
| **[Reference Skeleton](ref/src/)** | The **Template**. A working starter structure. |

---

## 🚀 Getting Started

1.  **Read** the [Architecture Spec](ref/arch.md) to understand the "Physics" of the system.
2.  **Study** the [Patterns](ref/patterns/) to see the "Mechanisms" in action.
3.  **Build** your Domain Models first. Define the Types, then the Logic, then the Shell.

**For AI Agents:** This repo is designed for you. The `.cursor/rules/` prime your context. The constraints act as guardrails—hallucinations become compilation errors.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
