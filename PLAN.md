# Development Plan
## Objective: Active Architecture Migration & Agent Workflow Hardening

**The Goal:**
Transform the repository's architectural guidance from a passive library of markdown files into an active, agent-enforced system. We will migrate patterns into Cursor Rules to ensure the agent "knows" the architecture implicitly rather than needing to "read" it. We will simultaneously harden the feedback loop to prevent domain modeling regressions (specifically primitive obsession) by implementing stricter validation hooks.

**Scope of Work:**
1.  **Migrate Patterns to Rules**: Convert `ref/patterns/*.md` into individual `.cursor/rules/` directories. Each rule will contain the pattern logic and examples, configured to apply intelligently based on file context (e.g., "Aggregate" rules applying to `entity.py` files).
2.  **Refactor Skeleton Strategy**: Transform the `ref/src/` "docstring skeletons" into a mechanism that reinforces the new Rules. This may involve converting them into Rule templates or updating their references to point to the new active Rules, ensuring a file creation event triggers the correct architectural context.
3.  **Restructure Documentation**: Move high-level documentation (`arch.md`, `agentic.md`) to `docs/` and clear out the `ref/` directory to eliminate ambiguity between "documentation for humans" and "rules for agents."
4.  **Harden Domain Modeling**: Implement specific Rules and/or Hooks that explicitly forbid "primitive obsession" (using `str` where a Value Object or Smart Enum exists) and enforce the use of `match/case` on Sum Types.
5.  **Workflow Automation**: configuring `.cursor/hooks.json` to run validation scripts that act as a "compiler" for our architectural constraints, providing immediate feedback to the agent if it violates the "Pure Domain" or "No I/O in Domain" rules.

**Formal Outcome:**
A repository where architectural patterns are actively injected into the agent's context via `.cursor/rules`, and architectural constraints are strictly enforced via `.cursor/hooks`, resulting in zero-tolerance for weak domain modeling.

## Feature - Ref Directory
I want to move the docs and skeleton from spec into the refs directory and update the readme links and ensure we have a properly 

## Feature - Cursor Rules Template
As a developer I want a templates directory in /ref with a template for a cursor rule so I know the best practices and can easily make new rules that are most effective

## Feature - Cursor Rules
As a developer I want a set of cursor rules that match the patterns that explicitly guide an agent on how to create constructs and more importantly how not to create them

## Feature - Advanced EMDCA Agent
