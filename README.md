# edu.cn 根域名与 CERNIC WHOIS 数据

本仓库发布 `edu.cn` 下恰好一层的根域名清单，以及 CERNIC WHOIS 逐域核验结果。最新累计版本更新于 **2026-10-04**：当前 1,439 条全部在当日通过后台 HTTP 重新查询 CERNIC；来源发现历史及原 DNS 证据日期保留。数据面向研究、测绘、资产盘点和可重复分析；DNS 和注册信息具有时效性，不能视为实时状态或注册权属证明。

## 当前数据统计

以下统计依据 [2026-10-04 累计汇总 JSON](data/edu-cn-roots-whois-latest.json)，统计单位为去重后、恰好一层的 `edu.cn` 根域名，表头不计入记录数。

| 指标 | 数量 |
| --- | ---: |
| 根域名总数 | **1,439** |
| 完整英文 WHOIS 记录（`full_record`） | 1,195 |
| 中文注册状态（`cn_status`） | 221 |
| 未找到匹配记录（`not_found`） | 23 |
| 返回登记信息（前两类之和） | 1,416 |
| 最新 CSV 记录数 / 汇总 JSON 记录数 / 逐域 JSON 文件数 | 1,439 / 1,439 / 1,439 |

| WHOIS 实际查询日期 | 记录数 | 完整记录 | 中文注册状态 | 未找到 |
| --- | ---: | ---: | ---: | ---: |
| 2026-10-04 全量 HTTP 复查 | 1,439 | 1,195 | 221 | 23 |
| 合计 | **1,439** | **1,195** | **221** | **23** |

本次最新版本的全部域名已于 2026-10-04 重新查询 WHOIS；历史批次保留此前日期。上述统计不代表当前 DNS 存活数量，本次未重新查询 DNS 或 CERNET 地址关联。

## 快速获取

- [WHOIS 核验 CSV](data/edu-cn-roots-whois-latest.csv)：1,439 行域名记录，UTF-8 BOM 编码，20 列。
- [WHOIS 核验 JSON 汇总](data/edu-cn-roots-whois-latest.json)：同一批 1,439 条记录，含数据集元信息。
- [逐域 JSON 文件](data/whois-json/)：每个根域名一个 JSON，文件名为域名加 `.json`，共 1,439 个。

可直接下载单文件：

```text
https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/edu-cn-roots-whois-latest.csv
https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/edu-cn-roots-whois-latest.json
```

克隆仓库可获得逐域 JSON：

```bash
git clone https://github.com/xingwangzhe/edu-cn-roots.git
```

## 通过 jsDelivr CDN 引用文件

无需克隆仓库，可以通过 jsDelivr 的 GitHub CDN 下载 CSV、汇总 JSON 或逐域 JSON。通用地址格式为：

```text
https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/<仓库内文件路径>
```

### 可直接使用的地址

| 文件 | CDN 地址 |
| --- | --- |
| 单个域名的 WHOIS JSON | [jxutcm.edu.cn.json](https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/whois-json/jxutcm.edu.cn.json) |
| WHOIS 汇总 JSON（含日期、数量和记录） | [edu-cn-roots-whois-latest.json](https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/edu-cn-roots-whois-latest.json) |
| WHOIS CSV | [edu-cn-roots-whois-latest.csv](https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/edu-cn-roots-whois-latest.csv) |

省略版本也可以引用，例如：

```text
https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots/data/whois-json/jxutcm.edu.cn.json
```

建议显式写出 `@main`，明确引用的分支。需要可复现的数据时，将 `@main` 替换为对应的完整 Git commit SHA，固定到一次提交。

### 浏览器读取逐域 JSON

逐域文件以根域名命名。下面的示例会将 `www.jxutcm.edu.cn` 或更多层前缀自动剥离为 `jxutcm.edu.cn`，再读取对应文件：

```javascript
async function readEduCnWhois(input) {
  const domain = input.trim().toLowerCase();
  const validDomain = /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.[a-z]{2,}$/;
  if (domain.length > 253 || !validDomain.test(domain) || !domain.endsWith(".edu.cn")) {
    throw new Error("请输入有效的 edu.cn 域名，例如 jxutcm.edu.cn");
  }

  const rootDomain = domain.split(".").slice(-3).join(".");
  const url = `https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/whois-json/${rootDomain}.json`;
  const response = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!response.ok) {
    throw new Error(`文件请求失败：HTTP ${response.status}；不能据此判断域名未注册`);
  }
  return response.json();
}

const record = await readEduCnWhois("www.jxutcm.edu.cn");
console.log(record);
```

也可以用命令行下载：

```bash
curl --fail --location \
  'https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/whois-json/jxutcm.edu.cn.json'
```

### 更新、缓存与结果边界

- CDN 提供仓库文件的静态副本，不会向 CERNIC 发起实时 WHOIS 查询；当前最新 WHOIS 快照全量采集于 **2026-10-04**；DNS 字段保留其原采集时间。
- `@main` 跟随主分支，但 CDN 缓存可能延迟反映修改，不保证即时更新。汇总文件的日期和数量请读取 `whois_queried`、`count`；逐域文件的字段以该文件实际结构为准。
- `latest` 是当前累计入口，会随发布更新；日期 / 批次文件是固定历史快照，不会自动切换。引用可复现结果时使用完整 commit SHA 或固定批次文件。
- 根域名文件只收录 `edu.cn` 下的一层域名。将子域归一化后，查到的是根域名登记快照，不是子域的独立 WHOIS 记录。
- HTTP 404 表示请求的文件不存在，可能是路径错误或数据集未收录；网络错误也不是登记状态。JSON 中的 `not_found` 表示当次查询没有匹配记录，都不能作为域名未注册或可注册的证明。
- CDN 不可用时，可按相同路径尝试 GitHub Raw，例如 [jxutcm.edu.cn 的原始文件](https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/whois-json/jxutcm.edu.cn.json)。

完整地址语法和缓存说明见 [jsDelivr 官方文档](https://www.jsdelivr.com/documentation#id-github)。公开网页查询可使用 [needhelp WHOIS 工具](https://needhelp.icu/zh/tools/whois-lookup)，查询方式见 [静态快照说明](https://needhelp.icu/zh/blogs/edu-cn-whois-static-lookup)。

## 数据范围与口径

- 仅包含直接位于 `edu.cn` 下的一层域名，例如 `tsinghua.edu.cn`；`www.tsinghua.edu.cn` 等更深子域不单独列为根域名。
- 对发现的子域做根域回卷；不按学校、教育机构或其他组织类型筛选。
- 既收录当前 DNS 可解析的域名，也保留历史 CERNIC 清单中的域名；DNS 消失不构成删除理由。
- 当前版本数量和返回类型见上方“当前数据统计”；统计必须从最新累计数据计算，不能沿用旧快照的分类数量。
- 此前两个增量阶段分别包含原有 1,317 条及新增 122 条。最新阶段已将全部 1,439 条 WHOIS 重新查询为 2026-10-04；历史快照日期不变，未刷新来源观察日期或 DNS 证据。

## 2026-10-04 增量更新

从 [JetBrains/swot 固定提交](https://github.com/JetBrains/swot/tree/b2dee08283cfee0ba43630779b6bf702bf5df76e/lib/domains/cn/edu) 提取根域名并与旧表比较，得到 63 个新增候选。系统 Chrome 逐域查询 CERNIC 后，59 个返回完整记录，4 个返回中文注册状态，全部保留原文及来源。

- [新增候选与 SWOT 文件路径](data/swot-new-candidates-2026-10-04.csv)
- [63 个 CERNIC 页面返回原文](data/cernic-swot-raw-2026-10-04.json)
- [旧批次合并脚本](scripts/merge-swot-20261004.py)：保留作历史说明；schema 2.0 迁移后已禁止运行，当前更新使用生成器或 HTTP 复查脚本。
- 原始 [2026-09-26 CSV](data/edu-cn-roots-whois-2026-09-26.csv) 和 [JSON](data/edu-cn-roots-whois-2026-09-26.json) 保持不变；`data/whois-json/` 是累计逐域集合。

新增记录的 DNS 状态明确标为未检查，A、AAAA、NS 和地址列表关联字段留空。WHOIS 登记的名称服务器及地址仅存于 WHOIS 字段，不代表当前解析结果。

### Hipo 增量与同日版本保留

继续遍历 [Hipo/university-domains-list 固定提交](https://github.com/Hipo/university-domains-list/blob/603e10f51b67c6553b9bca9aecc0db4c2417ed10/world_universities_and_domains.json) 的全部 10,268 条记录，对 `domains` 和 `web_pages` 两个字段提取并回卷域名，共得到 364 个唯一 `edu.cn` 根域，305 个已收录、59 个新增。59 个候选经系统 Chrome 查询 CERNIC，10 个返回完整记录、49 个返回中文注册状态，均保存原文；当前累计 1,439 条。

- [59 个候选及来源机构标签](data/hipo-new-candidates-2026-10-04.csv)
- [完整遍历比较及逐项证据](data/hipo-comparison-2026-10-04.json)
- [59 个 CERNIC 返回原文](data/cernic-hipo-raw-2026-10-04.json)
- [当前累计统计](data/statistics.json)

同一天已存在的 1,380 条 [SWOT 阶段 CSV](data/edu-cn-roots-whois-2026-10-04.csv) 和 [汇总 JSON](data/edu-cn-roots-whois-2026-10-04.json) 保留不覆盖；当前累计结果发布为 `data/edu-cn-roots-whois-latest.csv` 和 `.json`。同日后续更新应保留阶段证据，不能仅用文件名日期假定这是最终版本。

## 2026-10-04 全量后台 HTTP 复查

使用 [refresh_cernic.py](scripts/refresh_cernic.py) 直接请求 CERNIC，并按 GBK 解码。在当前连接路径上，1 / 2 / 4 / 8 并发各查询 24 个样本均成功；测试设置全局请求启动上限 8 次/秒，因此这不是服务端最大容量测试。

| 并发 | 样本请求数 | 吞吐量（次/秒） | 延迟中位数（秒） | 最慢请求（秒） |
| --- | ---: | ---: | ---: | ---: |
| 1 | 24 | 1.60 | 0.67 | 0.86 |
| 2 | 24 | 1.91 | 1.10 | 1.67 |
| 4 | 24 | 1.98 | 2.06 | 3.13 |
| 8 | 24 | 1.98 | 3.87 | 6.03 |

全量选择 **2 并发**：原始采集耗时 **810.84 秒（13.51 分钟）**，最终 1,439 条全部成功解析并校验。两条名称服务器多地址记录（nacta、xjnu）的初始解析错误已修复、重解析并再次 HTTP 核验。连接超时 10 秒、请求总超时 30 秒是客户端设置；没有触发超时，无法由这些结果推定服务端时间上限或绝对最大并发。

- [并发与耗时测试报告](data/cernic-http-benchmark-2026-10-04.json)
- [全量请求耗时、响应哈希、恢复及字段变化报告](data/cernic-http-refresh-20261004-184303.json)
- [复查前完整逐域 JSON 备份](data/history/pre-http-refresh-20261004-184303.json)
- [本次完整阶段 CSV](data/edu-cn-roots-whois-20261004-184303.csv) / [汇总 JSON](data/edu-cn-roots-whois-20261004-184303.json)

所有记录已补齐实际 `raw_text`。结构化差异涉及 808 条名称服务器、32 条网络名、11 条联系人及 6 条域名大小写；差异包含提取修正和此前遗漏的 IPv6，不应全部解释为注册数据库在本次发生变化。空网络名不再误取下一行的 Administrative 标题；联系人兼容合并及单列标题。名称服务器可选 `addresses` 列表保留同一主机全部 IPv4 / IPv6；CSV 也输出完整地址列表。DNS、CERNET 地址关联和发现来源未重新查询。

## 文件格式

### CSV

CSV 使用 UTF-8 BOM，适合常见表格软件直接打开。行首 12 列为域名来源、DNS 和 CERNET 关联信息；末尾 8 列为本次 WHOIS 核验结构化字段。多值记录以分号分隔。

| 字段 | 含义 |
| --- | --- |
| `root_domain` | `edu.cn` 下的一层根域名 |
| `organization_or_record_name` | 汇总表原有的机构名或记录名 |
| `collected_from` | 域名发现来源；可能包含多个来源 |
| `source_last_observed` | 来源中最后观察到该域名的时间（如来源可确定） |
| `current_dns_status` | 采集时对 A、AAAA、NS 查询的状态摘要；`NOERROR` 等是 DNS 响应状态 |
| `A_records` | A 记录 IPv4 地址 |
| `AAAA_records` | AAAA 记录 IPv6 地址 |
| `NS_records` | 权威名称服务器 |
| `CERNIC_WHOIS_status` | 面向阅读的 CERNIC WHOIS 查询结果摘要 |
| `CERNET_address_list_association` | 与 CERNIC/CERNET 地址列表的关联说明；不是注册状态字段 |
| `evidence_hostnames` | 支撑域名收录的证据主机名 |
| `review_notes` | 人工复核注记 |
| `whois_result_type` | 机器可读 WHOIS 响应类别：`full_record`、`cn_status` 或 `not_found` |
| `whois_org_cn` | 响应中提取的中文机构名；无值为空字段 |
| `whois_org_en` | 响应中提取的英文机构名；无值为空字段 |
| `whois_reg_date` | 响应中出现的注册日期，格式 `YYYYMMDD`；不适用时为空 |
| `whois_network_name` | WHOIS 记录中的网络名 |
| `whois_admin_contact` | WHOIS 记录公开的管理联系人文本/handle |
| `whois_ns` | WHOIS 响应中的名称服务器摘要，可能带地址 |
| `whois_queried` | 对该域名进行 CERNIC WHOIS 查询的日期 |

空字段表示本次返回内容没有相应值，不代表已确认该属性不存在。`not_found` 表示本次查询没有匹配记录，不应据此推断域名从未注册。

### 汇总 JSON

已发布历史汇总根对象包含 `dataset`、`schema_version`、`whois_queried`、`source`、`scope`、`count` 和 `records`。新生成汇总使用 `schema_version: "2.0"`，按当前逐域 JSON 重建。最新累计版另含 `updated`、`query_batches` 和 `notes`，说明不同批次的查询日期。`records` 是记录数组；字段与 CSV 一致，JSON 中空字段使用 `""`。将 CSV 导入程序时请注意其 UTF-8 BOM。

### 逐域 JSON

`data/whois-json/<root_domain>.json` 保存 WHOIS 响应的结构化提取，包括 `root_domain`、`type`、组织名称、域名名、网络名、联系人、名称服务器、地址和 `raw_note`。schema 2.0 的必需键均保留，不适用的可空字段为 `null`，列表为 `[]`，`metadata` 中空值为 `""`；只有可选名称服务器扩展字段可能缺省。其中 `type` 与 CSV 的 `whois_result_type` 对应。逐域文件便于按域名加载，但批量分析建议使用 CSV 或汇总 JSON。

逐域 JSON 的维护字段如下，完整约束见 [JSON Schema](schemas/whois-record.schema.json) 和 [贡献指南](CONTRIBUTING.md)：

| 字段 | 说明 |
| --- | --- |
| `schema_version` | 当前为 `"2.0"` |
| `whois_queried` / `source_url` | 实际 CERNIC 查询日期和带根域 query 参数的 URL |
| `raw_text` | GBK 解码后的实际页面文本；当前全部 1,439 条均有值 |
| `metadata` | CSV 第 2–12 列，保留独立的发现来源、DNS 和复核证据 |
| `nameservers[].host` / `ip` | 登记服务器名和主要地址；`ip` 可以是 IPv4 或 IPv6 |
| `nameservers[].ipv6` | 可选主要 IPv6 地址 |
| `nameservers[].addresses` | 可选完整地址列表，用于同一服务器返回多个 IPv4 / IPv6；主要地址必须在列表中 |

### 历史版本与当前入口

| 文件 / 目录 | 用途 |
| --- | --- |
| `data/edu-cn-roots-whois-latest.csv` / `.json` | 当前累计发布数据，1,439 条，全量 WHOIS 查询于 2026-10-04 |
| `data/whois-json/` | 当前可编辑的逐域数据源，不是旧快照目录 |
| `data/edu-cn-roots-whois-2026-09-26.*` | 1,317 条历史快照 |
| `data/edu-cn-roots-whois-2026-10-04.*` | 同日早期 SWOT 阶段的 1,380 条历史快照 |
| `data/edu-cn-roots-whois-20261004-184303.*` | 本次 1,439 条全量 HTTP 复查固定批次 |
| `data/history/` | 全量更新前的逐域数据备份 |
| `data/statistics.json` | 当前数量、结果分类、实际查询日期统计 |

## 来源与采集说明

WHOIS 查询使用 CERNIC 官方查询入口：<https://www.nic.edu.cn/cgi-bin/reg/otherobj>。查询入口接受域名、网络名或 IP 作为 `query` 参数。本数据集的逐域核验对象为表内根域名。**2026-10-04 在系统 Chrome 完成新增候选查询后，又通过本机后台 HTTP 完成 1,439 个根域名全量查询；当前出口可访问，不能将该接口概括为仅限教育网。**2026-09-26 使用 Check-Host 从 12 个境外公开 HTTP 探测节点请求 WHOIS 接口，全部收到 `403 Forbidden`；同日对 CERNIC 首页的 12 节点对照请求均返回 `200 OK`。可查看 [WHOIS 接口检测报告](https://check-host.net/check-report/4d8fa59ck9cd) 和 [首页对照报告](https://check-host.net/check-report/4d8fab19kf07)。这些历史探测仅描述对应节点的访问条件；检测报告没有列出各探测节点的源 IP，因此不应据此推导完整的允许/拒绝 IP 段。网络策略和服务可用性可能变化。

该服务返回内容可能是完整英文 WHOIS 记录，也可能是中文单行注册状态，或无匹配结果；本仓库将这些结果整理为 `full_record`、`cn_status` 和 `not_found` 三类。

域名发现列表来自多种公开来源和历史清单，来源信息保存在 `collected_from`、`source_last_observed`、`evidence_hostnames` 和 `review_notes` 中。DNS 记录及 CERNET 地址列表关联是独立维度，不应与 CERNIC WHOIS 结果混为一谈。

### 引用来源清单

下表按当前逐域 JSON 的 `metadata.collected_from` 标签统计唯一根域名。历史来源可能重叠，各行数量**不能相加作为总数**。WHOIS 核验与域名发现是不同维度；第三方机构标签保留为来源证据，机构字段使用实际 CERNIC 返回值。

| 来源 | 用途 | 当前记录中带该来源标签的根域数 | 引用与证据 |
| --- | --- | ---: | --- |
| CERNIC WHOIS | 登记信息核验，覆盖全部记录；其中 23 条返回未找到 | 1,439 | [官方查询入口](https://www.nic.edu.cn/cgi-bin/reg/otherobj)；逐域 `source_url`、`whois_queried`、`raw_text`；[最新全量报告](data/cernic-http-refresh-20261004-184303.json)；历史 [SWOT 原文](data/cernic-swot-raw-2026-10-04.json)、[Hipo 原文](data/cernic-hipo-raw-2026-10-04.json) |
| Hipo/university-domains-list | 本轮新增域名发现 | 59 | [固定提交的数据文件](https://github.com/Hipo/university-domains-list/blob/603e10f51b67c6553b9bca9aecc0db4c2417ed10/world_universities_and_domains.json)；[遍历比较](data/hipo-comparison-2026-10-04.json)、[候选 CSV](data/hipo-new-candidates-2026-10-04.csv) |
| JetBrains/swot | 上一轮新增域名发现 | 63 | [固定提交的 edu.cn 目录](https://github.com/JetBrains/swot/tree/b2dee08283cfee0ba43630779b6bf702bf5df76e/lib/domains/cn/edu)；[候选及文件路径](data/swot-new-candidates-2026-10-04.csv) |
| Community-maintained Chinese university-domain index (GitHub) | 历史域名发现 | 1,109 | 历史记录只保留此泛化标签，具体仓库 URL / 提交未保存在现有发布数据中；无法给出精确引用，待补证。原标签可在 [2026-09-26 汇总](data/edu-cn-roots-whois-2026-09-26.json) 中检查 |
| crt.sh Certificate Transparency | 证书中出现的主机名发现 | 393 | [crt.sh](https://crt.sh/)；逐域 `evidence_hostnames` 和来源标签。历史逐次查询响应未随本仓库发布 |
| CERNET 导报 / CERNIC 历史域名清单 | 历史域名发现 | 127 | 现有来源标签覆盖 1998 Q3、1999 Q1–Q4、2001 Q3；具体文档 URL 未保存在发布记录中，待补证；见 [历史汇总来源字段](data/edu-cn-roots-whois-2026-09-26.json) |
| HackerTarget free hostsearch | 主机名发现 | 6 | [Host Search 官方工具页](https://hackertarget.com/find-dns-host-records/)；逐域来源标签和证据主机名 |
| CERNIC 地址范围内的 PTR 样本 | 反向解析主机名发现 | 9 | [CERNIC 官方地址列表入口](https://www.nic.edu.cn/RS/ipstat/internalip/)；历史反向查询原始响应未随本仓库发布 |
| CERNIC/CERNET 服务域名参考与 DNS | 服务根域发现 | 4 | [CERNIC 官方站点](https://www.nic.edu.cn/)；具体发现证据见对应逐域记录 |
| CERNIC WHOIS spot-check / discovery 标签 | 历史 WHOIS 发现线索 | 2 | [官方查询入口](https://www.nic.edu.cn/cgi-bin/reg/otherobj)；此处仅统计 `collected_from` 标签，不是全部 WHOIS 核验数量 |

DNS 与地址关联的辅助来源：旧记录注明使用 [Google Public DNS DoH](https://developers.google.com/speed/public-dns/docs/doh)，部分 SERVFAIL 重试使用 Cloudflare DNS；CERNET 地址重合参考 [CERNIC IPv4 列表](https://www.nic.edu.cn/RS/ipstat/internalip/) 和 [官方 IPv6 地址 / 直联列表](https://www.nic.edu.cn/RS/ipstat/internalip/somepeers6.txt)。地址重合仅为网络线索，不代表注册权属。这两批新增的 122 个根域未执行 DNS 或地址关联查询。

后续发现来源必须保留可访问的 URL；仓库来源固定提交 SHA 和路径，其他列表注明版本或日期。不要将无法回溯的历史标签补写成未经确认的仓库或文档链接。

## 示例

读取汇总 JSON：

```python
import json

with open("data/edu-cn-roots-whois-latest.json", encoding="utf-8") as f:
    dataset = json.load(f)

print(dataset["count"])
for record in dataset["records"]:
    if record["whois_result_type"] == "full_record":
        print(record["root_domain"], record["whois_org_en"])
```

读取 CSV：

```python
import csv

with open("data/edu-cn-roots-whois-latest.csv", encoding="utf-8-sig", newline="") as f:
    for record in csv.DictReader(f):
        print(record["root_domain"], record["whois_result_type"])
```

## 自动校验与 CSV 生成

**当前数据源是 `data/whois-json/` 的 1,439 个逐域 JSON。** 后续新增或复查请编辑逐域 JSON，按照 [贡献指南](CONTRIBUTING.md) 填写 2.0 字段，并更新 [累计版本配置](data/dataset.json)。CSV 和汇总 JSON 从逐域数据生成，不能仅手工修改 CSV 来添加域名。

- [JSON Schema](schemas/whois-record.schema.json)：定义必需字段、空值规则、结果分类和名称服务器结构。
- [生成与校验脚本](scripts/build_dataset.py)：校验全部逐域 JSON，生成排序后的 UTF-8 BOM、20 列 CSV、汇总 JSON 和 `statistics.json`。
- [GitHub Actions CI](.github/workflows/dataset.yml)：相关文件 push / PR 或手动触发时，先运行测试，再校验并生成数据，上传 `edu-cn-roots-dataset` artifact。CI 不自动提交、推送或实时查询 CERNIC。
- [生成器测试](tests/test_dataset.py)：覆盖错误字段、分类、日期、IP、文件名、查询 URL、原文证据、重复 JSON 键，以及完整数据导出的往返一致性和确定性。
- [AI 工作说明](AGENTS.md)：列出维护入口、校验命令、历史记录和发布边界。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_dataset.py --output build
```

本轮生成结果在 `build/edu-cn-roots-whois-2026-10-04.csv`、同名 `.json` 及 `build/statistics.json`。`build/` 不进入 Git；CI 的生成文件可从对应 Actions 运行页面下载。发布累计结果时，将生成的 CSV / 汇总 JSON 复制为 `data/edu-cn-roots-whois-latest.csv` 和 `.json`，并同步 `data/statistics.json`；按批次另存历史快照，尤其不能覆盖同日早期阶段快照。更新上方数量、来源统计和引用。

逐域 JSON 新增 `schema_version`、`whois_queried`、`source_url`、`raw_text` 和 `metadata`。`metadata` 保存 CSV 第 2–12 列；WHOIS 其余字段由结构化记录派生。历史阶段旧记录曾使用 `raw_text: null` 标明缺失；最新全量复查已为全部 1,439 条保存实际 HTTP 返回原文。新采集记录必须保存原文。

`data/dataset.json` 的 `updated` 仅表示累计版本日期；统计按逐条 `whois_queried` 分组。未复查的旧记录保留真实查询日期，未查询的 DNS 不填成已验证。详细采集步骤、字段规则和 Git 忽略规则见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**旧脚本 `scripts/merge-swot-20261004.py` 仅是 2026-10-04 批次重建工具，不能用于后续增量更新。** 它会重写旧结构的逐域 JSON；2.0 迁移后使用 `scripts/build_dataset.py`，避免覆盖当前累计数据。

### 后台 HTTP 更新命令

默认网页访问仍使用系统浏览器；维护者明确要求后台 HTTP 时，使用以下流程。先测试当前连接路径，按吞吐量和延迟选择并发，不将本次测量当作永久参数。

```bash
# 小样本测量：1、2、4、8 并发，每档 24 条
.venv/bin/python scripts/refresh_cernic.py --benchmark
# 全量复查；本轮使用 2 并发
.venv/bin/python scripts/refresh_cernic.py --workers 2
```

脚本先备份逐域 JSON，将 HTML 和阶段结果保存在 `outputs/http-refresh/<批次>/`，失败最多重试 3 次并退避。只有全批次通过解析和字段校验，才更新正式逐域 JSON、latest、statistics 和固定批次快照。有失败时正式数据不变，应先检查报告和已保存响应、修复解析或重试失败请求，不能把采集错误写成 `not_found`。生成报告中的 SHA256 针对 HTTP 响应字节；逐域 `raw_text` 是 HTML 解析后的文本。

HTTP 脚本的连接超时 10 秒、总超时 30 秒及并发 1–8 是当前客户端实现参数。服务器时间上限未测得；本次吞吐量在约 2 次/秒趋于平稳，不能推导其他时间或出口的绝对容量。测试报告、全量报告和历史快照要随发布保留。CI 只校验已保存数据并生成 artifact，不发起全量外部查询。

## 更新与引用

每次重新查询后，建议将日期写入发布文件名和 `whois_queried`，保留旧快照以便比较。维护者可同时更新 CSV、汇总 JSON 和逐域 JSON；三者应覆盖相同的根域名集合，并保持字段口径一致。

引用本数据时请注明仓库 URL、累计版本日期 **2026-10-04**、实际查询批次日期和具体文件名。可使用如下引用格式：

> xingwangzhe, *edu.cn 根域名与 CERNIC WHOIS 数据*, 2026-10-04 累计版（全部 WHOIS 查询于 2026-10-04）, `edu-cn-roots-whois-latest.csv`（1,439 条，含 Hipo 增量）, https://github.com/xingwangzhe/edu-cn-roots

## 使用边界

- 数据是特定日期的公开信息快照；注册、联系人、名称服务器和 DNS 状态可能变化。
- WHOIS 输出是登记数据库返回的文本，不对其准确性、完整性或当前有效性作额外保证。
- 组织名称、地址和联系人字段仅为解释登记记录而保留；请遵守适用法律、CERNIC 服务条款及隐私要求，避免将联系人信息用于骚扰或未经授权的用途。
- 本项目与 CERNIC、CERNET 或表中机构无隶属或背书关系。
- 数据不构成安全结论、授权证明、法律意见或对任何域名控制权的证明。

## 许可

本项目采用 [MIT License](LICENSE)，Copyright (c) 2026 xingwangzhe。使用、复制、修改及分发本项目时，请保留 MIT 许可要求的版权和许可声明。

MIT 许可适用于维护者有权许可的项目内容。仓库包含来自公开来源的事实数据及 CERNIC WHOIS 返回；本项目的许可不替代第三方来源的适用条款，也不授予维护者不持有的权利。使用者仍需自行核实各来源的许可、隐私和个人信息使用要求。项目按 MIT 条款以“原样”提供，不作担保。
