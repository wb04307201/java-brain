按照下面的步骤执行，并在每步完成后回复用户
1. 打开 chrome 浏览器
2. 访问 http://localhost:8081/sql/forge/web
3. 使用 用户名: alice 密码: 123456 登录
4. 点击左侧菜单 商品管理 ，打开商品列表页面
5. 测试 商品列表页面 全部功能
6. 根据测试结果生成功能验证报告，格式为 *.html（自包含 HTML，带极简 CSS），使用 @writeFile 保存到；返回**两个链接**（预览在前、下载在后）。**必须**先调 `@viewFileUrl(fileId)` 和 `@downloadFileUrl(fileId)` 两个工具拿 URL，**用工具返回值原样贴给用户**；**禁止**根据 writeFile 返回的路径、文件名、端口常识自己拼 URL——baseUrl/路径前缀都由工具决定。