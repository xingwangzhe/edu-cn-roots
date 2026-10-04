# AGENTS.md — edu-cn-roots 维护说明

访问网页默认使用用户的系统浏览器，不使用内置浏览器，任务结束保留标签页。维护者为 xingwangzhe，邮箱 xingwangzhe@outlook.com。与 Cloudflare 交互时使用 cf CLI，除非项目存在 Wrangler 配置。

## 当前事实与维护入口

- 仅收录 `edu.cn` 下恰好一层的根域，深层子域回卷；不做机构类型过滤，历史条目不因 DNS 消失而删除。
- 截至 2026-10-04，累计 1,439 个根域：1,195 个 `full_record`、221 个 `cn_status`、23 个 `not_found`。1,317 条查询于 2026-09-26，122 条查询于 2026-10-04（SWOT 63、Hipo 59）。后续数量须从数据重新计算，不能将这里的数字视为固定约束。
- 当前唯一数据编辑入口是 `data/whois-json/<root_domain>.json`，结构为 schema 2.0。先读 `CONTRIBUTING.md`、`schemas/whois-record.schema.json`、`scripts/build_dataset.py` 和 `data/dataset.json`。
- `metadata` 保存原 CSV 第 2–12 列；WHOIS 字段和查询日期由顶层结构化值生成。所有必需键均保留，可空字段用 null、列表用 []、metadata 空字段用空字符串。
- 根目录 `edu-cn-roots.csv` 和 `whois-json/` 是忽略的本地副本，克隆后可能不存在。发布用的数据在 `data/`，生成输出在忽略目录 `build/`。

## CERNIC 查询与证据

- 入口：`https://www.nic.edu.cn/cgi-bin/reg/otherobj`；直接查询为 `?query=<域名或网络名或IP>`。
- 在 2026-10-04 的系统 Chrome 访问中，63 个新增域名全部返回登记数据；不需要登录。不能根据别处的 403 推断仅教育网能访问，也不能承诺所有出口可访问。
- 返回字节为 GB2312/GBK；直接解码用 `TextDecoder('gbk')`，浏览器 DOM 是已解码文本。
- 优先系统浏览器串行查询，每条保存实际原文、source_url 和 whois_queried。可使用工具支持的同源批量请求，但不要依赖历史工具名称或 RPC 行为；遵守当前浏览器 API 文档。
- `full_record` 为完整登记记录；`cn_status` 为中文注册状态；`not_found` 仅用于服务明确无匹配结果。403、超时、乱码和空白响应是采集失败，重试并保存错误，不得覆盖已有成功记录或伪装为 not_found。
- WHOIS 的 NS / IP 是登记数据，不是当前 DNS。DNS 或 CERNET 地址关联未独立查询时留空并说明未检查。
- 旧记录缺少 raw_text 的迁移例外要保留说明。新采集必须有实际原文；不补造历史证据。

## 更新、生成与校验

1. 检查 Git 工作区，保留用户修改。从当前逐域目录去重，并保存候选来源 URL、提交 SHA、原始主机名和观察日期。
2. 新增或复查逐域 JSON；复查前保留旧批次证据，未复查旧记录不刷新日期。扩展字段时同步 schema、生成器、测试和文档。
3. 更新 data/dataset.json 的 updated。用生成器产出 CSV / 汇总 JSON，保留历史快照，按需要将新快照从 build/ 复制到 data/。
4. 从 build/statistics.json 更新 README 数量、类型、实际查询日期分组和文件链接；不要混淆累计更新日期与全量查询日期。
5. 运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_dataset.py --output build
git diff --check
```

6. CI 为 .github/workflows/dataset.yml：测试通过后校验所有 JSON 并上传生成的 CSV / 汇总 JSON / statistics artifact。不自动提交或查询外部服务。报告本地验证、提交、推送和远端 CI 状态时分开表述。

## Git 与旧脚本注意事项

- `whois-json/` 忽略规则会匹配发布目录内的新文件。对明确新增文件使用 `git add -f -- data/whois-json/<domain>.json`，通过 git status 确认；不要将全部研究输出强制加入。
- 本 AGENTS.md 需跟踪发布，但已有忽略规则屏蔽它，因此首次需 `git add -f -- AGENTS.md`。
- `scripts/merge-swot-20261004.py` 固定从 2026-09-26 快照重建 63 条增量，会重写旧结构文件。schema 2.0 后不要执行它覆盖当前数据；使用 build_dataset.py。
- 历史 2026-09-26 和 2026-10-04 日期汇总文件保留为原快照。新生成的 schema 2.0 数据及迁移说明见 build/ 和当前逐域 JSON。

## 累计发布与来源引用

当前 1,439 条累计发布入口为 data/edu-cn-roots-whois-latest.csv 和 .json，统计为 data/statistics.json。2026-10-04 日期文件保留同日早期 SWOT 阶段的 1,380 条快照，不覆盖。生成后同步 latest 和 statistics；历史阶段另存。README 来源表根据 metadata.collected_from 标签按域名去重统计，来源重叠不可相加。历史泛化 GitHub 标签及 CERNET 导报条目缺少精确 URL 时明确说明待补证，不推测引用。
