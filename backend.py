import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ATTACHMENTS_ROOT = Path(__file__).parent / "attachments"
STATE_FILE = Path(__file__).parent / "tracking_state.json"


@dataclass
class ResourceItem:
    id: str
    file_path: Path
    rel_path: Path
    week: str
    meta: str
    discipline: str
    section: str
    title: str
    type: str
    url: Optional[str]
    completed: bool = False


def scan_folder(root: Path) -> Dict[str, Any]:
    node = {"_name": root.name, "_files": [], "_children": {}}
    for entry in sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if entry.is_dir():
            node["_children"][entry.name] = scan_folder(entry)
        elif entry.is_file():
            node["_files"].append(entry.name)
    return node


def load_tracking_state() -> Dict[str, bool]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_tracking_state(state: Dict[str, bool]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def extract_url_resources(file_path: Path) -> List[Dict[str, str]]:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    pattern = re.compile(r"([\w_]+)\s*=\s*[\"'](https?://[^\"']+)[\"']")
    matches = pattern.findall(text)
    resources = [{"name": name, "url": url} for name, url in matches]

    if not resources:
        urls = re.findall(r"https?://[^\s\"']+", text)
        for index, url in enumerate(urls, start=1):
            resources.append({"name": f"link_{index}", "url": url})
    return resources


def collect_resources(node: Dict[str, Any], rel_path: Path = Path(".")) -> List[ResourceItem]:
    resources: List[ResourceItem] = []
    for filename in node["_files"]:
        file_rel = rel_path / filename
        file_path = ATTACHMENTS_ROOT / file_rel
        parts = file_rel.parts
        week = parts[0] if len(parts) > 0 else ""
        meta = parts[1] if len(parts) > 1 else ""
        discipline = parts[2] if len(parts) > 2 else ""
        section = parts[3] if len(parts) > 3 else ""

        suffix = file_path.suffix.lower()
        if suffix in {".py", ".txt", ".md"}:
            url_resources = extract_url_resources(file_path)
            if url_resources:
                for idx, entry in enumerate(url_resources, start=1):
                    item_id = f"{file_rel.as_posix()}|{entry['name']}"
                    resource_type = "video" if any(marker in entry["url"] for marker in [".mp4", "youtube", "youtu.be"]) else "link"
                    resources.append(
                        ResourceItem(
                            id=item_id,
                            file_path=file_path,
                            rel_path=file_rel,
                            week=week,
                            meta=meta,
                            discipline=discipline,
                            section=section,
                            title=f"{filename} - {entry['name']}",
                            type=resource_type,
                            url=entry["url"],
                        )
                    )
                continue

        item_id = file_rel.as_posix()
        if suffix == ".pdf":
            resources.append(
                ResourceItem(
                    id=item_id,
                    file_path=file_path,
                    rel_path=file_rel,
                    week=week,
                    meta=meta,
                    discipline=discipline,
                    section=section,
                    title=filename,
                    type="pdf",
                    url=None,
                )
            )
        elif suffix in {".mp4", ".mov", ".webm"}:
            resources.append(
                ResourceItem(
                    id=item_id,
                    file_path=file_path,
                    rel_path=file_rel,
                    week=week,
                    meta=meta,
                    discipline=discipline,
                    section=section,
                    title=filename,
                    type="video",
                    url=str(file_path),
                )
            )
        else:
            resources.append(
                ResourceItem(
                    id=item_id,
                    file_path=file_path,
                    rel_path=file_rel,
                    week=week,
                    meta=meta,
                    discipline=discipline,
                    section=section,
                    title=filename,
                    type="file",
                    url=None,
                )
            )

    for child_name, child_node in node["_children"].items():
        resources.extend(collect_resources(child_node, rel_path / child_name))
    return resources


def build_summary(resources: List[ResourceItem]) -> Dict[str, int]:
    return {
        "resources": len(resources),
        "weeks": len({item.week for item in resources if item.week}),
        "metas": len({item.meta for item in resources if item.meta}),
        "disciplines": len({item.discipline for item in resources if item.discipline}),
    }


def get_filtered_resources(resources: List[ResourceItem], week: str, meta: str, discipline: str) -> List[ResourceItem]:
    filtered: List[ResourceItem] = []
    for item in resources:
        if week != "Todas" and item.week != week:
            continue
        if meta != "Todas" and item.meta != meta:
            continue
        if discipline != "Todas" and item.discipline != discipline:
            continue
        filtered.append(item)
    return filtered


def create_pdf_embed(file_path: Path) -> str:
    try:
        file_bytes = file_path.read_bytes()
    except OSError:
        return "<div class='alert error'>PDF não encontrado.</div>"
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"<iframe src='data:application/pdf;base64,{encoded}' width='100%' height='720px' style='border:none;'></iframe>"
