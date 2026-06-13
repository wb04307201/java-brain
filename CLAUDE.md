# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览（来自 README）

JavaBrain = 灵梭 AI Agent + SQL 工坊 MCP + SQL 工坊，把业务系统、数据库、AI 拼成一个"智能中枢"。仓库根目录包含两个**独立的** Spring Boot 模块（没有父级 `pom.xml`），分别承担后端业务库与 AI 对话前端：

- **`oms/`** —— 订单管理系统（原 `sql-forge-demo`）。内置 H2 + Flyway 演示库，并暴露 `sql-forge` 通用 CRUD/查询 API 与低代码控制台，被 AI 通过 MCP 调用。
- **`loom-agent/`** —— 灵梭 AI Agent（原 `spring-ai-chat-demo`）。聊天界面 + Spring AI 编排，注册 MCP 客户端与若干 Skill（`.st` 提示词）。

典型启动顺序：先 `oms`（监听 `8081`），再 `loom-agent`（`8080`，会通过 stdio 拉起 `sql-forge-mcp` 指向 `oms`）。

## 常用命令

仓库根目录没有聚合 `pom.xml`，所有 Maven 命令必须**在模块目录下**执行：

```bash
# 构建
mvn -f oms/pom.xml clean install -DskipTests
mvn -f loom-agent/pom.xml clean install -DskipTests

# 跑全部测试
mvn -f oms/pom.xml test
mvn -f loom-agent/pom.xml test

# 单测：使用 -Dtest 限定方法/类
mvn -f oms/pom.xml test -Dtest=OmsApplicationTests
mvn -f loom-agent/pom.xml test -Dtest=LoomAgentApplicationTests#contextLoads

# 启动应用（开发模式）
mvn -f oms/pom.xml spring-boot:run         # 默认端口 8081
mvn -f loom-agent/pom.xml spring-boot:run   # 默认端口 8080

# 打包可执行 jar
mvn -f oms/pom.xml package
mvn -f loom-agent/pom.xml package
```

JDK：`pom.xml` 中 `<java.version>17</java.version>`；本地 Maven 跑在 JDK 25 上时仍能编译，但**不要**改用 `--release 25` 等参数，除非同时调整两边的 `<java.version>`。

环境变量：`loom-agent` 启动前需设置 `DASHSCOPE_API_KEY`（阿里云百炼 qwen 模型）。README 注明外部 MCP 需要 `jbang`（PowerShell：`iex "& { $(iwr https://ps.jbang.dev) } app setup"`），多个 MCP 用 `npx.cmd` 拉起。

## 模块架构

### `oms` —— 业务/数据底座

- `cn.wubo.oms.OmsApplication` 入口；`server.port=8081`。
- 依赖：`sql-forge-spring-boot-starter` + `sql-forge-calcite-spring-boot-starter` + `sql-forge-web-spring-boot-starter`（版本 `1.6.0`）、H2、MySQL、PostgreSQL JDBC、Flyway（多方言）、Lombok 1.18.46。
- Flyway 脚本：`src/main/resources/db/migration/` 下 `V1__schema.sql`（业务表 + 字典 + 鉴权表）、`V2__data.sql`（种子数据：用户、商品、订单、订单明细、字典）、`V3__templates.sql`（Amis 模板种子）。MySQL / PostgreSQL 演示脚本在 `resources/mysql/` 与 `resources/postgresql/`。
- Calcite 联邦查询配置：`src/main/resources/model.json`（默认 `MYSQL`，附加 `POSTGRES`）。
- 自定义存储：包 `cn.wubo.oms` 下注册了 4 个 JDBC 实现作为 `@Primary` Bean，覆盖 `sql-forge` 默认内存存储：
  - `JdbcStorageConfiguration` 装配 `IUserStorage / IRoleStorage / IUserRoleStorage / IRoleTemplateStorage`，全部委托给 `ExecutorService` 执行 SQL。
  - 对应的 `Log*Execute` 是 sql-forge `IExecute` 拦截器，记录 select/selectPage/insert/update/delete 调用。
  - `CustomTemplateAmisStorage` / `CustomTemplateSqlStorage` 覆盖 Amis/SQL 模板的持久化。
- `application.yml` 关键项：`sql.forge.api.database.select-only=false`（允许写）、`apiKeys=[test]`、`schemata=[PUBLIC]`、`calcite.enabled=true`、`calcite.configuration=classpath:model.json`。

### `loom-agent` —— AI 编排层

- `cn.wubo.loom.agent.LoomAgentApplication` 入口；`server.port=8080`。
- 依赖：`spring-ai-loom-agent-spring-boot-starter:1.1.25`（核心编排）、`spring-ai-alibaba-starter-dashscope`（聊天/嵌入）、H2 + Flyway + Spring Boot JDBC（用于聊天记忆持久化）。
- 模型：`dashscope.chat.options.model=qwen3.7-plus`（启用 `multi_model` 与 `enable_thinking`），嵌入模型 `text-embedding-v4`。要换模型同时改 `pom.xml` 依赖与 `application.yml`。
- MCP 客户端：`mcp.client.stdio.servers-configuration=classpath:mcp-servers.json`。该 JSON 注册了 Bing 搜索、网页抓取、顺序思维、Playwright、Chrome DevTools、HTTP 客户端、AntV 图表、sql-forge-mcp（通过 `jbang.cmd` 拉起） 等。其中 sql-forge-mcp 默认参数指向 `http://localhost:8081`，**改端口要同步改这里**。
- Skill：`src/main/resources/skills/*.st` 是模板式提示词，由 `spring.ai.loom.agent.skills[]` 在 `application.yml` 中按 `name` 注册并触发。
  - `nl2sql.st` —— 自然语言查 oms 数据库（走 `@getSystems → @sqlForgeMetaDataTables → @executeSQL`）。
  - `web.st` —— 生成百度 Amis CRUD JSON 模板，调用 `@amisTemplateSave` 落盘到 oms，返回 `http://localhost:8081/sql/forge/console?id=...` 预览地址。
  - `news-watch.st` —— 三阶段搜索 → HTML 报告（强调"禁止自然语言自白、直接调工具"）。
  - `package-docker.st` —— 多栈项目部署（maven/npm/npm-frontend/pip），要求用户提供 `port` / `containerPort`，**不允许工具侧兜底猜值**。
  - `e2e.st` —— 浏览器端到端验证（登录 alice/123456，跑商品管理 → 生成 .md 报告）。
  - `http.st` —— JSONPlaceholder 的 GET/POST/PUT/DELETE 自检。
- 上传：`spring.servlet.multipart.max-file-size=10MB`（保存/预览能力所依赖）。

## 端到端数据流（改这三处时要联动）

`用户提问 → loom-agent Skill 触发 → Spring AI 调用 MCP 工具 → sql-forge-mcp → oms 暴露的 /sql/forge/api/json/{method}/{table} → JDBC → H2/MySQL/PostgreSQL → 结果回流 AI → 返回预览/下载链接`。

变更触点：

1. 改 oms 表结构 → `V*__schema.sql`（H2 通用），必要时同步 `resources/mysql/` 与 `resources/postgresql/`；AI 取表信息依赖此。
2. 改 sql-forge API 协议 → `oms` 自定义存储类（`Jdbc*Storage` / `Log*Execute` / `CustomTemplate*Storage`）和 `loom-agent` 的 Skill 提示词（`.st` 里的 JSON 协议样例）需同步。
3. 改 AI 模型/供应商 → 同时调 `loom-agent/pom.xml` 与 `application.yml`（dashscope 段）。DASHSCOPE_API_KEY 缺失会启动失败。
4. 改端口 → `oms/src/main/resources/application.yml` 的 `server.port` 与 `loom-agent/src/main/resources/mcp-servers.json` 中 `sql-forge-mcp` 的 `--sql.forge.mcp.systems[0].url` 必须一起改；`web.st` / `e2e.st` / README 里的 `localhost:8080/8081` 字面量也需更新。

## 注意事项

- `oms/data/testdb.mv.db` 与 `loom-agent/.local/datasource/db*` 是运行期 H2 文件，提交时被 `.gitignore` 排除；清理可删除对应目录后重启。
- Lombok 在 `oms` 通过 `maven-compiler-plugin` 的 `annotationProcessorPaths` 启用，IDE 需装 Lombok 插件。
- sql-forge 暴露的接口**默认无认证**，仅靠 `apiKey` 头或参数匹配（参考 `application.yml` 中的 `test`）；公网部署务必替换。
- `loom-agent` 启动前若 MCP 子进程（如 `sql-forge-mcp` / `bing-search`）下载失败，需要检查网络与 `jbang` / Node 环境；该报错只会在**首次调用**对应 Skill 时出现。