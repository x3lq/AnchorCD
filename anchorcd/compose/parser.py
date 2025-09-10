import yaml
from pathlib import Path
from typing import List, Tuple

def list_images(compose_path: str) -> List[Tuple[str, str]]:
    # return [(service_name, image_ref)]
    data = yaml.safe_load(Path(compose_path).read_text())
    res = []
    for svc, cfg in (data.get("services") or {}).items():
        img = cfg.get("image")
        if img: res.append((svc, img))
    return res