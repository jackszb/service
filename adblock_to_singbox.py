#!/usr/bin/env python3
import json
import re
import urllib.request
import os
import subprocess
import yaml

# 🆓 AdBlock 规则下载链接
URLS = [
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bilibili.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/wechat.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/weibo.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/xiaohongshu.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/iqiyi.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/amazon.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/ebay.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/amazon_streaming.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/disneyplus.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/apple_streaming.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/cloudflare.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/youtube.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/whatsapp.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/twitter.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/facebook.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/telegram.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/spotify.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/reddit.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/tiktok.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/discord.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/dropbox.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/chatgpt.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/instagram.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/netflix.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/line.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/vimeo.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/linkedin.yml",
    "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/pinterest.yml"
]

# 输出目录
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
for url in URLS:
    name = url.split("/")[-1].split(".")[0]  # 从 URL 中提取文件名（不带扩展名）

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
