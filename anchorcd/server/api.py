from fastapi import FastAPI, Request, Response
app = FastAPI()

@app.get("/health")
def health(): return {"ok": True}

# Optionally: endpoints to receive Git provider webhooks (push/PR merged) and trigger reconcile