#!/usr/bin/env python3
import json
import re
import urllib.request
import os
import subprocess

URLS = [
    # 🆓 AdBlock 规则下载链接
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bilibili.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/wechat.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/weibo.yml"
]

OUTPUT_DIR = "rules"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "block.json")  # JSON 文件
OUTPUT_SRS = os.path.join(OUTPUT_DIR, "block.srs")    # 二进制 SRS 文件

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


# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 下载并解析域名
for url in URLS:
    print(f"Downloading: {url}")
    with urllib.request.urlopen(url) as r:
        text = r.read().decode("utf-8", errors="ignore")
        for line in text.splitlines():
            d = extract(line)
            if d:
                domains.add(d)

# 构建 sing-box rule-set v3 JSON
output = {
    "version": 3,
    "rules": [
        {
            "domain_suffix": sorted(domains)
        }
    ]
}

# 写入 JSON 文件
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Done: {len(domains)} domains written to {OUTPUT_JSON}")

# 调用 sing-box 编译生成 SRS
print(f"Compiling SRS to {OUTPUT_SRS} ...")
subprocess.run(["sing-box", "rule-set", "compile", OUTPUT_JSON, "-o", OUTPUT_SRS], check=True)

print(f"Done: SRS written to {OUTPUT_SRS}")
