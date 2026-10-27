#!/usr/bin/env python3
"""Petit scraper Reddit via l'API officielle (OAuth), sans dépendance à URS.

Lit CLIENT_ID, CLIENT_SECRET, USER_AGENT (et optionnellement REDDIT_USERNAME /
REDDIT_PASSWORD) depuis l'environnement ou `.env`. Sans pseudo/mot de passe,
utilise le mode "application seule" (client_credentials), suffisant pour la lecture.
Sans CLIENT_ID/CLIENT_SECRET, passe par les pages `.json` publiques de Reddit
(fonctionne depuis une connexion perso, bloqué depuis la plupart des serveurs).

Exemples :
    python3 scripts/reddit_scrape.py python --sort top --time week --limit 50
    python3 scripts/reddit_scrape.py python --comments 3
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://oauth.reddit.com"
PUBLIC = "https://www.reddit.com"


def load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def get_token(session):
    client_id = os.environ.get("CLIENT_ID")
    secret = os.environ.get("CLIENT_SECRET")
    if not client_id or not secret:
        return None
    user, password = os.environ.get("REDDIT_USERNAME"), os.environ.get("REDDIT_PASSWORD")
    if user and password:
        data = {"grant_type": "password", "username": user, "password": password}
    else:
        data = {"grant_type": "client_credentials"}
    r = session.post("https://www.reddit.com/api/v1/access_token",
                     auth=(client_id, secret), data=data, timeout=30)
    r.raise_for_status()
    body = r.json()
    if "access_token" not in body:
        sys.exit(f"Échec d'authentification : {body}")
    return body["access_token"]


def get(session, path, **params):
    if "Authorization" in session.headers:
        url = API + path
    else:
        url = PUBLIC + path + ".json"
    r = session.get(url, params={"raw_json": 1, **params}, timeout=30)
    if r.status_code == 429:
        time.sleep(int(float(r.headers.get("x-ratelimit-reset", 60))))
        return get(session, path, **params)
    if r.status_code == 403 and "Authorization" not in session.headers:
        sys.exit("Reddit bloque les pages publiques depuis cette connexion : "
                 "lance le script depuis chez toi, ou renseigne CLIENT_ID/CLIENT_SECRET.")
    r.raise_for_status()
    return r.json()


def fetch_posts(session, sub, sort, time_filter, limit):
    posts, after = [], None
    while len(posts) < limit:
        listing = get(session, f"/r/{sub}/{sort}", limit=min(100, limit - len(posts)),
                      after=after, t=time_filter)["data"]
        posts += [c["data"] for c in listing["children"]]
        after = listing["after"]
        if not after:
            break
    return posts


def flatten_comments(children, depth=0):
    out = []
    for c in children:
        if c["kind"] != "t1":
            continue
        d = c["data"]
        out.append({"id": d["id"], "author": d.get("author"), "score": d.get("score"),
                    "depth": depth, "body": d.get("body")})
        if d.get("replies"):
            out += flatten_comments(d["replies"]["data"]["children"], depth + 1)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("subreddit")
    p.add_argument("--sort", default="hot", choices=["hot", "new", "top", "rising", "controversial"])
    p.add_argument("--time", default="day", choices=["hour", "day", "week", "month", "year", "all"])
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--comments", type=int, default=0, help="récupérer les commentaires des N premiers posts")
    p.add_argument("--out", type=Path, default=ROOT / "scrapes")
    args = p.parse_args()

    load_env()
    session = requests.Session()
    session.headers["User-Agent"] = os.environ.get("USER_AGENT") or "reps-scraper/0.1"
    token = get_token(session)
    if token:
        session.headers["Authorization"] = f"bearer {token}"
    else:
        print("Pas d'identifiants : utilisation des pages .json publiques.", file=sys.stderr)

    raw = fetch_posts(session, args.subreddit, args.sort, args.time, args.limit)
    posts = [{
        "id": d["id"], "title": d["title"], "author": d.get("author"), "score": d["score"],
        "num_comments": d["num_comments"], "created_utc": d["created_utc"],
        "url": d.get("url"), "permalink": "https://www.reddit.com" + d["permalink"],
        "selftext": d.get("selftext"),
    } for d in raw]

    for post in posts[:args.comments]:
        data = get(session, f"/comments/{post['id']}", limit=500)
        post["comments"] = flatten_comments(data[1]["data"]["children"])

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = args.out / f"{args.subreddit}-{args.sort}-{stamp}.json"
    path.write_text(json.dumps(posts, ensure_ascii=False, indent=2))
    print(f"{len(posts)} posts écrits dans {path}")


if __name__ == "__main__":
    main()
