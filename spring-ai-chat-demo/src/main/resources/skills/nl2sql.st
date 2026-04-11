1. 使用 @getMetaDataDatabase 获取数据库信息
2. 使用 @sqlForgeMetaDataTables 获取数据库表信息
3. 根据用户问题，编写一个 SQL 查询，以回答用户问题，要求:
   - 仅生成 SELECT 查询语句。如果问题会导致 INSERT、UPDATE 或 DELETE 操作
   - 如没有特殊说明，不要只将id作为查询结果
4. 使用 @executeSQL 执行 SQL 查询
5. 提示用户可以对结果进行分析，并给出分析意见
6. 如果生成图表，返回的图表url使用img标签展示，并设置width为100%，点击图片打开新的标签页显示图片
7. 如果生成并保存分析报告
   1. 使用 @list_allowed_directories 获取允许访问的目录
   2. 使用 @write_file 在允许访问的目录里保存报告为*.md，
   3. 保存后返回下载地址，格式为 http://localhost:8080/spring/ai/chat/file/download/文件名 ，使用a标签展示，点击进行下载