#!/usr/bin/env python3
import json
import re
import urllib.request
import os

URLS = [
    # 🆓 AdBlock 规则下载链接
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bilibili.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/wechat.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/weibo.yml"
]

OUTPUT_DIR = "rules"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "free.json")

domains = set()

def extract(line: str):
    line = line.strip()

    if not line:
        return None
    if line.startswith(("!", "#", "@@")):
        return None

    if line.startswith("||"):
        d = line[2:]
    elif line.startswith("|"):
        d = line[1:]
    else:
        return None

    if d.endswith("^"):
        d = d[:-1]

    if "/" in d or "?" in d:
        return None

    if re.fullmatch(r"[A-Za-z0-9.-]+", d):
        return d.lower()

    return None


os.makedirs(OUTPUT_DIR, exist_ok=True)

for url in URLS:
    print(f"Downloading: {url}")
    with urllib.request.urlopen(url) as r:
        text = r.read().decode("utf-8", errors="ignore")
        for line in text.splitlines():
            d = extract(line)
            if d:
                domains.add(d)

output = {
    "version": 3,
    "rules": [
        {
            "domain_suffix": sorted(domains)
        }
    ]
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Done: {len(domains)} domains written to {OUTPUT_JSON}")
