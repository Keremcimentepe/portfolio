# Portfolio — Kerem Çimentepe

Personal portfolio site in English (`/`) and Turkish (`/tr/`). Static HTML, CSS and a little
JavaScript; no framework, no cookies, no tracking or analytics.

## Layout

```
content/       site.toml (shared links), en.toml, tr.toml   ← edit text here
src/           site.css, site.js, theme.js
static/        CV (PDF), icons, Open Graph images, fonts (Inter, OFL)
build.py       turns content + src + static into public/
public/        generated site that the server serves (committed)
deploy/        Caddy site block and the server update script
```

## Change something

1. Edit `content/en.toml` and `content/tr.toml` (keep both languages in step).
2. Build: `python3 build.py` (Python 3.11+, standard library only).
3. Preview: `python3 -m http.server 8000 --directory public` and open http://localhost:8000
4. Commit **including `public/`** and push. CI fails if `public/` is out of date.

To replace the CV, overwrite `static/Kerem-Cimentepe-CV.pdf` and rebuild.

## How it is served

TaskFlow's Caddy (in the GorevTakip stack) is the only web server on the machine. Its Caddyfile
imports every `/srv/sites/*.caddy`, and the container sees the server folder `~/caddy-sites`
at `/srv/sites` (read-only):

```
~/caddy-sites/
  portfolio/          this repository (Caddy serves only portfolio/public)
  portfolio.caddy  -> portfolio/deploy/portfolio.caddy   (symlink)
```

## Update the live site

On the server, one command:

```bash
bash ~/caddy-sites/portfolio/deploy/update.sh
```

It pulls the latest commit. Page changes are live at once; if `deploy/portfolio.caddy`
changed, it validates the Caddy config first and then reloads it without downtime.

## Addresses

- Portfolio: https://keremcimentepe.com (www redirects here)
- TaskFlow: https://taskflow.keremcimentepe.com (served by the GorevTakip stack)

DNS: A records for `@`, `www` and `taskflow` point to the server's reserved IP (Cloudflare,
"DNS only"). To change the domain, update `content/site.toml` and the host names in
`deploy/portfolio.caddy`, rebuild, commit, push, and run the update command on the server.
