#!/usr/bin/env python3
"""Copies the current R-VPN Lite release from the main download site to the Releases of this repository.

Runs every hour in GitHub Actions. The site's version.json lists every file with its SHA-256 and size. When it names
a build that the release here does not have yet, every file listed in the site's SHA256SUMS is downloaded, checked
against SHA256SUMS and version.json, and published as release v<version>: a draft gets all files first and becomes
"Latest" only when complete, so the releases/latest/download/<file> links never point at a half-uploaded release.
A new build of the same version replaces the files of its release. Afterwards version.json is committed to main:
a stable raw link, and the commit keeps the hourly schedule alive (GitHub stops schedules in public repositories
without activity for 60 days).

DRY_RUN=1: download and check only, nothing is published."""
import hashlib
import json
import os
import pathlib
import subprocess
import time
import urllib.request

BASE = os.environ.get("RVPN_BASE", "https://download.plus.rvpn.space/lite").rstrip("/")
DIST = pathlib.Path(os.environ.get("DIST", "dist"))
DRY = os.environ.get("DRY_RUN") == "1"
REPO = os.environ.get("GITHUB_REPOSITORY", "Nexxus604/rvpn-lite")

ROWS = {  # version.json key -> system, in the order of the download page
    "android": "Android",
    "windows": "Windows 10 и 11 (x64)",
    "linux": "Ubuntu 24.04 и новее (64 бит)",
    "linux_rpm": "Fedora 39 и новее, AlmaLinux и Rocky 10 (64 бит)",
}


def fetch(url, dest=None):
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rvpn-lite-github-mirror",
                                                       "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                if dest is None:
                    return resp.read()
                with open(dest, "wb") as out:
                    while chunk := resp.read(1 << 20):
                        out.write(chunk)
                return None
        except OSError as exc:  # URLError, HTTPError, timeouts
            last = exc
            time.sleep(15 * (attempt + 1))
    raise SystemExit(f"cannot fetch {url}: {last}")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as src:
        while chunk := src.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def run(*cmd, check=True):
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def gh(*args, check=True):
    for attempt in range(3):
        res = run("gh", *args, check=False)
        if res.returncode == 0 or not check:
            return res
        print(f"gh {args[:2]} failed (try {attempt + 1}): {res.stderr.strip()[:300]}")
        time.sleep(20)
    raise SystemExit(f"gh {' '.join(args[:3])} failed")


def notes(version, build, tag, keys, marker):
    lines = [f"R-VPN Lite {version} (сборка {build}) — копия файлов с основного сайта загрузки {BASE}/", "",
             "| Система | Файл |", "| --- | --- |"]
    for key, system in ROWS.items():
        if key in keys:
            lines.append(f"| {system} | [{keys[key]}](https://github.com/{REPO}/releases/download/{tag}/{keys[key]}) |")
    for key, name in keys.items():
        if key not in ROWS and not key.startswith("router_"):
            lines.append(f"| {key} | `{name}` |")
    if any(key.startswith("router_") for key in keys):
        lines.append("| Роутеры с OpenWrt 24.10 и 25.12 | `R-VPN-Lite-router_<процессор>.apk` (25.12) "
                     "или `.ipk` (24.10), установка — в README |")
    lines += ["", f"Как войти и как поставить на роутер — в [README](https://github.com/{REPO}#readme). "
              "Проверка файлов: `sha256sum -c SHA256SUMS --ignore-missing`.", "", marker]
    return "\n".join(lines) + "\n"


def main():
    raw = fetch(f"{BASE}/version.json")
    manifest = json.loads(raw)
    version, build = str(manifest["version"]), int(manifest["build"])
    tag, marker = f"v{version}", f"<!-- build:{build} -->"
    files = {f["name"]: f for f in manifest["files"].values()}
    keys = {key: f["name"] for key, f in manifest["files"].items()}

    view = gh("release", "view", tag, "--json", "body,isDraft,assets", check=False)
    release = json.loads(view.stdout) if view.returncode == 0 else None
    if release and marker in (release.get("body") or "") and not release.get("isDraft"):
        print(f"{tag} (build {build}) is already published here")
        return

    sums_raw = fetch(f"{BASE}/SHA256SUMS")
    sums = {}
    for line in sums_raw.decode().splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1].lstrip("*")] = parts[0]
    bad = [name for name, f in files.items() if sums.get(name) != f["sha256"]]
    if bad:
        if fetch(f"{BASE}/version.json") != raw:
            print("the site changed during this run; the next run picks up the new version")
            return
        raise SystemExit(f"version.json and SHA256SUMS of the site disagree: {bad}")

    DIST.mkdir(parents=True, exist_ok=True)
    assets = []
    for name, digest in sums.items():
        path = DIST / name
        fetch(f"{BASE}/{name}", path)
        size = path.stat().st_size
        if sha256(path) != digest or (name in files and size != files[name]["size"]):
            if fetch(f"{BASE}/version.json") != raw:
                print("the site changed during this run; the next run picks up the new version")
                return
            raise SystemExit(f"{name}: does not match SHA256SUMS / version.json of the site")
        assets.append(str(path))
        print(f"ok {name} {size}")
    (DIST / "SHA256SUMS").write_bytes(sums_raw)
    (DIST / "version.json").write_bytes(raw)
    assets += [str(DIST / "SHA256SUMS"), str(DIST / "version.json")]
    names = {pathlib.Path(a).name for a in assets}
    print(f"{tag} build {build}: {len(assets)} files checked")
    if DRY:
        print("DRY_RUN: nothing published")
        return

    title, body = f"R-VPN Lite {version}", notes(version, build, tag, keys, marker)
    if release is None:
        gh("release", "create", tag, "--draft", "--target", "main", "--title", title, "--notes", body)
    gh("release", "upload", tag, *assets, "--clobber")
    for asset in (release or {}).get("assets", []):
        if asset["name"] not in names:  # a file the new build no longer has
            gh("release", "delete-asset", tag, asset["name"], "--yes")
    gh("release", "edit", tag, "--draft=false", "--latest", "--title", title, "--notes", body)
    print(f"published {tag} build {build}")

    pathlib.Path("version.json").write_bytes(raw)
    run("git", "add", "version.json")
    if run("git", "diff", "--cached", "--quiet", check=False).returncode != 0:
        run("git", "-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", f"R-VPN Lite {version} (build {build})")
        run("git", "push")


if __name__ == "__main__":
    main()
