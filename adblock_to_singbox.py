#!/usr/bin/env python3
import json
import re
import urllib.request
import os
import subprocess
import yaml

# 🆓 AdBlock 规则下载链接
URLS = [
    {"url": "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bilibili.yml", "name": "bilibili"},
    {"url": "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/wechat.yml", "name": "wechat"},
    {"url": "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/weibo.yml", "name": "weibo"}
]

OUTPUT_DIR = "rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 确保输出目录存在

def extract_from_yaml(yaml_data):
    """从 YAML 数据中提取域名"""
    domains = set()
    if 'rules' in yaml_data:
        for line in yaml_data['rules']:
            # 解析符合 AdBlock 格式的域名
            if line.startswith("||"):
                domain = line[2:]
            elif line.startswith("|"):
                domain = line[1:]
            else:
                continue

            if domain.endswith("^"):
                domain = domain[:-1]

            if "/" in domain or "?" in domain:
                continue

            if re.fullmatch(r"[A-Za-z0-9.-]+", domain):
                domains.add(domain.lower())
    return domains

# 下载并解析域名
for item in URLS:
    url = item["url"]
    name = item["name"]

    print(f"Downloading: {url}")
    with urllib.request.urlopen(url) as r:
        yaml_data = yaml.safe_load(r.read())
        domains = extract_from_yaml(yaml_data)

        # 生成 JSON 文件
        output_json = os.path.join(OUTPUT_DIR, f"{name}.json")
        output = {
            "version": 3,
            "rules": [
                {
                    "domain_suffix": sorted(domains)
                }
            ]
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Done: {len(domains)} domains written to {output_json}")

        # 调用 sing-box 编译生成 SRS
        output_srs = os.path.join(OUTPUT_DIR, f"{name}.srs")
        print(f"Compiling SRS to {output_srs} ...")
        subprocess.run(["sing-box", "rule-set", "compile", output_json, "-o", output_srs], check=True)

        print(f"Done: SRS written to {output_srs}")
