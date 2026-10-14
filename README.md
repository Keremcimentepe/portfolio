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
deploy/        Caddy site block used on the server
```

## Change something

1. Edit `content/en.toml` and `content/tr.toml` (keep both languages in step).
2. Build: `python3 build.py` (Python 3.11+, standard library only).
3. Preview: `python3 -m http.server 8000 --directory public` and open http://localhost:8000
4. Commit **including `public/`** and push. CI fails if `public/` is out of date.

To replace the CV, overwrite `static/Kerem-Cimentepe-CV.pdf` and rebuild.

## Update the live site

On the server, one command:

```bash
git -C ~/portfolio pull --ff-only
```

Caddy serves `~/portfolio/public` directly, so no restart is needed.

## Moving to a domain

Change `base_url` (and `taskflow_demo`) in `content/site.toml`, rebuild, commit, pull on the
server, and change the host name in the Caddy site block.
