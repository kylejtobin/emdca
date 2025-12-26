"""
THE STATE MACHINE (Workflow)

Role: Defines the business process graph.
Mandate: Mandate IX (Workflow) & II (State).
Pattern: ref/patterns/09-workflow-state-machine.md

Constraint:
- Smart Enums define the graph.
- Sum Types define the nodes.
- Pure Transitions `step(state, event)`.

Example Implementation:
```python
class ConversationKind(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"

class ActiveConversation(BaseModel):
    kind: Literal[ConversationKind.ACTIVE]
    def close(self) -> tuple[ClosedConversation, Intent]: ...
```
"""
