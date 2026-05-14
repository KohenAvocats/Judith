#!/usr/bin/env python3
"""
Import des jurisprudences Judilibre dans Notion via OAuth.
Cabinet Kohen Avocats - https://www.kohenavocats.fr

Lecture des JSON Judilibre (champs decision_date, zones, visa, titlesAndSummaries),
construction d'une presentation Notion structuree (callout, headings, divider, bookmark).
Parallelisme 10 workers + token bucket global pour respecter le rate limit Notion.
"""
from __future__ import annotations

import base64
import html
import json
import re
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# requests pour le keep-alive HTTP (gain x10-20 par rapport a urllib qui ouvre
# une nouvelle connexion TLS a chaque requete)
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Mappings location → libelle (extraits de la taxonomy Judilibre officielle)
try:
    from taxonomies import LOCATION_CA, LOCATION_TJ, LOCATION_TCOM
except ImportError:
    LOCATION_CA, LOCATION_TJ, LOCATION_TCOM = {}, {}, {}

# ===================== CONFIG =====================
NOTION_CLIENT_ID = "360d872b-594c-81e6-91f7-0037412b76b8"
NOTION_CLIENT_SECRET = "secret_vsfYjyZMFVYm028nrsMufCfJrMMi44VYC1SmBJ33xYO"
NOTION_REDIRECT_URI = "https://kohenavocats.github.io/notion-callback/"
LOCAL_CALLBACK_PORT = 53682

NOTION_AUTH_URL = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

DATABASE_NAME = "Jurisprudence Avril 2026"
JSON_DIR = Path(__file__).parent / "decisions_json"
CONFIG_DIR = Path.home() / ".kohen-jurisprudence"
TOKEN_FILE = CONFIG_DIR / "token.json"
PROGRESS_FILE = CONFIG_DIR / "progress.jsonl"
DB_FILE = CONFIG_DIR / "database.json"

MAX_BLOCK_CHARS = 1900
MAX_BLOCKS_PER_REQUEST = 90

WORKERS = 20
TARGET_RPS = 15.0  # Notion documente 3 req/s mais tolere des bursts ; on monte agressivement et on respecte Retry-After sur 429

# ===================== MAPPINGS =====================

CC_CHAMBERS = {
    "civ1": "Première chambre civile",
    "civ2": "Deuxième chambre civile",
    "civ3": "Troisième chambre civile",
    "comm": "Chambre commerciale, financière et économique",
    "soc": "Chambre sociale",
    "cr": "Chambre criminelle",
    "mixte": "Chambre mixte",
    "mi": "Chambre mixte",
    "pl": "Assemblée plénière",
    "ordo": "Ordonnance du Premier président",
    "creun": "Chambres réunies",
}

JURIS_LABELS = {
    "cc": "Cour de cassation",
    "ca": "Cour d'appel",
    "tj": "Tribunal judiciaire",
    "tcom": "Tribunal de commerce",
}

JURIS_COLORS = {
    "cc": "red", "ca": "orange", "tj": "blue", "tcom": "green",
}

MONTHS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
             "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


# ===================== UI =====================

LOCK = threading.Lock()

def cprint(msg, color=None):
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
              "blue": "\033[94m", "bold": "\033[1m", "reset": "\033[0m"}
    with LOCK:
        if color and sys.stdout.isatty():
            print(f"{colors.get(color, '')}{msg}{colors['reset']}", flush=True)
        else:
            print(msg, flush=True)


def banner():
    print()
    cprint("=" * 64, "blue")
    cprint("   Import des Jurisprudences Avril 2026 dans Notion", "bold")
    cprint("   Cabinet Kohen Avocats", "blue")
    cprint("=" * 64, "blue")
    print()


# ===================== TOKEN BUCKET =====================

class TokenBucket:
    def __init__(self, rate: float):
        self.rate = rate
        self.tokens = rate
        self.last = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens < 1:
                wait = (1 - self.tokens) / self.rate
                time.sleep(wait)
                self.tokens = 0
            else:
                self.tokens -= 1


BUCKET = TokenBucket(TARGET_RPS)


# ===================== OAUTH =====================

class CallbackHandler(BaseHTTPRequestHandler):
    received_code = None
    received_state = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            CallbackHandler.received_code = params["code"][0]
            CallbackHandler.received_state = params.get("state", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>OK</title><style>body{font-family:-apple-system,sans-serif;text-align:center;padding:4em;color:#1d1d1f}
h1{color:#E09019}</style></head><body>
<h1>Authentification reussie</h1>
<p>Vous pouvez fermer cet onglet et retourner au terminal.</p>
</body></html>""")
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *_):
        pass


def run_oauth() -> dict:
    state = secrets.token_urlsafe(16)
    auth_url = NOTION_AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": NOTION_CLIENT_ID, "response_type": "code", "owner": "user",
        "redirect_uri": NOTION_REDIRECT_URI, "state": state,
    })
    server = HTTPServer(("127.0.0.1", LOCAL_CALLBACK_PORT), CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print()
    cprint("=" * 64, "bold")
    cprint("  IMPORTANT pendant l'autorisation Notion :", "bold")
    cprint("=" * 64, "bold")
    cprint("  ETAPE 1 : Cliquez 'Selectionner les pages'", "green")
    cprint("  ETAPE 2 : Cochez UNE SEULE page (creez-la si necessaire)", "green")
    cprint("  ETAPE 3 : Cliquez 'Autoriser'", "green")
    cprint("=" * 64, "bold")
    print()
    cprint(f"Si rien ne s'ouvre, ouvrez : {auth_url}", "yellow")
    webbrowser.open(auth_url)
    cprint("\nEn attente de votre autorisation...", "yellow")

    start = time.time()
    while CallbackHandler.received_code is None:
        if time.time() - start > 300:
            server.shutdown()
            raise SystemExit("Timeout.")
        time.sleep(0.3)
    server.shutdown()
    if CallbackHandler.received_state != state:
        raise SystemExit("Erreur de securite (state mismatch).")

    auth = base64.b64encode(f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}".encode()).decode()
    req = urllib.request.Request(NOTION_TOKEN_URL,
        data=json.dumps({"grant_type": "authorization_code",
                         "code": CallbackHandler.received_code,
                         "redirect_uri": NOTION_REDIRECT_URI}).encode(),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erreur OAuth ({e.code}) : {e.read().decode()}")

    CONFIG_DIR.mkdir(exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(payload, indent=2))
    cprint(f"Connecte au workspace : {payload.get('workspace_name', '?')}", "green")
    return payload


def get_token() -> dict:
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text())
            if data.get("access_token"):
                cprint(f"Reconnexion au workspace : {data.get('workspace_name', '?')}", "green")
                return data
        except Exception:
            pass
    return run_oauth()


# ===================== NOTION CLIENT =====================

class NotionClient:
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }
        # Session HTTP avec keep-alive et pool de connexions
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            adapter = HTTPAdapter(pool_connections=WORKERS, pool_maxsize=WORKERS * 2, max_retries=0)
            self.session.mount("https://", adapter)
        else:
            self.session = None

    def request(self, method: str, path: str, body: dict | None = None, retries: int = 6) -> dict:
        url = NOTION_API + path if path.startswith("/") else path
        for attempt in range(retries):
            BUCKET.acquire()
            try:
                if self.session is not None:
                    resp = self.session.request(method, url, json=body, timeout=60)
                    if resp.status_code == 429:
                        wait = float(resp.headers.get("Retry-After", 5))
                        time.sleep(wait)
                        continue
                    if resp.status_code in (500, 502, 503, 504) and attempt < retries - 1:
                        time.sleep(min(2 ** attempt, 30))
                        continue
                    if resp.status_code >= 400:
                        raise RuntimeError(f"Notion {method} {path} -> {resp.status_code} {resp.text[:200]}")
                    return resp.json()
                # Fallback urllib
                data = json.dumps(body).encode() if body is not None else None
                req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                err_body = e.read().decode()
                if e.code == 429:
                    wait = float(e.headers.get("Retry-After", 5))
                    time.sleep(wait)
                    continue
                if e.code in (500, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(min(2 ** attempt, 30))
                    continue
                raise RuntimeError(f"Notion {method} {path} -> {e.code} {err_body[:200]}")
            except (urllib.error.URLError,) + ((requests.exceptions.RequestException,) if HAS_REQUESTS else ()):
                if attempt < retries - 1:
                    time.sleep(min(2 ** attempt, 30))
                    continue
                raise
        raise RuntimeError("Notion API unreachable")

    def search_shared_pages(self) -> list[dict]:
        results = []
        cursor = None
        while True:
            body = {"filter": {"value": "page", "property": "object"}, "page_size": 100}
            if cursor:
                body["start_cursor"] = cursor
            r = self.request("POST", "/search", body)
            results.extend(r.get("results", []))
            if not r.get("has_more"):
                break
            cursor = r.get("next_cursor")
        return results

    def create_database(self, parent_page_id: str) -> dict:
        body = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": DATABASE_NAME}}],
            "properties": {
                "Décision": {"title": {}},
                "Juridiction": {"select": {"options": [
                    {"name": JURIS_LABELS["cc"], "color": "red"},
                    {"name": JURIS_LABELS["ca"], "color": "orange"},
                    {"name": JURIS_LABELS["tj"], "color": "blue"},
                    {"name": JURIS_LABELS["tcom"], "color": "green"},
                ]}},
                "Date": {"date": {}},
                "Numéro": {"rich_text": {}},
                "Chambre": {"rich_text": {}},
            },
        }
        return self.request("POST", "/databases", body)

    def create_page_in_db(self, database_id: str, properties: dict, children: list[dict]) -> dict:
        body = {
            "parent": {"database_id": database_id},
            "properties": properties,
            "children": children[:MAX_BLOCKS_PER_REQUEST],
        }
        page = self.request("POST", "/pages", body)
        remaining = children[MAX_BLOCKS_PER_REQUEST:]
        if remaining:
            page_id = page["id"]
            while remaining:
                chunk = remaining[:MAX_BLOCKS_PER_REQUEST]
                remaining = remaining[MAX_BLOCKS_PER_REQUEST:]
                self.request("PATCH", f"/blocks/{page_id}/children", {"children": chunk})
        return page


# ===================== PRESENTATION NOTION =====================

def fr_date(iso: str) -> str:
    """ 2026-04-15 -> 15 avril 2026 """
    try:
        y, m, d = iso.split("-")
        di = int(d)
        day = "1er" if di == 1 else str(di)
        return f"{day} {MONTHS_FR[int(m)]} {y}"
    except Exception:
        return iso


def chamber_label(jurisdiction: str, chamber: str) -> str:
    if jurisdiction == "cc":
        return CC_CHAMBERS.get(chamber, chamber or "")
    return chamber or ""


def juris_full_label(jurisdiction: str, chamber: str, location: str) -> str:
    if jurisdiction == "cc":
        if chamber == "ordo":
            return "Ordonnance du Premier président de la Cour de cassation"
        cl = chamber_label("cc", chamber)
        return f"{cl} de la Cour de cassation" if cl else "Cour de cassation"
    if jurisdiction == "ca":
        return LOCATION_CA.get(location) or f"Cour d'appel ({location})"
    if jurisdiction == "tj":
        return LOCATION_TJ.get(location) or f"Tribunal judiciaire ({location})"
    if jurisdiction == "tcom":
        return LOCATION_TCOM.get(location) or f"Tribunal de commerce ({location})"
    return JURIS_LABELS.get(jurisdiction, jurisdiction)


def rt(text: str, bold: bool = False, italic: bool = False, code: bool = False,
       color: str = "default", href: str | None = None) -> dict:
    return {
        "type": "text",
        "text": {"content": text[:MAX_BLOCK_CHARS], **({"link": {"url": href}} if href else {})},
        "annotations": {"bold": bold, "italic": italic, "code": code, "color": color, "strikethrough": False, "underline": False},
    }


def para(rich_texts: list[dict], color: str = "default") -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": rich_texts, "color": color}}


def heading(level: int, text: str, color: str = "default") -> dict:
    key = f"heading_{level}"
    return {"object": "block", "type": key,
            key: {"rich_text": [rt(text)], "color": color, "is_toggleable": False}}


def divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def quote(text: str) -> dict:
    return {"object": "block", "type": "quote",
            "quote": {"rich_text": [rt(text)], "color": "default"}}


def bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [rt(text)], "color": "default"}}


def callout(rich_texts: list[dict], color: str = "gray_background") -> dict:
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": rich_texts, "color": color,
                        "icon": {"type": "emoji", "emoji": "📜"}}}


def bookmark(url: str, caption: str = "") -> dict:
    block = {"object": "block", "type": "bookmark", "bookmark": {"url": url}}
    if caption:
        block["bookmark"]["caption"] = [rt(caption)]
    return block


def _extract_zone_text(zone_obj, text: str) -> str:
    """Extrait le texte d'une zone Judilibre (offsets start/end dans text)."""
    if isinstance(zone_obj, list):
        parts = []
        for item in zone_obj:
            if isinstance(item, dict) and "start" in item and "end" in item:
                parts.append(text[item["start"]:item["end"]])
            elif isinstance(item, str):
                parts.append(item)
        return "\n\n".join(p.strip() for p in parts if p.strip())
    if isinstance(zone_obj, dict) and "start" in zone_obj and "end" in zone_obj:
        return text[zone_obj["start"]:zone_obj["end"]]
    if isinstance(zone_obj, str):
        return zone_obj
    return ""


def text_chunks_to_paragraphs(text: str) -> list[dict]:
    """Convertit un texte libre en blocs paragraph Notion (<= 1900 chars chacun)."""
    blocks = []
    # Normalise les sauts de ligne multiples
    paragraphs = re.split(r"\n\s*\n+", text)
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        for i in range(0, len(p), MAX_BLOCK_CHARS):
            chunk = p[i:i + MAX_BLOCK_CHARS]
            blocks.append(para([rt(chunk)]))
    return blocks


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return html.unescape(s).strip()


def extract_visa_links(visa_html: str) -> list[tuple[str, str]]:
    """Extrait (texte_lien, url) depuis du HTML."""
    return re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', visa_html or "")


def source_url(decision_id: str, jurisdiction: str) -> str:
    # L'ensemble des decisions Judilibre est exposé sur courdecassation.fr
    return f"https://www.courdecassation.fr/decision/{decision_id}"


def build_body(d: dict) -> list[dict]:
    """Construit le contenu Notion structure pour une decision."""
    blocks: list[dict] = []

    juris = d.get("jurisdiction", "")
    juris_label = JURIS_LABELS.get(juris, juris)
    ch_label = chamber_label(juris, d.get("chamber", ""))
    full_label = juris_full_label(juris, d.get("chamber", ""), d.get("location", ""))
    date_iso = d.get("decision_date", "")
    date_str = fr_date(date_iso) if date_iso else ""
    number = d.get("number", "")
    ecli = d.get("ecli", "")
    solution = d.get("solution", "")
    formation = d.get("formation", "")

    # 1. En-tete sobre (quote, sans icone)
    summary_rt = []
    if date_str:
        summary_rt.append(rt(date_str, bold=True, color=JURIS_COLORS.get(juris, "default")))
    if date_str and full_label:
        summary_rt.append(rt("  ·  "))
    if full_label:
        summary_rt.append(rt(full_label, bold=True))
    if number:
        summary_rt.append(rt("  ·  "))
        summary_rt.append(rt(f"n° {number}", code=True))
    blocks.append({"object": "block", "type": "quote",
                   "quote": {"rich_text": summary_rt, "color": "default"}})


    # 2. Visa (articles invoques) en bullets avec liens Legifrance
    visas = d.get("visa") or []
    if visas:
        blocks.append(heading(3, "Visa"))
        for v in visas:
            title_html = (v or {}).get("title", "")
            txt = strip_html(title_html)
            if not txt:
                continue
            # On reconstruit un rich_text avec les liens si possible
            links = extract_visa_links(title_html)
            if links:
                # Premier lien comme reference principale
                first_url, first_txt = links[0]
                blocks.append({
                    "object": "block", "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [rt(txt, href=first_url)], "color": "default"},
                })
            else:
                blocks.append(bullet(txt))

    # 3. Sommaires
    summaries = d.get("titlesAndSummaries") or []
    if summaries:
        blocks.append(heading(3, "Sommaire"))
        for s in summaries:
            t = (s or {}).get("title") or ""
            summ = (s or {}).get("summary") or ""
            if t:
                blocks.append(para([rt(t, bold=True)]))
            if summ:
                for i in range(0, len(summ), MAX_BLOCK_CHARS):
                    blocks.append(quote(summ[i:i + MAX_BLOCK_CHARS]))

    # 4. Texte de la decision
    blocks.append(divider())
    blocks.append(heading(2, "Texte de la décision"))

    zones = d.get("zones") or {}
    text = d.get("text") or ""
    if zones and any(zones.get(k) for k in ("introduction", "motivations", "dispositif")) and text:
        # Le decoupage semantique Judilibre est une liste d'offsets {start, end} dans `text`
        zone_labels = {"introduction": "Introduction et procédure",
                       "motivations": "Motifs de la décision",
                       "dispositif": "Dispositif"}
        for zone_key in ("introduction", "motivations", "dispositif"):
            zone_obj = zones.get(zone_key)
            if not zone_obj:
                continue
            zone_text = _extract_zone_text(zone_obj, text)
            if not zone_text.strip():
                continue
            blocks.append(heading(3, zone_labels[zone_key]))
            blocks.extend(text_chunks_to_paragraphs(zone_text))
    else:
        blocks.extend(text_chunks_to_paragraphs(text))

    # 5. Source officielle
    blocks.append(divider())
    blocks.append(heading(3, "Source officielle"))
    decision_id = d.get("id", "")
    url = source_url(decision_id, juris)
    blocks.append(bookmark(url, caption=f"ECLI : {ecli}" if ecli else ""))

    return blocks


def build_properties(d: dict, title: str) -> dict:
    juris = d.get("jurisdiction", "")
    props = {"Décision": {"title": [rt(title[:2000])]}}
    if juris in JURIS_LABELS:
        props["Juridiction"] = {"select": {"name": JURIS_LABELS[juris]}}
    if d.get("decision_date"):
        props["Date"] = {"date": {"start": d["decision_date"]}}
    if d.get("number"):
        props["Numéro"] = {"rich_text": [rt(d["number"][:200])]}
    ch = d.get("chamber", "")
    if ch:
        # Libelle long pour CC, libelle libre pour le reste
        label = CC_CHAMBERS.get(ch, ch) if juris == "cc" else ch
        props["Chambre"] = {"rich_text": [rt(label[:200])]}
    return props


def build_title(d: dict) -> str:
    juris = d.get("jurisdiction", "")
    full = juris_full_label(juris, d.get("chamber", ""), d.get("location", ""))
    date = fr_date(d.get("decision_date", "")) if d.get("decision_date") else ""
    num = d.get("number", "")
    parts = [full]
    if date:
        parts.append(date)
    if num:
        parts.append(f"n° {num}")
    return ", ".join(parts)


# ===================== PROGRESS =====================

PROGRESS_LOCK = threading.Lock()


def load_done() -> set[str]:
    if not PROGRESS_FILE.exists():
        return set()
    done = set()
    for line in PROGRESS_FILE.read_text().splitlines():
        try:
            done.add(json.loads(line)["filename"])
        except Exception:
            pass
    return done


def log_done(filename: str, page_id: str) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    with PROGRESS_LOCK:
        with PROGRESS_FILE.open("a") as f:
            f.write(json.dumps({"filename": filename, "page_id": page_id, "ts": time.time()}) + "\n")


# ===================== PARENT =====================

def _page_title(p: dict) -> str:
    for prop in (p.get("properties") or {}).values():
        if prop.get("type") == "title" and prop.get("title"):
            return "".join(t.get("plain_text", "") for t in prop["title"]) or "Sans titre"
    if isinstance(p.get("title"), list) and p["title"]:
        return p["title"][0].get("plain_text", "Sans titre")
    return "Sans titre"


def get_parent_page_id(client: NotionClient, token_data: dict) -> str:
    template_id = token_data.get("duplicated_template_id")
    if template_id:
        cprint("Page dediee creee automatiquement par Notion.", "green")
        return template_id
    while True:
        cprint("Recherche de la page partagee...", "yellow")
        pages = client.search_shared_pages()
        if pages:
            chosen = pages[0]
            cprint(f"Page parente : {_page_title(chosen)}", "green")
            return chosen["id"]
        print()
        cprint("=" * 64, "yellow")
        cprint("AUCUNE PAGE PARTAGEE AVEC L'APPLICATION", "yellow")
        cprint("=" * 64, "yellow")
        print()
        print("  1. Ouvrez Notion. Creez une page (ex: 'Jurisprudence Avril 2026').")
        print("  2. '...' en haut a droite -> 'Connexions' -> ajoutez 'Createur de RAG'.")
        print()
        input("Appuyez sur Entree quand c'est fait...")
        print()


def get_or_create_database(client: NotionClient, token_data: dict) -> str:
    if DB_FILE.exists():
        try:
            db = json.loads(DB_FILE.read_text())
            cprint("Reprise dans la database existante.", "green")
            return db["id"]
        except Exception:
            pass
    parent_id = get_parent_page_id(client, token_data)
    cprint("Creation de la database...", "yellow")
    db = client.create_database(parent_id)
    DB_FILE.write_text(json.dumps({"id": db["id"], "title": DATABASE_NAME, "parent": parent_id}, indent=2))
    cprint(f"Database creee : {db.get('url')}", "green")
    return db["id"]


# ===================== IMPORT =====================

PROGRESS = {"done": 0, "errors": 0, "start": 0.0}


def import_one(client: NotionClient, db_id: str, json_path: Path, total: int) -> tuple[str, str | None]:
    try:
        d = json.loads(json_path.read_text(encoding="utf-8"))
        title = build_title(d)
        properties = build_properties(d, title)
        children = build_body(d)
        page = client.create_page_in_db(db_id, properties, children)
        log_done(json_path.name, page["id"])
        with LOCK:
            PROGRESS["done"] += 1
            done = PROGRESS["done"]
            if done % 25 == 0 or done == total:
                elapsed = time.time() - PROGRESS["start"]
                rate = done / elapsed if elapsed > 0 else 0
                eta_min = (total - done) / rate / 60 if rate > 0 else 0
                cprint(f"[{done}/{total}] {rate:.1f}/s  ETA {eta_min:.0f} min", "blue")
        return json_path.name, None
    except Exception as e:
        with LOCK:
            PROGRESS["errors"] += 1
        return json_path.name, str(e)


# ===================== MAIN =====================

def main():
    banner()
    if not JSON_DIR.exists():
        cprint(f"Dossier {JSON_DIR} introuvable.", "red")
        sys.exit(1)
    files = sorted(JSON_DIR.rglob("*.json"))
    if not files:
        cprint(f"Aucun JSON dans {JSON_DIR}.", "red")
        sys.exit(1)
    cprint(f"Decisions a importer : {len(files)}", "bold")

    token = get_token()
    client = NotionClient(token["access_token"])
    db_id = get_or_create_database(client, token)

    done_files = load_done()
    if done_files:
        cprint(f"Reprise : {len(done_files)} deja importees, on les saute.", "yellow")
    to_import = [f for f in files if f.name not in done_files]
    total = len(to_import)
    cprint(f"A importer maintenant : {total}", "bold")
    if total == 0:
        cprint("Tout est deja importe.", "green")
        return

    eta_min = total / (TARGET_RPS * 0.7) / 60
    cprint(f"Workers : {WORKERS} en parallele, cible {TARGET_RPS} req/s", "yellow")
    cprint(f"Duree estimee : ~{eta_min:.0f} min ({eta_min/60:.1f} h).", "yellow")
    cprint("Vous pouvez interrompre (Ctrl+C) et relancer sans rien perdre.\n", "yellow")

    PROGRESS["start"] = time.time()
    errors = []
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(import_one, client, db_id, f, total): f for f in to_import}
            for fut in as_completed(futures):
                name, err = fut.result()
                if err:
                    errors.append((name, err))
                    if len(errors) <= 5:
                        cprint(f"  Erreur {name} : {err[:150]}", "red")
    except KeyboardInterrupt:
        cprint("\nInterruption. Relance pour reprendre.", "yellow")

    elapsed = time.time() - PROGRESS["start"]
    cprint(f"\nTermine en {elapsed/60:.1f} min : {PROGRESS['done']} importees, {PROGRESS['errors']} erreurs.", "green")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nArret.", "yellow")
    except SystemExit:
        raise
    except Exception as e:
        cprint(f"\nErreur : {e}", "red")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entree pour fermer...")
