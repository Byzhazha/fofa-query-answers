# FOFA 自然语言 → 查询语句 答卷（参赛包 pkg-08e82c8d）

本仓库是一份**FOFA 网络空间测绘比赛**的正式答卷归档：把 100 条中文自然语言资产检索需求，转换成一条条合法、完整、可执行的 FOFA Query。

| 项 | 值 |
| --- | --- |
| 选手名称 | 李佳阳 |
| 参赛包编号 | `pkg-08e82c8d` |
| 题目集 | 100 题（M001–M100） |
| 答卷文件 | [`答案.json`](答案.json) |
| 题号对照 | [`notes/题目与答案对照.md`](notes/题目与答案对照.md) |
| 修订记录 | [v2：2026-10-29 语法修订](#修订记录) |

## 交付物

- `答案.json`：符合上传要求的答卷（UTF-8 with BOM，字段 `选手名称` / `参赛包编号` / `答案[]`，题号与题目集完全一致、无缺题重复）。
- `notes/题目与答案对照.md`：100 条「题干 → 查询语句」逐条对照，便于人工复核。
- `scripts/icon_hash.py`：M097（网站图标相同资产）所用 favicon mmh3 哈希计算脚本，可复现。
- `scripts/validate_answer.py`：答卷自检脚本（题号完整性、JSON 结构、空值、换行）。

## 方法

不依赖训练数据，全部靠**语义拆解 + FOFA 官方字段语义**落成查询：

1. **读包**：从 `题目.json` 取题号与题干，`答案模板.json` 保留参赛包编号与题号顺序。
2. **拆解需求维度**：定位（`ip` / `country` / `region` / `city` / `asn` / `org`）、服务（`protocol` / `base_protocol` / `port` / `banner`）、Web（`title` / `header` / `body` / `status_code` / `js_name`）、证书（`cert.*`）、指纹与标签（`app` / `product` / `product.version` / `category` / `cloud_name` / `fid` / `icon_hash` / `jarm` / `tls.ja3s`）、时间（`after` / `before` / `cert.not_after.*`）。
3. **套用官方字段名与运算符**：字段与运算符支持范围以 FOFA 官网当前加载的搜索语法表为准（见下节），不用"想当然"的字段名。
4. **布尔改写**：把"任一命中"写成 `||`，"排除/不等于"写成 `!=`，把 "A 或（B 且 C）" 这类嵌套用括号显式分组。
5. **可执行性优先**：每条只输出**一条** Query，不加解释、不加 Markdown；确实无法表达的填固定答案。
6. **自检**：题号集合与 `题目.json` 做全等比较，避免整份被拒。

### 关键字段名校正（易错点）

| 需求语义 | 正确字段 | 常见错误写法 |
| --- | --- | --- |
| 证书序列号（十进制串） | `cert.sn` | `cert.serial_number`；用冒号分隔的十六进制原文 |
| 证书颁发者 ≠ 持有者 | `cert.is_equal=false` | 误判为"不可转换" |
| 证书与访问域名不匹配 | `cert.is_match=false` | `cert.match` |
| 证书是否过期 | `cert.is_expired=false` | 用 `cert.is_valid=true` 代替"未过期" |
| 证书到期时间比较 | `cert.not_after.after` / `cert.not_after.before` | `cert.not_after>=` / `<=`（不在运算符集内） |
| 证书持有者根域名 | `cert.domain` | 与 `cert.subject.cn`（通用名称）混用 |
| 服务端 TLS 指纹 | `tls.ja3s` | `ja3s` |
| 传输层协议（TCP/UDP） | `base_protocol` | 用 `protocol="tcp"` |
| 产品版本 / 产品门类 | `product.version` / `category` | `version` / `product_category` |
| 资产更新时间 | `after` / `before` | `lastupdatetime`（仅返回字段） |
| 资产类型（网站/协议） | `type="subdomain"` / `type="service"` | 用 `protocol` 代替类型 |
| CNAME 根域 | `cname_domain` | `cname`（完整别名记录） |
| 是否绑域名 / 是否 IPv6 / 是否云 | `is_domain` / `is_ipv6` / `is_cloud` | `domain!=""` / IP 正则 |
| 蜜罐、仿冒站群 | `is_honeypot` / `is_fraud` | 关键词排除 |

**运算符语义（官方原文）**

- `=`：匹配；`=""` 时匹配「字段不存在或值为空」。
- `==`：完全匹配；`==""` 时匹配「字段存在且值为空」。题干出现"完整为/精确为"时用 `==`。
- `!=`：不匹配；`!=""` 时匹配「值不为空」。
- `*=`：模糊匹配，支持 `*` 与 `?`（`?` 匹配单个字符）。
- 并非所有字段都支持 `!=`：例如 `app` 仅支持 `=`，`is_domain/is_ipv6/is_cloud/type/after/before` 也只有 `=`。

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

- **M080**（47.96.0.1–47.96.0.5 闭区间）：FOFA 无区间语法，用 5 个 `ip=` 的 `||` 精确表达，避免 `/29` 引入 .0/.6/.7。
- **M023**（`a.z.163.com` 形态）：`host*="?.?.163.com"`，`?` 匹配单字符，正好对应"两级各一个字符"。
- **M076**（`.com` 前恰好四个字符）：`domain*="????.com"`；同时按官方语义用 `title==""`（存在且为空）而非 `title=""`。
- **M082**：证书到期区间改用官方比较语法 `cert.not_after.after` / `.before`；官方示例只给到日期粒度，**秒级时间能否识别需在比赛环境确认**。
- **M072**：WAF 排除改用 `product!="WAF"`，因为 `app` 官方仅支持 `=`，写 `app!="WAF"` 会导致语句不可执行。
- **M030**：题干写 `Set-Cookie:PHPSESSID`，但真实响应头为 `Set-Cookie: PHPSESSID=...`（冒号后有空格），故用 `header="PHPSESSID"` 保命中；若要贴合字面可改 `header="Set-Cookie: PHPSESSID"`。
- **M005**（域名里带 vpn）：按"根域名含 vpn"理解，用 `domain="vpn"`；若需覆盖仅子域含 vpn 的主机，可改 `host="vpn"`。
- **M034**（持有者名称是 apple.com、域名不是 apple.com）：`cert.subject.cn="apple.com"` 用关键词匹配而非 `==`，以覆盖 `*.apple.com` 等常见形态。
- **M051 / M070**：题干要求"标题完整为/完整等于"，故用 `==` 完全匹配；M051 的标题文本是否确为中文"WHM 登录"仍需实测。
- **M039 / M038**：均落到官方"证书持有者根域名"字段 `cert.domain`，分别对应"持有者名称根域"和"证书里的根域名"。
- **M013**：`after="2026-08-01"` 取资产更新时间维度。

## 修订记录

### v2 — 2026-10-29 语法修订（13 条）

依据 FOFA 官网搜索语法表（`v5static.fofa.info` 当前加载的语法资源）逐条复核后修订：

| 题号 | v1 | v2 | 原因 |
| --- | --- | --- | --- |
| M082 | `cert.not_after>=` / `<=` | `cert.not_after.after` / `.before` | 比较符不在官方运算符集内 |
| M072 | `app!="WAF"` | `product!="WAF"` | `app` 仅支持 `=` |
| M100 | 冒号十六进制序列号 | 十进制 `cert.sn` | 官方示例为十进制整数字符串 |
| M046 | 无类型限制 | 追加 `type="subdomain"` | 题干"网站类资产"对应资产类型字段 |
| M058 | `cname` | `cname_domain` | 题干指定"CNAME 根域" |
| M033 / M043 | `cert.is_valid=true` | `cert.is_expired=false` | 题干"未过期"对应过期状态字段 |
| M051 / M070 | `title="…"` | `title=="…"` | 题干"完整为/完整等于" |
| M088 | `server="Apache"` | `server=="Apache"` | 题干"精确为" |
| M076 / M086 | `title=""` | `title==""` | 官方：`=""` 含字段缺失，`==""` 才是"存在且为空" |
| M039 | `cert.subject.cn="qq.com"` | `cert.domain="qq.com"` | 官方 `cert.domain` 即"证书持有者根域名" |

## 复现

```bash
# 1. 自检答卷结构（需要题目.json）
python scripts/validate_answer.py 答案.json 题目.json

# 2. 复算 M097 的 favicon 哈希
python scripts/icon_hash.py https://octodex.github.com/favicon.ico
```

> 说明：本仓库仅用于比赛答卷归档与方法复盘，所有 Query 均面向公开测绘数据，不含任何账号、密钥或未授权数据。请遵守 FOFA 服务条款，仅用于合法授权的安全研究。
