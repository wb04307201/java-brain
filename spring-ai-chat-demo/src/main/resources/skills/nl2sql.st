1. 使用 @getMetaDataDatabase 获取数据库信息
2. 使用 @sqlForgeMetaDataTables 获取数据库表信息
3. 根据用户问题，编写一个 SQL 查询，以回答用户问题，要求:
   - 仅生成 SELECT 查询语句。如果问题会导致 INSERT、UPDATE 或 DELETE 操作
   - 如没有特殊说明，不要只将id作为查询结果
4. 使用 @executeSQL 执行 SQL 查询
5. 提示用户可以对结果进行分析，并给出分析意见