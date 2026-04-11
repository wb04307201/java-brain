1. 使用 @list_allowed_directories 获取允许访问的目录
2. 使用 @write_file 在允许访问的目录里保存报告为*.md，
3. 保存后返回下载地址，格式为 http://localhost:8080/spring/ai/chat/file/download/文件名 ，使用a标签展示，点击进行下载