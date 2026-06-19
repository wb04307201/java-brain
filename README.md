<div align="right">
  <a href="README.zh-CN.md">中文</a> | English
</div>

# JavaBrain

**Intelligent Solution for Enterprise Digital Systems** — Empower your business systems with "thinking" and "execution" capabilities in minutes.

**Components** (3 independent modules):

- 🧠 [**Loom AI Agent**](https://github.com/wb04307201/spring-ai-loom-agent): Spring AI orchestration with zero-code RAG / MCP / Skill integration ([Gitee Mirror](https://gitee.com/wb04307201/spring-ai-loom-agent))
- 🛠️ [**SQL Forge**](https://github.com/wb04307201/sql-forge): CRUD + Calcite Federated Queries + Amis Low-Code ([Gitee Mirror](https://gitee.com/wb04307201/sql-forge))
- 🔗 **SQL Forge MCP**: Secure AI-to-Database bridge (same repo as SQL Forge)

**3 Intelligent Assistants for Users**:

- 💬 **Conversational Agent**: Natural language interaction, intelligent Q&A, multi-turn dialogue
-  **Data Analytics Assistant**: Natural language queries, 90-second analysis reports
- 🎨 **Intelligent Low-Code Assistant**: Generate CRUD pages in one sentence, ready in 10 minutes

**Three Core Capabilities**:

- **AI-Powered Business Data Queries**: Ask in natural language, get analysis reports in 90 seconds (NL2SQL + Charts + HTML Reports)
- **One-Sentence CRUD Page Generation**: Production-ready maintenance pages in 10 minutes (AI semantic inference + Amis low-code)
- **LLM Controllability**: LLM never connects directly to databases; goes through MCP restricted tools + templated APIs; switch to local models for full privatization

---

## Usage Examples

### Natural Language Database Queries

Enter in the Loom chat interface:

```text
Show product counts by category in the order system, draw a bar chart, save as HTML report
```

Execution chain: `nl2sql.st` → `getSystems` → `sqlForgeMetaDataTables` → `executeSQL` → AntV Charts → HTML Report.
Downloadable from the console after generation.

![img.png](img.png)
![img_3.png](img_3.png)

### Natural Language CRUD Page Generation

Round 1:

```text
Help me create a single-table maintenance page for the products table.
```

Round 2 (confirmation):

```text
Looks good, generate it directly.
```

Execution chain: `web.st` → `amisTemplateSave` → saved to oms → returns
`http://localhost:8081/sql/forge/console?id=...` preview URL.

![img_1.png](img_1.png)
![img_2.png](img_2.png)

### More Scenarios

| Skill Template | Trigger Scenario | Output |
|---|---|---|
| `nl2sql.st` | Natural language database queries + reports | HTML / Markdown reports |
| `web.st` | Generate Amis CRUD JSON templates | Console preview page |

---

## Project Positioning

JavaBrain is an intelligent solution for enterprise digital systems, composed of 3 independent components that can be combined on demand:

| Component | Role | Upstream Repo | In This Repo |
|---|---|---|---|
| Loom AI Agent | Chat UI + Spring AI orchestration (RAG / MCP / Skill / Files), **orchestration hub in this demo**: hosts chat UI, invokes Skills by user intent, connects to oms and other external services via MCP | `spring-ai-loom-agent` | No |
| SQL Forge | Data management (type-safe CRUD / Calcite federated queries / Amis low-code), **data foundation in this demo**: builds oms, hosts order/product/user data | `sql-forge` | No |
| SQL Forge MCP | AI ↔ DB bridge (stdio subprocess, invoked by Agent) | `sql-forge` (same repo, different module) | No |
| `oms` | Business foundation (demo carrier) + authentication + metadata + console UI | — | Yes |
| `loom-agent` | Agent frontend entry, references Loom starter | — | Yes |

> Repos = 2 (Loom / SQL Forge), Components = 3 (Loom / SQL Forge / SQL Forge MCP).

---

## Repository Structure

```
java-brain/
├── oms/                # Business foundation, default port 8081
│   ├── src/main/resources/db/migration/   # Flyway: H2/MySQL/PostgreSQL
│   ├── src/main/java/cn/wubo/oms/         # Custom JDBC storage / IExecute interceptors
│   └── src/main/resources/model.json      # Calcite federated query configuration
└── loom-agent/         # AI frontend, default port 8080
    ├── src/main/resources/mcp-servers.json   # Registers Bing / Playwright / sql-forge-mcp etc.
    └── src/main/resources/skills/*.st        # nl2sql / web / news-watch / e2e / http / package-docker
```

The two modules have **no parent** `pom.xml`. All Maven commands must specify the module with `-f`, see `oms/pom.xml` and `loom-agent/pom.xml`.

---

## Architecture & Data Flow

```
                         ┌──────────────────────────────┐
   Browser  ◀── chat UI ─▶│       loom-agent            │
   :8080/spring/ai/loom  │  (Loom Spring AI Orchestration)│
                         │  ┌──────────────────────┐   │
                         │  │ Skill Templates(.st) │──┼──▶ Natural Language → Tool Calls
                         │  └──────────────────────┘   │
                         │  ┌──────────────────────┐   │
                         │  │ MCP Client(stdio)   │──┼──▶ npx / jbang subprocesses
                         │  └──────────────────────┘   │
                         └────────┬─────────────────────┘
                                  │ HTTP / MCP
                                  ▼
                         ┌──────────────────────────────┐
                         │     sql-forge-mcp subprocess │
                         │  (launched by jbang, points to oms)│
                         └────────┬─────────────────────┘
                                  │ /sql/forge/api/json/{method}/{table}
                                  ▼
                         ┌──────────────────────────────┐
                         │            oms                │
                         │  (Spring Boot + sql-forge)   │
                         │  IUserStorage / IExecute /   │
                         │  Calcite Federation          │
                         └────────┬─────────────────────┘
                                  │ JDBC
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
                 H2           MySQL         PostgreSQL
              (default)     (demo db)       (demo db)
```

**Change Touchpoints** (must update together):

1. Schema changes → `oms` module's `V*__schema.sql` (H2), sync `resources/mysql/` and `resources/postgresql/` if needed.
2. sql-forge API protocol changes → `oms`'s `Jdbc*Storage` / `Log*Execute` / `CustomTemplate*Storage` and `loom-agent`'s `*.st` template JSON protocol examples.
3. AI model/vendor changes → both `loom-agent/pom.xml` and `application.yml` (dashscope section).
4. Port changes → `oms`'s `server.port`, `loom-agent`'s `mcp-servers.json` `sql-forge-mcp`'s `--sql.forge.mcp.systems[0].url`, and `localhost:8080/8081` literals in README / `.st` files.

---

## Prerequisites

| Tool | Version | Purpose | Symptom if Missing |
|---|---|---|---|
| JDK | 17+ | Compile/run both modules | Maven errors immediately |
| Maven | 3.8+ | Build | Startup fails |
| `jbang` | Latest | Launch `sql-forge-mcp` subprocess | `jbang not found` on first SQL call |
| Node.js | 18+ (optional) | Launch Playwright / Chrome DevTools MCPs | Not needed if not using these Skills |
| `DASHSCOPE_API_KEY` | Alibaba Cloud Bailian qwen key | Loom calls qwen3.7-plus | Startup fails directly |

**jbang Installation**:

```powershell
# Windows (PowerShell)
iex "& { $(iwr https://ps.jbang.dev) } app setup"
```

```bash
# Linux / macOS
curl -Ls https://sh.jbang.dev | bash -s - app setup
```

**DASHSCOPE_API_KEY Setup**:

```powershell
# Windows (PowerShell, current session)
$env:DASHSCOPE_API_KEY = "sk-..."
# Permanent: setx DASHSCOPE_API_KEY "sk-..."
```

```bash
# Linux / macOS
export DASHSCOPE_API_KEY="sk-..."
```

---

## Startup

> Startup order: `oms` first (called by `loom-agent` via MCP), then `loom-agent`.

### 1. Start oms (default `8081`)

```bash
mvn -f oms/pom.xml spring-boot:run
```

After startup, access:

- `http://localhost:8081/sql/forge/web/home.html` — sql-forge console (auto-redirects to `/login.html` if not logged in)
- Console default credentials: `admin` / `admin123`

### 2. Start loom-agent (default `8080`)

Open a new terminal:

```bash
mvn -f loom-agent/pom.xml spring-boot:run
```

After startup, access:

- `http://localhost:8080/spring/ai/loom` — Loom chat interface

### 3. Verify

```bash
# oms health
curl -sf http://localhost:8081/sql/forge/api/json/list/USER_INFO | head -c 200

# loom-agent health
curl -sf http://localhost:8080/spring/ai/loom | head -c 200
```

---

## Port List

| Port | Service | Sync Changes Required |
|---|---|---|
| `8081` | oms (sql-forge + console) | `loom-agent`'s `mcp-servers.json` `sql-forge-mcp`'s `--sql.forge.mcp.systems[0].url` |
| `8080` | loom-agent (Loom UI + API) | Browser access URL, `localhost:8080` literals in `.st` templates |

---

## Troubleshooting

| Symptom | Root Cause | Resolution |
|---|---|---|
| loom-agent startup fails with `DASHSCOPE_API_KEY not set` | Environment variable not injected | Set per "Prerequisites" section and restart |
| `jbang not found` when calling SQL from chat | `jbang` not installed / PATH not生效 | Install jbang per "Prerequisites" and reopen terminal |
| `BindException: 8081 already in use` | oms port occupied | Change `server.port` in `oms/src/main/resources/application.yml`, sync `mcp-servers.json` |
| `sql-forge-mcp` subprocess repeatedly restarts after startup | oms not ready / wrong port | Confirm oms listens on 8081 and `mcp-servers.json` url points to correct port |
| Flyway error `Migration checksum mismatch` | Local H2 state file残留 | Delete `oms/data/testdb.mv.db` and `loom-agent/.local/datasource/db*` then restart |
| MCP subprocess timeout on first launch | Slow initial download of `sql-forge-mcp` image | Wait or configure mirror; only happens on first Skill call |

> Local H2 files `oms/data/testdb.mv.db` and `loom-agent/.local/datasource/db*` are excluded by `.gitignore`; delete directories and restart to clean.

---

## Upstream Repositories

| Repository | Components | Description | Mirror |
|---|---|---|---|
| spring-ai-loom-agent | Loom AI Agent | Independently usable, AI orchestration only | [GitHub](https://github.com/wb04307201/spring-ai-loom-agent) · [Gitee](https://gitee.com/wb04307201/spring-ai-loom-agent) |
| sql-forge | SQL Forge + SQL Forge MCP | Same repo, different modules | [GitHub](https://github.com/wb04307201/sql-forge) · [Gitee](https://gitee.com/wb04307201/sql-forge) |

Submit issues and feature requests to the corresponding upstream repositories. This repo is for combination demo and scaffold maintenance only.

---

## Development

```bash
# Build
mvn -f oms/pom.xml clean install -DskipTests
mvn -f loom-agent/pom.xml clean install -DskipTests

# Test
mvn -f oms/pom.xml test
mvn -f loom-agent/pom.xml test

# Single test: limit to method/class
mvn -f oms/pom.xml test -Dtest=OmsApplicationTests
mvn -f loom-agent/pom.xml test -Dtest=LoomAgentApplicationTests#contextLoads

# Package executable jar
mvn -f oms/pom.xml package
mvn -f loom-agent/pom.xml package
```

> Local Maven runs on JDK 25 but still compiles (`<java.version>17</java.version>`). Do not add `--release 25` to commands unless you also adjust `<java.version>` in both pom files.

---

## License

This repository code is for demo and scaffold purposes. Business component dependencies follow their respective upstream licenses.
