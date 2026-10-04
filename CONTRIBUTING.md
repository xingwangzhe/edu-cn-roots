# 数据贡献指南

## 数据源与生成文件

`data/whois-json/<root_domain>.json` 是当前累计数据的唯一编辑入口。每个根域名一个文件，使用 `schemas/whois-record.schema.json` 定义的 2.0 格式。`data/dataset.json` 的 `updated` 是累计版本日期，逐域 `whois_queried` 是实际查询日期。不要手工添加 CSV 行来代替逐域 JSON。

历史日期 CSV / 汇总 JSON 保留不变。当前累计 CSV 和汇总 JSON 由 `scripts/build_dataset.py` 生成到 `build/`，CI 上传为 `edu-cn-roots-dataset` artifact。CI 不自动提交文件，也不查询 CERNIC 或 DNS。

## 添加或复查域名

1. 从最新逐域集合检查重复域名。只保留恰好一层的 `xxx.edu.cn`；子域回卷，小写，不做机构类型过滤。保留 DNS 消失和历史登记条目。
2. 保存公开来源 URL、实际观察日期、原始主机名；Git 仓库来源固定提交 SHA 和路径。
3. 通过系统浏览器查询 `https://www.nic.edu.cn/cgi-bin/reg/otherobj?query=<root_domain>`，保存实际返回原文。直接处理字节时按 GBK 解码。串行查询并保留标签页。网络失败、403、超时、乱码、空白页不得标为 `not_found`。
4. 编辑逐域 JSON，填写下表字段。可以参照 `data/whois-json/cupk.edu.cn.json`（完整记录）或 `data/whois-json/ccdgut.edu.cn.json`（中文状态）。不要复制示例域名的实际值。
5. 新采集记录必须填写 `raw_text`。迁移旧记录时才允许 `null`，并在 `metadata.review_notes` 解释原文缺失。复查旧域名前保存原始记录到单独的历史批次文件，不覆写原有日期快照。
6. 将 `data/dataset.json` 的 `updated` 更新为本轮累计日期。未复查的域名保持原有查询日期及数据；不要批量刷新日期。
7. 安装校验依赖、执行测试和生成脚本。根据 `build/statistics.json` 更新 README 数量、分类、批次统计。生成的 CSV 为 UTF-8 BOM、20 列，按域名排序。
8. 若本轮需要仓库内发布新快照，将 `build/edu-cn-roots-whois-<日期>.csv` 和同名 `.json` 复制到 `data/`，更新 README 快速获取链接、示例和引用。`build/` 是忽略的生成目录。
9. 检查 Git 差异。本仓库的忽略规则会匹配新的 `data/whois-json` 文件，使用 `git add -f -- data/whois-json/<root_domain>.json` 添加明确的新增文件；不要强制添加所有研究输出。PR 中说明新增/复查数量、实际查询日期、返回类型、DNS 是否查询及测试结果。

## 逐域 JSON 字段

所有顶层字段均必需；不适用的可空字段填写 `null`，列表使用 `[]`，`metadata` 中空字段使用 `""`。不允许未声明的字段，扩展时应一起更新 schema、生成器、测试和文档。

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 固定 `"2.0"` |
| `root_domain` | 小写一层根域，与文件名一致 |
| `type` | `full_record`、`cn_status` 或 `not_found` |
| `org_en` / `org_cn` | CERNIC 返回的英文/中文机构名 |
| `domain_name` | 完整 WHOIS 的域名，忽略大小写后须等于根域 |
| `network_name` / `admin_contact` | 返回的网络名 / 联系人；缺失为 `null` |
| `reg_date` | 中文状态中的真实注册日期 `YYYYMMDD`；不适用为 `null` |
| `nameservers` | 对象数组，含 `host`、`ip`，可有 `ipv6` 和 `addresses` 完整地址列表；保留登记服务器顺序 |
| `address` | WHOIS 地址行的字符串数组 |
| `raw_note` | 中文状态 / 无匹配原文摘要；完整记录可为 `null` |
| `whois_queried` | 实际查询日期 `YYYY-MM-DD` |
| `source_url` | 带该根域 `query` 参数的 CERNIC 查询 URL |
| `raw_text` | 实际页面原文；旧记录迁移可为 `null`，必须解释 |
| `metadata` | 原 CSV 的第 2–12 列，键名见 schema 和 README CSV 字段表 |

完整记录必须有英文机构名和匹配的 `domain_name`。中文状态必须有中文机构名、有效注册日期及 `raw_note`。无匹配必须有 `raw_note` 和明确的服务返回证据，不表示从未注册。`source_last_observed` 保留来源说明，历史值可能含日期说明文本。

WHOIS 名称服务器地址可能已经过期，不能冒充当前 DNS。未执行 DNS 查询时，`current_dns_status` 写明未检查，`A_records`、`AAAA_records`、`NS_records` 留空；CERNET 地址关联没有独立证据也留空。

## 本地验证及 CI

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_dataset.py --output build
git diff --check
```

GitHub Actions 在相关数据、schema、脚本、测试或工作流发生 push / PR 时运行，也支持手动触发。它检查全部逐域文件的 schema、必填字段、枚举、日期、IP、文件名、查询 URL 和结果证据，执行生成器测试，再产出 CSV、汇总 JSON 和数量统计 artifact。任何失败均阻止产物上传。CI 校验的是保存数据的一致性，不证明远端注册信息仍然实时有效。

`scripts/merge-swot-20261004.py` 是旧批次重建工具，会重写本地数据。2.0 迁移后不要将它用于后续更新或重新运行来覆盖当前逐域数据；使用新的生成器。

## 当前累计发布入口

当前使用 data/edu-cn-roots-whois-latest.csv / .json 和 data/statistics.json。生成后同步这些文件，保留旧日期或批次快照；同一天已有快照不可覆盖。README 来源表按 collected_from 标签统计唯一域名，重叠来源不相加；新增来源保留精确 URL、版本和证据，历史缺失引用明确标为待补证。

## 后台 HTTP 全量复查

维护者明确要求直接 HTTP 时，可运行 `python3 scripts/refresh_cernic.py --benchmark` 测试 1、2、4、8 并发，每级 24 条；全局请求启动上限为 8 次/秒，不进行无界压力测试。`python3 scripts/refresh_cernic.py --workers 2` 全量复查当前逐域集合。连接超时 10 秒、单请求总超时 30 秒，失败最多尝试 3 次并退避。这里是客户端设置，不是已证明的 CERNIC 服务端超时上限。

脚本先保存当前所有逐域 JSON 到 `data/history/`，再将响应 HTML 和解析结果写入 `outputs/http-refresh/<批次>/`。只有全部请求和字段校验成功，才更新正式 JSON 并生成 latest、统计及带批次时间的历史 CSV / 汇总 JSON；有失败时保留检查点，正式数据不变。响应按 GBK 解码，保留原文，实测 timing 和响应 SHA256 写入批次报告。原始来源、观察日期、DNS 记录不因 WHOIS 复查刷新。
