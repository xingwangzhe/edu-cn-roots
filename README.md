# edu.cn 根域名与 CERNIC WHOIS 数据

本仓库发布 `edu.cn` 下恰好一层的根域名清单，以及截至 **2026-09-26** 对 CERNIC WHOIS 查询的逐域核验结果。数据面向研究、测绘、资产盘点和可重复分析；DNS 和注册信息具有时效性，不能视为实时状态或注册权属证明。

## 快速获取

- [WHOIS 核验 CSV](data/edu-cn-roots-whois-2026-09-26.csv)：1,317 行域名记录，UTF-8 BOM 编码，20 列。
- [WHOIS 核验 JSON 汇总](data/edu-cn-roots-whois-2026-09-26.json)：同一批 1,317 条记录，含数据集元信息。
- [逐域 JSON 文件](data/whois-json/)：每个根域名一个 JSON，文件名为域名加 `.json`，共 1,317 个。

可直接下载单文件：

```text
https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/edu-cn-roots-whois-2026-09-26.csv
https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/edu-cn-roots-whois-2026-09-26.json
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
| WHOIS 汇总 JSON（含日期、数量和记录） | [edu-cn-roots-whois-2026-09-26.json](https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/edu-cn-roots-whois-2026-09-26.json) |
| WHOIS CSV | [edu-cn-roots-whois-2026-09-26.csv](https://cdn.jsdelivr.net/gh/xingwangzhe/edu-cn-roots@main/data/edu-cn-roots-whois-2026-09-26.csv) |

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

- CDN 提供仓库文件的静态副本，不会向 CERNIC 发起实时 WHOIS 查询；当前公开快照采集于 **2026-09-26**。
- `@main` 跟随主分支，但 CDN 缓存可能延迟反映修改，不保证即时更新。汇总文件的日期和数量请读取 `whois_queried`、`count`；逐域文件的字段以该文件实际结构为准。
- 汇总文件名包含日期：以后新增另一日期的文件，不会使旧 URL 自动切换，需要更新引用路径。
- 根域名文件只收录 `edu.cn` 下的一层域名。将子域归一化后，查到的是根域名登记快照，不是子域的独立 WHOIS 记录。
- HTTP 404 表示请求的文件不存在，可能是路径错误或数据集未收录；网络错误也不是登记状态。JSON 中的 `not_found` 表示当次查询没有匹配记录，都不能作为域名未注册或可注册的证明。
- CDN 不可用时，可按相同路径尝试 GitHub Raw，例如 [jxutcm.edu.cn 的原始文件](https://raw.githubusercontent.com/xingwangzhe/edu-cn-roots/main/data/whois-json/jxutcm.edu.cn.json)。

完整地址语法和缓存说明见 [jsDelivr 官方文档](https://www.jsdelivr.com/documentation#id-github)。公开网页查询可使用 [needhelp WHOIS 工具](https://needhelp.icu/zh/tools/whois-lookup)，查询方式见 [静态快照说明](https://needhelp.icu/zh/blogs/edu-cn-whois-static-lookup)。

## 数据范围与口径

- 仅包含直接位于 `edu.cn` 下的一层域名，例如 `tsinghua.edu.cn`；`www.tsinghua.edu.cn` 等更深子域不单独列为根域名。
- 对发现的子域做根域回卷；不按学校、教育机构或其他组织类型筛选。
- 既收录当前 DNS 可解析的域名，也保留历史 CERNIC 清单中的域名；DNS 消失不构成删除理由。
- 当前版本共 1,317 个根域名：1,126 个完整英文 WHOIS 记录，168 个中文注册状态，23 个未在 CERNIC 查询中找到匹配记录。
- WHOIS 批量查询日期为 2026-09-26。该日期只表示本次数据采集快照。

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

根对象包含 `dataset`、`schema_version`、`whois_queried`、`source`、`scope`、`count` 和 `records`。`records` 是记录数组；字段与 CSV 一致，JSON 中空字段使用 `""`。将 CSV 导入程序时请注意其 UTF-8 BOM。

### 逐域 JSON

`data/whois-json/<root_domain>.json` 保存 WHOIS 响应的结构化提取，包括 `root_domain`、`type`、组织名称、域名名、网络名、联系人、名称服务器、地址和 `raw_note`。字段会因响应形态不同而为空或缺省；其中 `type` 与 CSV 的 `whois_result_type` 对应。逐域文件便于按域名加载，但批量分析建议使用 CSV 或汇总 JSON。

## 来源与采集说明

WHOIS 查询使用 CERNIC 官方查询入口：<https://www.nic.edu.cn/cgi-bin/reg/otherobj>。查询入口接受域名、网络名或 IP 作为 `query` 参数。本数据集的逐域核验对象为表内根域名。**截至 2026-09-26 的实测，该 WHOIS 接口只能在教育网环境下查询。**使用 Check-Host 从 12 个境外公开 HTTP 探测节点请求 WHOIS 接口，全部收到 `403 Forbidden`；同日对 CERNIC 首页的 12 节点对照请求均返回 `200 OK`。可查看 [WHOIS 接口检测报告](https://check-host.net/check-report/4d8fa59ck9cd) 和 [首页对照报告](https://check-host.net/check-report/4d8fab19kf07)。此结论描述本次实际测试到的访问条件；检测报告没有列出各探测节点的源 IP，因此不应据此推导完整的允许/拒绝 IP 段。网络策略和服务可用性可能变化。

该服务返回内容可能是完整英文 WHOIS 记录，也可能是中文单行注册状态，或无匹配结果；本仓库将这些结果整理为 `full_record`、`cn_status` 和 `not_found` 三类。

域名发现列表来自多种公开来源和历史清单，来源信息保存在 `collected_from`、`source_last_observed`、`evidence_hostnames` 和 `review_notes` 中。DNS 记录及 CERNET 地址列表关联是独立维度，不应与 CERNIC WHOIS 结果混为一谈。

## 示例

读取汇总 JSON：

```python
import json

with open("data/edu-cn-roots-whois-2026-09-26.json", encoding="utf-8") as f:
    dataset = json.load(f)

print(dataset["count"])
for record in dataset["records"]:
    if record["whois_result_type"] == "full_record":
        print(record["root_domain"], record["whois_org_en"])
```

读取 CSV：

```python
import csv

with open("data/edu-cn-roots-whois-2026-09-26.csv", encoding="utf-8-sig", newline="") as f:
    for record in csv.DictReader(f):
        print(record["root_domain"], record["whois_result_type"])
```

## 更新与引用

每次重新查询后，建议将日期写入发布文件名和 `whois_queried`，保留旧快照以便比较。维护者可同时更新 CSV、汇总 JSON 和逐域 JSON；三者应覆盖相同的根域名集合，并保持字段口径一致。

引用本数据时请注明仓库 URL、快照日期 **2026-09-26** 和具体文件名。可使用如下引用格式：

> xingwangzhe, *edu.cn 根域名与 CERNIC WHOIS 数据*, 2026-09-26 快照, `edu-cn-roots-whois-2026-09-26.csv`, https://github.com/xingwangzhe/edu-cn-roots

## 使用边界

- 数据是特定日期的公开信息快照；注册、联系人、名称服务器和 DNS 状态可能变化。
- WHOIS 输出是登记数据库返回的文本，不对其准确性、完整性或当前有效性作额外保证。
- 组织名称、地址和联系人字段仅为解释登记记录而保留；请遵守适用法律、CERNIC 服务条款及隐私要求，避免将联系人信息用于骚扰或未经授权的用途。
- 本项目与 CERNIC、CERNET 或表中机构无隶属或背书关系。
- 数据不构成安全结论、授权证明、法律意见或对任何域名控制权的证明。

## 许可

本仓库目前未声明统一的再分发许可。公开可访问不等同于授予版权、数据库权利或个人信息再利用许可。使用者应自行核实各来源的许可和适用规则；在维护者补充明确许可前，请勿将仓库理解为无条件开放数据许可。
