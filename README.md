# Java大脑：让您的系统瞬间拥有“思考”与“执行”的智能大脑
告别繁琐的 AI 接入与数据开发，Java大脑为您提供一站式智能化解决方案：
- 🧠 灵梭 (AI 赋能中心)：Spring Boot 专属 AI 加速器。零配置接入 RAG 知识库、MCP 工具与 Skill 技能库，自带高颜值聊天界面，让您的应用秒变智能助手。
- 🛠️ SQL工坊 (数据管理引擎)：全能的数据库操作框架。从类型安全的实体操作、JSON CRUD，到 Apache Calcite 跨库联邦查询，再到 Amis 低代码可视化管理，按需插拔，让数据开发效率提升 300%。
- 🔗 SQL工坊 MCP (智能数据桥梁)：打通 AI 与业务的任督二脉。让“灵梭”智能体安全、合规地直接对话您的业务数据库，实现基于真实数据的智能问答、自动化报表与业务决策。


## 代码包含如下两个项目
1. [oms](oms): 在系统上增加数据库元数据、低代码功能，提供给智能体调用
2. [loom-agent](loom-agent): 聊天界面，对接AI，并包含调用系统的Skill

> 注：营销段落提到的"SQL工坊 MCP"组件（`sql-forge-mcp`）位于上游 sql-forge 仓库，由 loom-agent 通过 stdio 自动拉起，不在本仓代码中。

## 启动
1. 启动 oms 项目，内含测试用 H2 数据库与初始化脚本，数据库包含用户、商品、订单、订单明细，以及字典、字典项数据
   启动后可访问 `http://localhost:8081/sql/forge/web/home.html` 查看 sql-forge 控制台（未登录会自动跳转到 `/login.html`）
   用户名`admin`
   密码`admin123`
2. sql-forge-mcp 通过 stdio 提供给 loom-agent，目前 loom-agent 内已配置好 stdio
   但运行环境需要 jbang（类似于 python 的 uv，或者 node 的 npx），安装命令可参考
   > Windows (PowerShell)
   > ```shell
   > iex "& { $(iwr https://ps.jbang.dev) } app setup"
   > ```
   > Linux / macOS
   > ```shell
   > curl -Ls https://sh.jbang.dev | bash -s - app setup
   > ```
3. 启动 loom-agent，作为聊天界面，也可以使用其他聊天界面，但需自行配置 mcps、skill
   可访问 `http://localhost:8080/spring/ai/loom` 查看聊天界面
   loom-agent 目前通过阿里云百炼调用 qwen3.7-plus 大模型（启用多模型与深度思考），key 配置在环境变量中，变量名为 `DASHSCOPE_API_KEY`
   如需使用其他模型，请自行更换模型配置与依赖库

## 使用
### 自然语言调用数据库
```text
订单系统各分类商品数,画柱状图,保存HTML报告
```

### 自然语言生成页面
例如web生成需求如下：
```markdown
帮我创建商品单表维护功能

商品表信息:

| 列名              | 类型     | 长度  | 描述   | 用于搜索 | 字典编码       |
|-----------------|--------|-----|------|------|------------|
| ID              | uuid   | 36  | 商品ID |      |            |
| NAME            | string | 50  | 商品名称 | 模糊   |            |
| DICT_CATEGORIES | dict   | 100 | 商品类型 | 模糊   | categories |
| PRICE           | number |     | 价格   | 模糊   |            |


字典项表:

| 列名        | 类型     | 长度  | 描述    |
|-----------|--------|-----|-------|
| DICT_CODE | string | 100 | 字典编码  |
| ITEM_CODE | string | 100 | 字典项编码 |
| ITEM_NAME | string | 100 | 字典项名称 |
```



