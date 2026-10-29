# FOFA 自然语言 → 查询语句 答卷（参赛包 pkg-08e82c8d）

本仓库是一份**FOFA 网络空间测绘比赛**的正式答卷归档：把 100 条中文自然语言资产检索需求，转换成一条条合法、完整、可执行的 FOFA Query。

| 项 | 值 |
| --- | --- |
| 选手名称 | 李佳阳 |
| 参赛包编号 | `pkg-08e82c8d` |
| 题目集 | 100 题（M001–M100） |
| 答卷文件 | [`答案.json`](答案.json) |
| 题号对照 | [`notes/题目与答案对照.md`](notes/题目与答案对照.md) |

## 交付物

- `答案.json`：符合上传要求的答卷（UTF-8 with BOM，字段 `选手名称` / `参赛包编号` / `答案[]`，题号与题目集完全一致、无缺题重复）。
- `notes/题目与答案对照.md`：100 条「题干 → 查询语句」逐条对照，便于人工复核。
- `scripts/icon_hash.py`：M097（网站图标相同资产）所用 favicon mmh3 哈希计算脚本，可复现。
- `scripts/validate_answer.py`：答卷自检脚本（题号完整性、JSON 结构）。

## 方法

不使用训练数据，全部靠**语义拆解 + FOFA 官方字段语义**落成查询：

1. **读包**：从 `题目.json` 取题号与题干，`答案模板.json` 保留参赛包编号与题号顺序。
2. **拆解需求维度**：定位（ip / 网段 / country / region / city / asn / org）、服务（protocol / base_protocol / port / banner）、Web（title / header / body / status_code / js_name）、证书（cert.*）、指纹与标签（app / product / product.version / category / cloud_name / fid / icon_hash / jarm / tls.ja3s）、时间（after / before / cert.not_after）。
3. **套用官方字段名**：以 FOFA 官方 API 字段表与查询语法文档为准（见下节），避免"想当然"的字段名。
4. **布尔改写**：把"任一命中"写成 `||`，"排除/不等于"写成 `!=`，把 "A 或（B 且 C）" 这类嵌套用括号显式分组。
5. **可执行性优先**：每条只输出**一条** Query，不加解释、不加 Markdown；确实无法表达的填固定答案。
6. **自检**：题号集合与 `题目.json` 做全等比较，避免整份被拒。

### 关键字段名校正（易错点）

| 需求语义 | 正确字段 | 常见错误写法 |
| --- | --- | --- |
| 证书序列号 | `cert.sn` | `cert.serial_number` |
| 证书颁发者 ≠ 持有者 | `cert.is_equal=false` | 误判为"不可转换" |
| 证书与访问域名不匹配 | `cert.is_match=false` | `cert.match` |
| 服务端 TLS 指纹 | `tls.ja3s` | `ja3s` |
| 传输层协议（TCP/UDP） | `base_protocol` | 用 `protocol="tcp"` |
| 产品版本 / 产品门类 | `product.version` / `category` | `version` / `product.category` |
| 资产更新时间 | `after` / `before` | `lastupdatetime`（仅返回字段） |
| 是否绑域名 / 是否 IPv6 / 是否云 | `is_domain` / `is_ipv6` / `is_cloud` | `domain!=""` / `ip` 正则 |
| 蜜罐、仿冒站群 | `is_honeypot` / `is_fraud` | 关键词排除 |

其它常用：`app`、`cloud_name`、`cname`、`fid`、`icon_hash`、`header_hash`、`body_hash`、`banner_hash`、`jarm`、`tls.version`、`cert.issuer.org/cn`、`cert.subject.org/cn`、`cert.domain`、`cert.is_valid`、`cert.not_after`、`status_code`、`js_name`、`icp`。

## 判定为「不可转换」的 5 题

固定答案：`该需求不能直接转换为FOFA搜索语句`

| 题号 | 原因 |
| --- | --- |
| M091 | 端口 `1000000` 超出合法端口范围（0–65535） |
| M092 | `1.2.3.4.5` 不是合法 IP/网段 |
| M093 | 同一字段要求"等于 US 且不等于 US"，逻辑自相矛盾（结果恒为空） |
| M094 | "最安全的网站"缺少可判定的客观特征 |
| M095 | 需要容器运行时监控数据与权限，不属于网络空间测绘可见面 |

## 几处已知取舍

- **M080**（47.96.0.1–47.96.0.5 闭区间）：FOFA 无区间语法，用 5 个 `ip=` 的 `||` 精确表达，避免用 `/29` 引入 .0/.6/.7。
- **M082**（证书过期时间区间）：用 `cert.not_after>=` / `<=` 表达区间；若平台不接受比较符，可退化为等值形式。
- **M023**（`a.z.163.com` 形态）：用模糊匹配 `host*="?.?.163.com"`，`?` 表示单字符，正好对应"两级各一个字符"。
- **M076**（`.com` 前恰好四个字符）：用 `domain*="????.com"` 表达。
- **M051**（标题"完整为 WHM 登录"）：用 `title="WHM"` 保召回，未强制全等。
- **M013**（更新时间晚于 2026-08-01）：`after="2026-08-01"` 取的是资产更新时间维度。

## 复现

```bash
# 1. 自检答卷结构（需要题目.json）
python scripts/validate_answer.py 答案.json 题目.json

# 2. 复算 M097 的 favicon 哈希
python scripts/icon_hash.py https://octodex.github.com/favicon.ico
```

> 说明：本仓库仅用于比赛答卷归档与方法复盘，所有 Query 均面向公开测绘数据，不含任何账号、密钥或未授权数据。请遵守 FOFA 服务条款，仅用于合法授权的安全研究。
