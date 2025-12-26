# Pattern 04: Execution (Intent as Contract)

## The Principle
Deciding to do something, doing it, and interpreting the result are three separate concerns. The Domain decides and specifies interpretation. Infrastructure captures raw reality. The Shell composes models—never catching exceptions.

## The Mechanism
1. **The Domain** returns inert, serializable **Intents** specifying what to do AND how to interpret outcomes
2. **Infrastructure** captures raw results as **Sum Types** (success or failure variants)—no exceptions escape
3. **Foreign Models** translate raw infrastructure data through a `.to_foreign().to_domain()` chain
4. **The Shell** composes these models: Intent + RawResult → DomainOutcome

The Domain never sees exceptions. It only sees data.

---

## ❌ Anti-Pattern: Mixed Concerns

Decision-making mixed with execution makes the system impossible to test without mocking.

```python
def process_signup(user: User):
    if user.is_vip:
        smtp_client.send(to=user.email, subject="Welcome VIP", body="...")  # ❌ Side effect!
```

---

## Supporting Types

These types form the outcome chain. Showing shape, not exhaustive fields.

```python
# Failures are explicit domain types (Smart Enum)
class SmtpFailure(StrEnum):
    CONNECTION_FAILED = "connection_failed"
    TIMEOUT = "timeout"
    RECIPIENT_REJECTED = "recipient_rejected"
    # ...

class InfraResultKind(StrEnum):
    SUCCESS = "client_success"
    ERROR = "client_error"
    SMTP_SENT = "smtp_sent"
    SMTP_FAILED = "smtp_failed"

# Client-level outcomes (Sum Type)
class SmtpClientSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[InfraResultKind.SUCCESS]
    message_id: MessageId

class SmtpClientError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[InfraResultKind.ERROR]
    failure: SmtpFailure
    detail: SmtpErrorDetail  # SmtpErrorWithCode | SmtpErrorNoCode

type SmtpClientOutcome = SmtpClientSuccess | SmtpClientError

# Infrastructure outcomes (what Intent interprets)
class SmtpSent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[InfraResultKind.SMTP_SENT]
    message_id: MessageId

class SmtpFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[InfraResultKind.SMTP_FAILED]
    failure: SmtpFailure

# Executor-level outcomes (final result)
class EmailResultKind(StrEnum):
    SENT = "email_sent"
    FAILED = "email_failed"
    UNHANDLED = "email_unhandled"

class EmailSent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[EmailResultKind.SENT]
    message_id: MessageId
    recipient: Email

class EmailFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[EmailResultKind.FAILED]
    recipient: Email
    failure: SmtpFailure

class EmailUnhandled(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[EmailResultKind.UNHANDLED]
    recipient: Email
    failure: SmtpFailure

type EmailResult = EmailSent | EmailFailed | EmailUnhandled
```

---

## ✅ Pattern: The Self-Interpreting Intent

The Intent carries execution parameters AND outcome interpretation. The Domain decides what failures it handles gracefully.

```python
class IntentKind(StrEnum):
    SEND_EMAIL = "send_email"
    NO_OP = "no_op"

class SendEmailIntent(BaseModel):
    """Complete specification: what to do AND how to interpret results."""
    model_config = {"frozen": True}
    kind: Literal[IntentKind.SEND_EMAIL]
    
    to: Email
    subject: EmailSubject
    body: EmailBody
    handled_failures: tuple[SmtpFailure, ...]  # NO DEFAULT—explicit
    
    def on_sent(self, outcome: SmtpSent) -> EmailSent:
        return EmailSent(kind=EmailResultKind.SENT, message_id=outcome.message_id, recipient=self.to)
    
    def on_failed(self, outcome: SmtpFailed) -> EmailFailed:
        return EmailFailed(kind=EmailResultKind.FAILED, recipient=self.to, failure=outcome.failure)
    
    def is_handled(self, failure: SmtpFailure) -> bool:
        return failure in self.handled_failures


class NoOp(BaseModel):
    """Domain decided no action needed."""
    model_config = {"frozen": True}
    kind: Literal[IntentKind.NO_OP]
    reason: NoOpReason  # NO DEFAULT—must be explicit


type SignupDecision = SendEmailIntent | NoOp
```

The Aggregate returns the Intent:

```python
class User(BaseModel):
    model_config = {"frozen": True}
    id: UserId
    email: Email
    is_vip: bool
    
    def decide_signup_action(self) -> SignupDecision:
        if self.is_vip:
            return SendEmailIntent(
                kind=IntentKind.SEND_EMAIL,
                to=self.email,
                subject=EmailSubject.WELCOME_VIP,
                body=EmailBody.VIP_TEMPLATE,
                handled_failures=(SmtpFailure.CONNECTION_FAILED, SmtpFailure.TIMEOUT),
            )
        return NoOp(kind=IntentKind.NO_OP, reason=NoOpReason.NON_VIP)
```

---

## ✅ Pattern: Infrastructure as Sum Type

Raw infrastructure results are captured as data—never as exceptions. Each outcome variant is explicit.

```python
class RawSmtpResultKind(StrEnum):
    SUCCESS = "raw_success"
    CONNECT_ERROR = "connect_error"

class RawSmtpSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[RawSmtpResultKind.SUCCESS]
    message_id: MessageId

class RawSmtpConnectError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[RawSmtpResultKind.CONNECT_ERROR]
    message: ErrorMessage

# ... other failure variants: timeout, recipients_refused, response_error, unknown

type RawSmtpResult = RawSmtpSuccess | RawSmtpConnectError | ...  # Sum Type
```

---

## ✅ Pattern: Foreign Model Translation

Foreign Models mirror external reality and own the translation to domain types. The chain is: `Raw → Foreign → Domain`.

```python
class SmtpConnectErrorForeign(BaseModel):
    """Mirrors what smtplib.SMTPConnectError contains."""
    model_config = {"frozen": True}
    message: str
    
    def to_domain(self) -> SmtpClientError:
        return SmtpClientError(
            kind=InfraResultKind.ERROR,
            failure=SmtpFailure.CONNECTION_FAILED,
            detail=SmtpErrorNoCode(kind="no_code", message=self.message),
        )


class RawSmtpConnectError(BaseModel):
    """Raw data from infrastructure edge."""
    model_config = {"frozen": True}
    kind: Literal[RawSmtpResultKind.CONNECT_ERROR]
    message: str
    
    def to_foreign(self) -> SmtpConnectErrorForeign:
        return SmtpConnectErrorForeign(message=self.message)
```

Usage: `raw.to_foreign().to_domain()` — pure model composition.

---

## ✅ Pattern: The Pure Executor

The Executor composes models. It receives raw data, parses through the Foreign Model chain, and interprets via the Intent. No try/except—just pattern matching.

```python
# Pure Helper Module (Stateless)
class SmtpParser:
    """Pure functions for parsing raw results."""
    @staticmethod
    def parse(raw: RawSmtpResult) -> SmtpClientOutcome:
        match raw:
            case RawSmtpSuccess():
                return raw.to_foreign().to_domain()
            case RawSmtpConnectError():
                return raw.to_foreign().to_domain()
            # ... other variants

class EmailExecutor:
    """Service Layer: Worker with Tools. NOT a Model."""
    def __init__(self, config: SmtpConfig):
        self.config = config
    
    def execute(self, intent: SendEmailIntent, raw: RawSmtpResult) -> EmailResult:
        # Pure Transformation: Raw -> Domain Outcome
        outcome = SmtpParser.parse(raw)
        
        match outcome:
            case SmtpClientSuccess(message_id=mid):
                return intent.on_sent(SmtpSent(kind=InfraResultKind.SMTP_SENT, message_id=mid))
            
            case SmtpClientError(failure=f) if intent.is_handled(f):
                return intent.on_failed(SmtpFailed(kind=InfraResultKind.SMTP_FAILED, failure=f))
            
            case SmtpClientError(failure=f):
                return EmailUnhandled(kind=EmailResultKind.UNHANDLED, recipient=intent.to, failure=f)
```

---

## ✅ Pattern: Composing the Request

No optionality. If the decision requires infrastructure, pair Intent with its result as a Sum Type.

```python
class ExecutableEmail(BaseModel):
    """Intent paired with its infrastructure result."""
    model_config = {"frozen": True}
    kind: Literal["executable_email"]
    intent: SendEmailIntent
    raw: RawSmtpResult

type DispatchRequest = ExecutableEmail | NoOp  # Not raw | None
```

---

## Composition Root

```python
# Configuration (Data)
config = SmtpConfig(host="smtp.example.com", port=587)
executor = EmailExecutor(config=config)

# Runtime Loop
decision = user.decide_signup_action()

match decision:
    case NoOp():
        pass
    case SendEmailIntent() as intent:
        # 1. I/O (Infrastructure)
        raw_result = smtp_adapter.send(intent, config) 
        
        # 2. Interpretation (Pure Executor)
        final_result = executor.execute(intent, raw_result)
```

---

## Cognitive Checks

- [ ] **Intent is Complete:** Carries parameters AND outcome mapping
- [ ] **No try/except:** Models parse, they don't catch
- [ ] **No Default Values:** `handled_failures`, `reason` explicit at construction
- [ ] **No Optionality:** Sum Types replace `| None`
- [ ] **Foreign Model Chain:** `raw.to_foreign().to_domain()`
- [ ] **Executor Pattern-Matches:** No `isinstance()`, no `raise`
- [ ] **Types Over Strings:** Am I using `Email`, `MessageId`, `NoOpReason`?
- [ ] **Smart Enums:** Am I using `IntentKind` and `ResultKind`?
