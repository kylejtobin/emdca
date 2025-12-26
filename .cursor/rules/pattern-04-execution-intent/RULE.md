---
description: "Pattern 04: Execution — Intent as Contract. Domain decides, Shell executes, models parse."
globs: ["**/domain/**/*.py", "**/service/**/*.py"]
alwaysApply: false
---

# Pattern 04: Execution Intent

## Valid Code Structure

```python
# Smart Enums
class IntentKind(StrEnum):
    SEND_EMAIL = "send_email"
    NO_OP = "no_op"

class EmailResultKind(StrEnum):
    SENT = "email_sent"
    FAILED = "email_failed"
    UNHANDLED = "email_unhandled"

# Intent: Complete specification of what to do AND how to interpret results
class SendEmailIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[IntentKind.SEND_EMAIL]  # NO DEFAULT
    
    to: Email
    subject: EmailSubject
    body: EmailBody
    handled_failures: tuple[SmtpFailure, ...]  # NO DEFAULT
    
    def is_handled(self, failure: SmtpFailure) -> bool:
        """Check if a failure type is in the handled set."""
        return failure in self.handled_failures
    
    def on_sent(self, outcome: SmtpSent) -> EmailSent:
        return EmailSent(kind=EmailResultKind.SENT, message_id=outcome.message_id, recipient=self.to)
    
    def on_failed(self, outcome: SmtpFailed) -> EmailFailed:
        return EmailFailed(kind=EmailResultKind.FAILED, recipient=self.to, failure=outcome.failure)

# NoOp: Explicit "do nothing" decision
class NoOp(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[IntentKind.NO_OP]  # NO DEFAULT
    reason: NoOpReason

type SignupDecision = SendEmailIntent | NoOp

# Aggregate returns Intent
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

# Executor: Service Layer (Regular Class - "Worker with Tools")
class EmailExecutor:
    def __init__(self, config: SmtpConfig):
        self.config = config
    
    def execute(self, intent: SendEmailIntent, raw: RawSmtpResult) -> EmailResult:
        # Pure Parsing logic (static or module-level)
        outcome = SmtpParser.parse(raw)
        
        match outcome:
            case SmtpClientSuccess(message_id=mid):
                return intent.on_sent(SmtpSent(kind=InfraResultKind.SMTP_SENT, message_id=mid))
            case SmtpClientError(failure=f) if intent.is_handled(f):
                return intent.on_failed(SmtpFailed(kind=InfraResultKind.SMTP_FAILED, failure=f))
            case SmtpClientError(failure=f):
                return EmailUnhandled(kind=EmailResultKind.UNHANDLED, recipient=intent.to, failure=f)
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Intent carries parameters + outcome mapping | Side effects in domain |
| `on_success`/`on_failure` methods on Intent | `try/except` in executor |
| `raw.to_foreign().to_domain()` chain | Exceptions for control flow |
| **Smart Enums for Intent/Result Kinds** | **String Literals for Kinds** |
| Infrastructure returns Sum Type | **Service/Client Object injection into domain/executor** |
| `handled_failures` explicit | Default values on Intent fields |
| **Executor is a Regular Class** | **Executor is a Pydantic Model or Dataclass** |
| **Typed Fields (Email)** | **Stringly Typed Fields (str)** |
