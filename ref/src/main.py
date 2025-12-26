"""
THE COMPOSITION ROOT (Launcher)

Role: The Big Bang. Configures and starts the application.
Mandate: Mandate V (Config) & VIII (Coordination) & X (Infrastructure).
Pattern: ref/patterns/05-config-injection.md

Flow:
1. Load Config (Crash on Failure).
2. Wire Infrastructure (Service Classes).
3. Launch Interface (App).

Example Implementation:
```python
import uvicorn
from domain.system.config import AppConfig
from service.conversation import ConversationExecutor, ConversationRuntime
from api.app import create_api

def main():
    # 1. Load Config (System crashes if env is missing)
    # AppConfig inherits BaseSettings, so it loads from env/files automatically.
    config = AppConfig()

    # 2. Wire Dependencies (Service Classes)
    # Executors take Config
    executor = ConversationExecutor(
        dsn=config.database_url,
        api_key=config.api_key
    )
    
    # Runtimes take Executors
    runtime = ConversationRuntime(executor=executor)

    # 3. Launch Interface (pass wired services)
    app = create_api(runtime=runtime)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```
"""
