import asyncio, typer, uvicorn, os, signal
from anchorcd.config import load_config
from anchorcd.reconcilers.watcher import run_cycle, reconcile_on_merge

app = typer.Typer()

@app.command()
def once(config: str = "anchors.yaml"):
    cfg = load_config(config)
    for r in cfg.repos:
        res = run_cycle(r, cfg.secrets)
        typer.echo(res)

@app.command()
def daemon(config: str = "anchors.yaml", interval: int = 900, api_port: int = 8080):
    cfg = load_config(config)

    async def loop():
        while True:
            for r in cfg.repos:
                try:
                    res = run_cycle(r, cfg.secrets)
                    print(res)
                except Exception as e:
                    print("cycle error:", e)
            await asyncio.sleep(interval)

    async def main():
        loop_task = asyncio.create_task(loop())
        # optional: start FastAPI for webhooks/health
        server = uvicorn.Server(uvicorn.Config("anchorcd.server.api:app", host="0.0.0.0", port=api_port, log_level="info"))
        server_task = asyncio.create_task(server.serve())
        stop = asyncio.get_running_loop().create_future()
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_running_loop().add_signal_handler(sig, lambda: stop.set_result(True))
        await stop
        loop_task.cancel(); server.should_exit = True
        await asyncio.gather(loop_task, server_task, return_exceptions=True)

    asyncio.run(main())

if __name__ == "__main__":
    app()