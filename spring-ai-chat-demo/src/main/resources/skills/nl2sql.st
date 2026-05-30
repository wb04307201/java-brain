1. 使用 @getSystems 获取所有系统信息
2. 分析与用户意图一致的系统， 使用 @sqlForgeMetaDataTables 获取系统使用的数据库中所有表的信息
3. 根据用户意图，使用 @getMetaDataTableInfo获取表信息，编写一个 SQL 查询，以回答用户问题，要求:
   - 仅生成 SELECT 查询语句。如果问题会导致 INSERT、UPDATE 或 DELETE 操作
   - 如没有特殊说明，不要只将id作为查询结果
4. 使用 @executeSQL 执行 SQL 查询
5. 提示用户可以对结果进行分析，并给出分析意见
6. 如果生成图表，返回的图表url使用img标签展示，并设置width为100%，点击图片打开新的标签页显示图片
7. 如果生成并保存分析报告
   1. 使用 @listAllowedDirectories 获取允许访问的目录
   2. 使用 @writeFile 在允许访问的目录里保存报告为*.md，返回文件id
   3. 使用 @downloadFileUrl 获取下载地址
   1. 使用 @viewFileUrl 获取预览地址