#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算 favicon 的 FOFA / Shodan 通用 icon_hash。

算法：icon_hash = mmh3_32(base64.encodebytes(favicon_bytes))
即先把图标原始字节做带换行的 Base64 编码，再取 MurmurHash3 x86_32（有符号）。

用法：
    python icon_hash.py https://octodex.github.com/favicon.ico
"""
import base64
import struct
import sys
import urllib.request


def mmh3_x86_32(data: bytes, seed: int = 0) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h1 = seed
    nblocks = len(data) // 4
    for i in range(nblocks):
        k1 = struct.unpack_from("<I", data, i * 4)[0]
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[nblocks * 4:]
    k1 = 0
    if len(tail) == 3:
        k1 ^= tail[2] << 16
    if len(tail) >= 2:
        k1 ^= tail[1] << 8
    if len(tail) >= 1:
        k1 ^= tail[0]
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
    h1 ^= len(data)
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1 - (1 << 32) if h1 >= 1 << 31 else h1


def icon_hash(url: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    return mmh3_x86_32(base64.encodebytes(raw))


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://octodex.github.com/favicon.ico"
    value = icon_hash(target)
    print(f"# {target}")
    print(f'icon_hash="{value}"')
