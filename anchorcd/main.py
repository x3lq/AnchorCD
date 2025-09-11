import asyncio, typer, uvicorn, os, signal, logging, time
from anchorcd.config import load_config
from anchorcd.reconcilers.watcher import run_cycle, reconcile_on_merge

# Configure logging: INFO by default, DEBUG when ANCHORCD_LOG=DEBUG
LOG_LEVEL = os.getenv("ANCHORCD_LOG", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("anchorcd")

app = typer.Typer()

@app.command()
def create_ssh_key(path: str):

    if not path:
        logger.error("No path provided for SSH key")
        return (False, None)

    path = os.path.expanduser(path)

    if os.path.exists(path):
        logger.error("File %s already exists, nothihng to do", path)
        return (True, path)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    os.system(f"ssh-keygen -t rsa -b 4096 -f {path} -N ''")
    logger.info("SSH key created at %s", path)
    
    with open(path + ".pub", "r") as f:
        pubkey = f.read().strip()
        logger.info("Add the public key to your Git provider: %s", pubkey)
    
    return (True, path)



@app.command()
def once(config: str = "anchors.yaml"):
    logger.info("Running one reconciliation cycle with config: %s", config)
    cfg = load_config(config)

    # Optional: create SSH key if not exists
    if cfg.secrets.ssh_key is not None:
        create_ssh_key(cfg.secrets.ssh_key)

    for r in cfg.repos:
        try:
            res = run_cycle(r, cfg.secrets)
            logger.info("Repo %s cycle OK", r.name)
            logger.info("Repo %s: %s", r.name, res.get("status"))

        except Exception:
            logger.exception("Repo %s cycle failed", r.name)

@app.command()
def daemon(config: str = "anchors.yaml", interval: int = 900, api_port: int = 8080):
    cfg = load_config(config)
    logger.info("Starting daemon: interval=%ss api_port=%s repos=%d", interval, api_port, len(cfg.repos))

    # Optional: create SSH key if not exists
    create_ssh_key(config)

    async def loop():
        while True:
            for r in cfg.repos:
                start = time.time()
                try:
                    res = run_cycle(r, cfg.secrets)
                    elapsed = (time.time() - start) * 1000
                    logger.info("Repo %s cycle OK", r.name)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Repo %s cycle result: %s (%.1f ms)", r.name, res, elapsed)
                    else:
                        logger.info("Repo %s: %s", r.name, res.get("status"))
                except Exception:
                    logger.exception("Repo %s cycle failed", r.name)
            logger.debug("Sleeping %s seconds before next cycle", interval)
            await asyncio.sleep(interval)

    async def main():
        loop_task = asyncio.create_task(loop())
        # optional: start FastAPI for webhooks/health
        server = uvicorn.Server(uvicorn.Config(
            "anchorcd.server.api:app",
            host="0.0.0.0",
            port=api_port,
            log_level=LOG_LEVEL.lower(),
        ))
        server_task = asyncio.create_task(server.serve())
        stop = asyncio.get_running_loop().create_future()
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_running_loop().add_signal_handler(sig, lambda: stop.set_result(True))
        logger.info("Daemon ready: API on :%s", api_port)
        await stop
        logger.info("Shutting down daemon…")
        loop_task.cancel(); server.should_exit = True
        await asyncio.gather(loop_task, server_task, return_exceptions=True)

    asyncio.run(main())

if __name__ == "__main__":
    app()