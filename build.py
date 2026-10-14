#!/usr/bin/env python3
"""Build the portfolio into ./public from ./content (TOML), ./src and ./static.

Standard library only (Python 3.11+). Run:  python3 build.py
The output is deterministic, so CI can check that public/ is up to date.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tomllib
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
SRC = ROOT / "src"
STATIC = ROOT / "static"
OUT = ROOT / "public"


def load(name: str) -> dict:
    with open(CONTENT / name, "rb") as fh:
        return tomllib.load(fh)


def e(text: str) -> str:
    return escape(str(text), quote=True)


def fingerprint(src: Path, dest_dir: Path) -> str:
    data = src.read_bytes()
    digest = hashlib.sha256(data).hexdigest()[:10]
    name = f"{src.stem}.{digest}{src.suffix}"
    (dest_dir / name).write_bytes(data)
    return f"/assets/{name}"


THEME_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="12" r="8.25" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    '<path d="M12 3.75a8.25 8.25 0 0 1 0 16.5z" fill="currentColor"/></svg>'
)


def head(site: dict, c: dict, assets: dict, *, noindex: bool = False) -> str:
    m = c["meta"]
    base = site["base_url"].rstrip("/")
    url = base + m["path"]
    other_locale = "tr_TR" if m["lang"] == "en" else "en_US"
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site["name"],
        "url": url,
        "email": "mailto:" + site["email"],
        "affiliation": {"@type": "CollegeOrUniversity", "name": "Gazi University"},
        "address": {"@type": "PostalAddress", "addressLocality": "Ankara", "addressCountry": "TR"},
        "sameAs": [site["github"], site["linkedin"]],
        "knowsAbout": ["C#", "ASP.NET Core", "Entity Framework Core", "PostgreSQL", "React", "TypeScript", "Docker"],
    }
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{e(m['title'])}</title>",
        f'<meta name="description" content="{e(m["description"])}">',
    ]
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    else:
        lines += [
            f'<link rel="canonical" href="{e(url)}">',
            f'<link rel="alternate" hreflang="en" href="{e(base)}/">',
            f'<link rel="alternate" hreflang="tr" href="{e(base)}/tr/">',
            f'<link rel="alternate" hreflang="x-default" href="{e(base)}/">',
        ]
    lines += [
        '<meta name="color-scheme" content="light dark">',
        '<meta name="theme-color" content="#f7f8fa" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#0f151e" media="(prefers-color-scheme: dark)">',
    ]
    if not noindex:
        lines += [
            '<meta property="og:type" content="profile">',
            '<meta property="profile:first_name" content="Kerem">',
            '<meta property="profile:last_name" content="Çimentepe">',
            f'<meta property="og:site_name" content="{e(site["name"])}">',
            f'<meta property="og:title" content="{e(m["title"])}">',
            f'<meta property="og:description" content="{e(m["description"])}">',
            f'<meta property="og:url" content="{e(url)}">',
            f'<meta property="og:locale" content="{e(m["locale"])}">',
            f'<meta property="og:locale:alternate" content="{other_locale}">',
            f'<meta property="og:image" content="{e(base)}/{e(m["og_image"])}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{e(m["og_image_alt"])}">',
            '<meta name="twitter:card" content="summary_large_image">',
        ]
    lines += [
        '<link rel="icon" href="/favicon.ico" sizes="32x32">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="preload" href="/assets/fonts/inter-4.0-400.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{assets["css"]}">',
        f'<script src="{assets["theme"]}"></script>',
        f'<script src="{assets["js"]}" defer></script>',
    ]
    if not noindex:
        ld = json.dumps(person, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        lines.append(f'<script type="application/ld+json">{ld}</script>')
    return "\n".join(lines)


def header(c: dict, other_href: str, other_lang: str) -> str:
    ui = c["ui"]
    nav = "".join(f'<li><a href="#{e(n["id"])}">{e(n["label"])}</a></li>' for n in ui["nav"])
    return f"""<a class="skip" href="#main">{e(ui["skip"])}</a>
<header class="site-header wrap">
  <nav class="site-nav" aria-label="{e(ui["nav_label"])}"><ul>{nav}</ul></nav>
  <div class="header-tools">
    <a class="lang" href="{e(other_href)}" hreflang="{other_lang}" lang="{other_lang}">{e(ui["lang_switch"])}</a>
    <button class="theme-toggle" type="button" data-label-dark="{e(ui["theme_to_dark"])}" data-label-light="{e(ui["theme_to_light"])}" aria-label="{e(ui["theme_to_dark"])}">{THEME_ICON}</button>
  </div>
</header>"""


def hero(site: dict, c: dict) -> str:
    ui, h = c["ui"], c["hero"]
    facts = "".join(f"<div><dt>{e(f['term'])}</dt><dd>{e(f['value'])}</dd></div>" for f in h["facts"])
    return f"""<section class="hero" aria-labelledby="name">
  <h1 id="name">{e(site["name"])}</h1>
  <p class="lead">{e(h["lead"])}</p>
  <dl class="facts">{facts}</dl>
  <div class="actions">
    <a class="btn btn-primary" href="/{e(site["cv_file"])}" download>{e(ui["cv"])} <span class="btn-note">{e(ui["cv_note"])}</span></a>
    <a class="btn btn-secondary" href="mailto:{e(site["email"])}">{e(ui["email_cta"])}</a>
    <span class="text-links"><a href="{e(site["github"])}">GitHub</a><a href="{e(site["linkedin"])}">LinkedIn</a></span>
  </div>
</section>"""


def section(sid: str, heading: str, body: str) -> str:
    return f"""<section id="{sid}" class="section" aria-labelledby="{sid}-h">
  <h2 id="{sid}-h">{e(heading)}</h2>
  <div class="section-body">
{body}
  </div>
</section>"""


def about(c: dict) -> str:
    a = c["about"]
    paras = "".join(f'<p class="about-intro">{e(p)}</p>' for p in a["body"])
    langs = "".join(
        f"<div><dt>{e(l['name'])}</dt><dd class=\"muted\">{e(l['level'])}</dd></div>" for l in a["languages"]
    )
    body = f"""<div class="prose">{paras}</div>
<div class="subgrid">
  <div class="edu">
    <h3 class="minor">{e(a["education_heading"])}</h3>
    <p>{e(a["degree"])}</p>
    <p class="muted tnum">{e(a["dates"])}</p>
    <p class="muted tnum">{e(a["gpa"])}</p>
    <p class="muted">{e(a["coursework"])}</p>
  </div>
  <div>
    <h3 class="minor">{e(a["languages_heading"])}</h3>
    <dl class="lang-list">{langs}</dl>
  </div>
</div>"""
    return section(c["ui"]["nav"][0]["id"], a["heading"], body)


def route(f: dict) -> str:
    return f"""<figure class="route-figure">
  <div class="route" aria-hidden="true">
    <span class="node">{e(f["route_browser"])}</span>
    <span class="edge"><span class="edge-label">HTTPS</span></span>
    <span class="node node-hub">Caddy</span>
    <span class="joint"></span>
    <span class="branches">
      <span class="branch"><span class="edge edge-entry"><code class="edge-label">/api/*</code></span><span class="node">{e(f["route_api"])}</span><span class="edge edge-inner"></span><span class="node">{e(f["route_db"])}</span></span>
      <span class="branch"><span class="edge edge-entry"><code class="edge-label">/*</code></span><span class="node">{e(f["route_web"])}</span></span>
    </span>
  </div>
  <figcaption>{e(f["route_caption"])}</figcaption>
</figure>"""


def projects(site: dict, c: dict) -> str:
    p = c["projects"]
    f = p["featured"]
    details = "".join(f"<div><dt>{e(d['term'])}</dt><dd>{e(d['text'])}</dd></div>" for d in f["details"])
    others = []
    for o in p["others"]:
        pts = "".join(f"<li>{e(x)}</li>" for x in o["points"])
        others.append(
            f"""<article class="project">
  <div class="project-head"><h3>{e(o["name"])}</h3><p class="project-kind">{e(o["kind"])}</p></div>
  <p class="stack">{e(o["stack"])}</p>
  <ul class="points">{pts}</ul>
</article>"""
        )
    body = f"""<article class="project-featured">
  <div class="project-head"><h3>{e(f["name"])}</h3><p class="project-kind">{e(f["kind"])}</p></div>
  <p class="project-summary">{e(f["summary"])}</p>
  <p class="stack">{e(f["stack"])}</p>
  <p class="project-links"><a href="{e(site["taskflow_demo"])}">{e(f["demo_label"])}</a><a href="{e(site["taskflow_code"])}">{e(f["code_label"])}</a><span class="note">{e(f["code_note"])}</span></p>
  {route(f)}
  <dl class="details">{details}</dl>
</article>
{"".join(others)}
<p class="more"><a href="{e(site["github"])}">{e(c["ui"]["more_github"])}</a></p>"""
    return section(c["ui"]["nav"][1]["id"], p["heading"], body)


def skills(c: dict) -> str:
    s = c["skills"]
    rows = "".join(f"<div><dt>{e(g['name'])}</dt><dd>{e(g['items'])}</dd></div>" for g in s["groups"])
    return section(c["ui"]["nav"][2]["id"], s["heading"], f'<dl class="skills">{rows}</dl>')


def contact(site: dict, c: dict) -> str:
    ui, k = c["ui"], c["contact"]
    body = f"""<p class="prose">{e(k["body"])}</p>
<a class="email-big" href="mailto:{e(site["email"])}">{e(site["email"])}</a>
<div class="contact-actions">
  <button class="btn btn-secondary copy-btn" type="button" data-copy="{e(site["email"])}" data-done="{e(ui["copied"])}" hidden>{e(ui["copy"])}</button>
  <span class="copy-status sr-only" aria-live="polite"></span>
  <a href="{e(site["linkedin"])}">LinkedIn</a>
  <a href="{e(site["github"])}">GitHub</a>
  <a href="/{e(site["cv_file"])}" download>{e(ui["cv"])}</a>
</div>"""
    return section(c["ui"]["nav"][3]["id"], k["heading"], body)


def footer(site: dict, c: dict) -> str:
    return f"""<footer class="wrap">
  <div class="site-footer">
    <p>© {e(site["name"])}</p>
    <p>{e(c["ui"]["footer_privacy"])}</p>
  </div>
</footer>"""


def page(site: dict, c: dict, assets: dict) -> str:
    lang = c["meta"]["lang"]
    other_lang = "tr" if lang == "en" else "en"
    other_href = "/tr/" if lang == "en" else "/"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
{head(site, c, assets)}
</head>
<body>
{header(c, other_href, other_lang)}
<main id="main" class="wrap">
{hero(site, c)}
{about(c)}
{projects(site, c)}
{skills(c)}
{contact(site, c)}
</main>
{footer(site, c)}
</body>
</html>
"""


def not_found(site: dict, assets: dict) -> str:
    meta = {"meta": {"title": "404 · " + site["name"], "description": "Page not found / Sayfa bulunamadı", "lang": "en", "path": "/404.html"}}
    return f"""<!doctype html>
<html lang="en">
<head>
{head(site, meta, assets, noindex=True)}
</head>
<body>
<main id="main" class="wrap notfound">
  <h1>Page not found</h1>
  <p>The address may be mistyped, or the page has moved. <a href="/">Go to the home page</a>.</p>
  <h2 lang="tr" class="notfound-tr">Sayfa bulunamadı</h2>
  <p lang="tr">Adres yanlış yazılmış ya da sayfa taşınmış olabilir. <a href="/tr/">Ana sayfaya dön</a>.</p>
</main>
</body>
</html>
"""


def sitemap(site: dict) -> str:
    base = site["base_url"].rstrip("/")
    alts = (
        f'<xhtml:link rel="alternate" hreflang="en" href="{base}/"/>'
        f'<xhtml:link rel="alternate" hreflang="tr" href="{base}/tr/"/>'
    )
    urls = "".join(f"<url><loc>{base}{p}</loc>{alts}</url>" for p in ("/", "/tr/"))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        f"{urls}</urlset>\n"
    )


def main() -> None:
    site = load("site.toml")
    pages = [load("en.toml"), load("tr.toml")]

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    assets_dir = OUT / "assets"
    assets_dir.mkdir(exist_ok=True)
    assets = {
        "css": fingerprint(SRC / "site.css", assets_dir),
        "theme": fingerprint(SRC / "theme.js", assets_dir),
        "js": fingerprint(SRC / "site.js", assets_dir),
    }

    for c in pages:
        target = OUT / c["meta"]["path"].strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(site, c, assets), encoding="utf-8")

    (OUT / "404.html").write_text(not_found(site, assets), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(site), encoding="utf-8")
    base = site["base_url"].rstrip("/")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")

    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in files)
    print(f"Built {len(files)} files into public/ ({total / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
