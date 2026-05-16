# JavaBrain
## 赋予系统AI能力，成为本体驱动的智能体
> 打通业务、系统与数据的智能中枢平台，重构企业数字化大脑


## 代码包含如下三个项目
1. [sql-forge-demo](sql-forge-demo): 在系统上增加数据库元数据、低代码功能，提供给智能体调用
2. [sql-forge-mcp](sql-forge-mcp): 连接系统与AI
3. [spring-ai-chat-demo](spring-ai-chat-demo): 聊天界面，对接AI，并包含调用系统的Skill

## 启动
1. 启动sql-forge-demo项目，内涵测试用H2数据库，与初始化脚本，数据库包含用户、商品、订单、订单明细，以及字典，字典项数据
   可访问`http://localhost:8081/sql/forge/console` 查看sql-forge库控制台
2. sql-forge-mcp需要编译成成jar，通过stdio提供给spring-ai-chat-demo,目前spring-ai-chat-demo内已包含编译好的jar，并配置好stdio  
   运行环境需要jbang(类似于python的uv，或者node的npx),安装命令可参考  
   > Windows (PowerShell)
   > ```shell
   > iex "& { $(iwr https://ps.jbang.dev) } app setup"
   > ```
   > Linux / macOS
   > ```shell
   > curl -Ls https://sh.jbang.dev | bash -s - app setup
   > ```
3. 启动spring-ai-chat-demo，作为聊天界面，也可以使用其他聊天界面，但需配置自行配置mcps、skill  
   可访问`http://localhost:8080/spring/ai/loom` 查看聊天界面  
   spring-ai-chat-demo目前使用通过阿里云百炼调用qwen-plus大，key配置在环境变量中，变量名为DASHSCOPE_API_KEY  
   如需使用其他模型，请自行更换模型配置与依赖库


## 使用
### 自然语言调用数据库
```text
请帮我查询数据库里有哪些商品？哪个商品在订单表里订购数量最多？哪个商品在订单表里订购价格合计最多？
```

也可以配合其他mcp工具例如继续对话：
```text
请更详细的分析各种商品订购数量与销售额，并保存分析报告
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



