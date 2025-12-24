# EMDCA: Explicitly Modeled Data-Centric Architecture

[![Architecture: EMDCA](https://img.shields.io/badge/Architecture-EMDCA-blueviolet)](ref/arch.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**A rigorous architectural standard for building correct-by-construction, AI-native software systems.**

EMDCA eliminates "conceptual fragmentation" by enforcing strict co-location of logic and data, utilizing algebraic data types, and separating decision-making (Pure Core) from execution (Impure Shell).

---

## 🎯 Why EMDCA?

Software systems fail not from incorrect algorithms but from **scattered truth**. The rules governing a business entity become distributed across services, validators, and utilities. Understanding what an "Order" truly is requires archaeology across dozens of files.

EMDCA fixes this structurally:

- **Co-locate logic with data.** The type answers the question, not an external service.
- **Make invalid states unrepresentable.** Validation happens once, at construction.
- **Separate decisions from side effects.** The Pure Core decides; the Impure Shell executes.

---

## ⚖️ The 10 Mandates

1.  **Construction:** Factory methods on frozen Pydantic models. Parse, don't validate.
2.  **State:** Sum Types (Discriminated Unions). Make invalid states unrepresentable.
3.  **Control Flow:** Railway Oriented Programming. No exceptions for domain logic.
4.  **Execution:** Intents as Contracts. Infrastructure returns Sum Types; models parse.
5.  **Configuration:** EnvVars as Foreign Reality. Translate to pure AppConfig.
6.  **Storage:** DB as Foreign Reality. Stores are Pydantic models injected as fields.
7.  **Translation:** Foreign Models with `.to_domain()`. Declarative mapping at the border.
8.  **Coordination:** Orchestrators are Pydantic models with dependencies as fields.
9.  **Workflow:** Process as State Machine. Transitions are methods on source state.
10. **Infrastructure:** Capability as Data. Model what infrastructure expects.

**→ Read the [Architecture Spec](ref/arch.md) for the principles, then the [Patterns](ref/patterns/) for implementation.**

---

## 🛡️ Automated Enforcement: "The Architect's Mirror"

EMDCA is not just a document; it is an active constraint system. This repository includes **The Architect's Mirror** (`.cursor/hooks/mirror.py`), a pure-Python AST analyzer that enforces the mandates in real-time.

It acts as a "Synthetic Supervisor" for both Human Developers and AI Agents, instantly flagging:
- **Structural Violations**: Using `raise` or `await` in the Domain.
- **Architectural Drift**: Importing external libraries (`boto3`) into the Pure Core.
- **Procedural Habits**: Writing `Manager` classes instead of Aggregates.

The Mirror runs:
1.  **Locally**: Inside Cursor via Hooks (`afterFileEdit`).
2.  **Remotely**: In GitHub Actions (`.github/workflows/ci.yml`).

---

## 📚 Documentation

| Document | What It Is |
| :--- | :--- |
| **[Manifesto](manifesto.md)** | The **Philosophy**. Why explicit modeling matters. |
| **[Architecture Spec](ref/arch.md)** | The **Laws**. The 10 mandates in detail. |
| **[Structure Guide](ref/structure.md)** | The **Map**. Vertical slice file organization. |
| **[Patterns Library](ref/patterns/)** | The **Blueprints**. Idiomatic Python implementations. |
| **[Agentic Systems](ref/agentic.md)** | The **Translation**. "Agent" buzzwords → real patterns. |
| **[Reference Skeleton](ref/src/)** | The **Template**. A working starter structure. |

---

## 🚀 Getting Started

**To Learn:** 
1. Read this README for the overview
2. Read the [Architecture Spec](ref/arch.md) for the principles
3. Read the [Patterns](ref/patterns/) for implementation details

**To Reference:** Copy `ref/` into your project. Use the patterns as a style guide.

**To Build:** Start from the [Reference Skeleton](ref/src/). Every file links back to the mandates.

**For AI Agents:** This repo is designed for you. The `.cursor/rules/` prime your context. The constraints act as guardrails—hallucinations become compilation errors.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
