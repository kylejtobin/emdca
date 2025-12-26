"""
THE IMPERATIVE SHELL (Executors & Runtimes)

Role: Wiring, I/O, and Orchestration.
Mandate: Mandate VIII (Coordination) & VI (Storage) & X (Infrastructure).
Pattern: ref/patterns/08-orchestrator-loop.md
Pattern: ref/patterns/06-storage-foreign-reality.md

Constraint:
- Regular Python Classes (Not Pydantic Models).
- Dependencies injected via `__init__`.
- No Business Logic (delegates to Domain).

Example Implementation:
```python
class ConversationExecutor:
    def __init__(self, dsn: PostgresDsn, api_key: ApiKey): ...
    def load(self, id: ConversationId) -> Conversation: ...
    def save(self, conversation: Conversation): ...

class ConversationRuntime:
    def __init__(self, executor: ConversationExecutor): ...
    def run(self, intent: StartConversation) -> Result: ...
```
"""
