# reps

Scraper Reddit basé sur [URS](https://github.com/JosephLai241/URS) (Universal Reddit Scraper, licence MIT), qui utilise l'API officielle via PRAW. URS est inclus comme sous-module dans `vendor/URS`, figé sur un commit précis.

## Ce que fait URS

- Scraper un subreddit (hot, new, top, controversial, recherche par mot-clé)
- Scraper un utilisateur Reddit (posts, commentaires, karma)
- Récupérer les commentaires d'un post sous forme d'arbre
- Suivre un subreddit en direct (livestream)
- Fréquence de mots et nuage de mots sur les résultats
- Export JSON (par défaut) ou CSV

## Installation

Prérequis : Python 3.11+, [Poetry](https://python-poetry.org/docs/#installation), [Rust](https://rustup.rs).

```bash
git clone --recurse-submodules https://github.com/saidhepl/reps
cd reps
./scripts/install.sh
```

## Identifiants Reddit

1. Va sur https://www.reddit.com/prefs/apps et crée une app de type **script**.
2. Copie l'identifiant (sous le nom de l'app) et le secret dans `.env` (créé par le script d'installation à partir de `.env.example`).
3. Renseigne aussi ton pseudo et ton mot de passe Reddit.

`.env` est ignoré par git.

## Utilisation

```bash
./scripts/scrape.sh -h                      # aide complète
./scripts/scrape.sh --check                 # vérifie les identifiants et le quota API
./scripts/scrape.sh -r france h 25          # 25 posts "hot" de r/france
./scripts/scrape.sh -r france s "IA" --csv  # recherche "IA" dans r/france, export CSV
./scripts/scrape.sh -u spez 10              # 10 éléments du profil u/spez
./scripts/scrape.sh -c https://www.reddit.com/r/... 0   # tous les commentaires d'un post
```

Les résultats arrivent dans `scrapes/<date>/`.

## Mettre à jour URS

```bash
git -C vendor/URS pull origin master
git add vendor/URS && git commit -m "Met à jour URS"
```

## Scraper léger (sans URS)

`scripts/reddit_scrape.py` n'a besoin que de Python et `requests`, et seulement de `CLIENT_ID` / `CLIENT_SECRET` (pseudo et mot de passe facultatifs). Il passe par l'API OAuth officielle, ce qui le fait aussi tourner depuis un serveur ou le cloud, où les endpoints `.json` publics de Reddit sont bloqués.

```bash
python3 scripts/reddit_scrape.py python --sort top --time week --limit 50 --comments 5
```

Résultat : `scrapes/<subreddit>-<tri>-<date>.json`.
