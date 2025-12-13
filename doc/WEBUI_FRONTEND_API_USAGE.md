# qBittorrent WebUI 前端 HTTP 接口使用总结

本文档总结了 qBittorrent WebUI 前端代码中使用的所有 HTTP API 接口及其功能。

## 目录
1. [认证接口 (Authentication)](#认证接口)
2. [应用程序接口 (Application)](#应用程序接口)
3. [Torrent 管理接口 (Torrents)](#torrent-管理接口)
4. [传输控制接口 (Transfer)](#传输控制接口)
5. [同步接口 (Sync)](#同步接口)
6. [RSS 接口 (RSS)](#rss-接口)
7. [搜索接口 (Search)](#搜索接口)
8. [日志接口 (Log)](#日志接口)

---

## 认证接口

### 1. 用户登录
- **接口**: `POST /api/v2/auth/login`
- **文件**: `public/scripts/login.js:40`
- **功能**: 用户登录认证
- **使用场景**: 登录页面提交用户名和密码

### 2. 用户登出
- **接口**: `POST /api/v2/auth/logout`
- **文件**: `private/scripts/mocha-init.js:1283`
- **功能**: 注销当前用户会话
- **使用场景**: 用户点击登出按钮

---

## 应用程序接口

### 1. 获取构建信息
- **接口**: `GET /api/v2/app/buildInfo`
- **文件**: `private/scripts/cache.js:57`
- **功能**: 获取 qBittorrent 构建信息（版本、编译选项等）
- **使用场景**: 应用初始化时缓存构建信息

### 2. 获取应用版本
- **接口**: `GET /api/v2/app/version`
- **文件**: `private/scripts/cache.js:157`
- **功能**: 获取 qBittorrent 版本号
- **使用场景**: 应用初始化时缓存版本信息

### 3. 获取应用偏好设置
- **接口**: `GET /api/v2/app/preferences`
- **文件**: `private/scripts/cache.js:84`
- **功能**: 获取应用的所有配置选项
- **使用场景**: 打开设置页面时加载当前配置

### 4. 设置应用偏好设置
- **接口**: `POST /api/v2/app/setPreferences`
- **文件**: `private/scripts/cache.js:121`
- **参数**: `json` - JSON 格式的配置数据
- **功能**: 保存应用配置
- **使用场景**: 用户修改设置后保存

### 5. 关闭应用
- **接口**: `POST /api/v2/app/shutdown`
- **文件**: `private/scripts/mocha-init.js:1299`
- **功能**: 关闭 qBittorrent 应用
- **使用场景**: 用户点击"退出"菜单

### 6. 获取目录内容
- **接口**: `GET /api/v2/app/getDirectoryContent`
- **文件**: `private/scripts/pathAutofill.js:67`
- **参数**: `dirPath`, `mode`
- **功能**: 获取指定目录的文件列表（用于路径自动完成）
- **使用场景**: 用户输入路径时的自动补全功能

### 7. 获取网络接口列表
- **接口**: `GET /api/v2/app/networkInterfaceList`
- **文件**: `private/views/preferences.html:2115`
- **功能**: 获取系统网络接口列表
- **使用场景**: 设置页面选择网络接口

### 8. 获取网络接口地址列表
- **接口**: `GET /api/v2/app/networkInterfaceAddressList`
- **文件**: `private/views/preferences.html:2144`
- **功能**: 获取指定网络接口的 IP 地址列表
- **使用场景**: 设置页面选择监听地址

### 9. 发送测试邮件
- **接口**: `POST /api/v2/app/sendTestEmail`
- **文件**: `private/views/preferences.html:1917`
- **功能**: 发送测试邮件以验证邮件配置
- **使用场景**: 设置邮件通知后测试配置

### 10. 获取 Cookies
- **接口**: `GET /api/v2/app/cookies`
- **文件**: `private/views/cookies.html:146`
- **功能**: 获取已保存的 Cookies
- **使用场景**: Cookie 管理页面显示现有 Cookies

### 11. 设置 Cookies
- **接口**: `POST /api/v2/app/setCookies`
- **文件**: `private/views/cookies.html:125`
- **功能**: 设置或更新 Cookies
- **使用场景**: Cookie 管理页面添加/修改 Cookies

---

## Torrent 管理接口

### 1. 添加 Torrent
- **接口**: `POST /api/v2/torrents/add`
- **文件**: 
  - `private/upload.html:18` (表单提交)
  - `private/download.html:20` (表单提交)
- **功能**: 添加新的 torrent（通过文件上传或 URL）
- **使用场景**: 
  - 上传 .torrent 文件
  - 从 URL 或磁力链接添加 torrent

### 2. 删除 Torrent
- **接口**: `POST /api/v2/torrents/delete`
- **文件**: 
  - `private/scripts/mocha-init.js:519`
  - `private/scripts/mocha-init.js:796`
  - `private/views/confirmdeletion.html:80`
- **参数**: `hashes`, `deleteFiles`
- **功能**: 删除指定的 torrent
- **使用场景**: 
  - 删除选中的 torrent
  - 删除可见的所有 torrent
  - 确认删除对话框

### 3. 启动 Torrent
- **接口**: `POST /api/v2/torrents/start`
- **文件**: 
  - `private/scripts/mocha-init.js:562`
  - `private/scripts/mocha-init.js:737`
  - `private/scripts/mocha-init.js:1203`
- **参数**: `hashes`
- **功能**: 启动指定的 torrent 下载
- **使用场景**: 
  - 启动选中的 torrent
  - 启动所有可见的 torrent

### 4. 停止 Torrent
- **接口**: `POST /api/v2/torrents/stop`
- **文件**: 
  - `private/scripts/mocha-init.js:549`
  - `private/scripts/mocha-init.js:758`
  - `private/scripts/mocha-init.js:1188`
- **参数**: `hashes`
- **功能**: 停止指定的 torrent 下载
- **使用场景**: 
  - 停止选中的 torrent
  - 停止所有可见的 torrent

### 5. 重新检查 Torrent
- **接口**: `POST /api/v2/torrents/recheck`
- **文件**: 
  - `private/scripts/mocha-init.js:621`
  - `private/views/confirmRecheck.html:31`
- **参数**: `hashes`
- **功能**: 重新检查 torrent 文件完整性
- **使用场景**: 用户手动触发文件校验

### 6. 重新通告 Torrent
- **接口**: `POST /api/v2/torrents/reannounce`
- **文件**: `private/scripts/mocha-init.js:642`
- **参数**: `hashes`
- **功能**: 强制向 tracker 重新通告
- **使用场景**: 手动触发 tracker 更新

### 7. 重命名 Torrent
- **接口**: `POST /api/v2/torrents/rename`
- **文件**: `private/rename.html:48`
- **参数**: `hash`, `name`
- **功能**: 重命名 torrent
- **使用场景**: 重命名对话框

### 8. 获取 Torrent 属性
- **接口**: `GET /api/v2/torrents/properties`
- **文件**: `private/scripts/prop-general.js:91`
- **参数**: `hash`
- **功能**: 获取 torrent 的详细属性信息
- **使用场景**: 属性面板的"常规"标签页

### 9. 获取 Torrent 文件列表
- **接口**: `GET /api/v2/torrents/files`
- **文件**: 
  - `private/scripts/prop-files.js:344`
  - `private/rename_files.html:382`
- **参数**: `hash`
- **功能**: 获取 torrent 包含的文件列表
- **使用场景**: 属性面板的"文件"标签页

### 10. 设置文件优先级
- **接口**: `POST /api/v2/torrents/filePrio`
- **文件**: `private/scripts/prop-files.js:297`
- **参数**: `hash`, `id`, `priority`
- **功能**: 设置文件下载优先级（不下载/普通/高/最高）
- **使用场景**: 文件列表中修改文件优先级

### 11. 重命名文件
- **接口**: `POST /api/v2/torrents/renameFile`
- **文件**: 
  - `private/scripts/rename-files.js:244`
  - `private/rename_file.html:64`
- **参数**: `hash`, `oldPath`, `newPath`
- **功能**: 重命名 torrent 中的文件
- **使用场景**: 文件列表中重命名文件

### 12. 重命名文件夹
- **接口**: `POST /api/v2/torrents/renameFolder`
- **文件**: 
  - `private/scripts/rename-files.js:244`
  - `private/rename_file.html:64`
- **参数**: `hash`, `oldPath`, `newPath`
- **功能**: 重命名 torrent 中的文件夹
- **使用场景**: 文件列表中重命名文件夹

### 13. 获取 Torrent Trackers
- **接口**: `GET /api/v2/torrents/trackers`
- **文件**: `private/scripts/prop-trackers.js:62`
- **参数**: `hash`
- **功能**: 获取 torrent 的 tracker 列表
- **使用场景**: 属性面板的"Trackers"标签页

### 14. 添加 Trackers
- **接口**: `POST /api/v2/torrents/addTrackers`
- **文件**: `private/addtrackers.html:30`
- **参数**: `hash`, `urls`
- **功能**: 为 torrent 添加新的 tracker
- **使用场景**: 添加 tracker 对话框

### 15. 编辑 Tracker
- **接口**: `POST /api/v2/torrents/editTracker`
- **文件**: `private/edittracker.html:41`
- **参数**: `hash`, `origUrl`, `newUrl`
- **功能**: 编辑现有 tracker URL
- **使用场景**: 编辑 tracker 对话框

### 16. 删除 Trackers
- **接口**: `POST /api/v2/torrents/removeTrackers`
- **文件**: 
  - `private/scripts/prop-trackers.js:226`
  - `private/confirmtrackerdeletion.html:29`
- **参数**: `hash`, `urls`
- **功能**: 删除指定的 tracker
- **使用场景**: Tracker 列表中删除 tracker

### 17. 获取 Web Seeds
- **接口**: `GET /api/v2/torrents/webseeds`
- **文件**: `private/scripts/prop-webseeds.js:62`
- **参数**: `hash`
- **功能**: 获取 torrent 的 Web Seed 列表
- **使用场景**: 属性面板的"Web Seeds"标签页

### 18. 添加 Web Seeds
- **接口**: `POST /api/v2/torrents/addWebSeeds`
- **文件**: `private/addwebseeds.html:29`
- **参数**: `hash`, `urls`
- **功能**: 添加 Web Seed URL
- **使用场景**: 添加 Web Seed 对话框

### 19. 编辑 Web Seed
- **接口**: `POST /api/v2/torrents/editWebSeed`
- **文件**: `private/editwebseed.html:37`
- **参数**: `hash`, `origUrl`, `newUrl`
- **功能**: 编辑 Web Seed URL
- **使用场景**: 编辑 Web Seed 对话框

### 20. 删除 Web Seeds
- **接口**: `POST /api/v2/torrents/removeWebSeeds`
- **文件**: `private/scripts/prop-webseeds.js:201`
- **参数**: `hash`, `urls`
- **功能**: 删除 Web Seed
- **使用场景**: Web Seeds 列表中删除

### 21. 添加 Peers
- **接口**: `POST /api/v2/torrents/addPeers`
- **文件**: `private/addpeers.html:39`
- **参数**: `hashes`, `peers`
- **功能**: 手动添加 peer 连接
- **使用场景**: 添加 peer 对话框

### 22. 获取 Piece 状态
- **接口**: `GET /api/v2/torrents/pieceStates`
- **文件**: `private/scripts/prop-general.js:237`
- **参数**: `hash`
- **功能**: 获取 torrent 各个 piece 的下载状态
- **使用场景**: 属性面板显示 piece 下载进度条

### 23. 获取分类列表
- **接口**: `GET /api/v2/torrents/categories`
- **文件**: 
  - `private/scripts/download.js:39`
  - `private/views/rssDownloader.html:432`
- **功能**: 获取所有分类
- **使用场景**: 
  - 下载页面选择分类
  - RSS 下载器选择分类

### 24. 创建分类
- **接口**: `POST /api/v2/torrents/createCategory`
- **文件**: 
  - `private/newcategory.html:76`
  - `private/newcategory.html:112`
- **参数**: `category`, `savePath`
- **功能**: 创建新分类
- **使用场景**: 新建分类对话框

### 25. 编辑分类
- **接口**: `POST /api/v2/torrents/editCategory`
- **文件**: `private/newcategory.html:131`
- **参数**: `category`, `savePath`
- **功能**: 编辑分类属性
- **使用场景**: 编辑分类对话框

### 26. 设置 Torrent 分类
- **接口**: `POST /api/v2/torrents/setCategory`
- **文件**: 
  - `private/scripts/mocha-init.js:848`
  - `private/newcategory.html:89`
- **参数**: `hashes`, `category`
- **功能**: 将 torrent 移动到指定分类
- **使用场景**: 右键菜单设置分类

### 27. 删除分类
- **接口**: `POST /api/v2/torrents/removeCategories`
- **文件**: 
  - `private/scripts/mocha-init.js:930`
  - `private/scripts/mocha-init.js:951`
- **参数**: `categories`
- **功能**: 删除指定分类
- **使用场景**: 
  - 删除选中的分类
  - 删除未使用的分类

### 28. 创建标签
- **接口**: `POST /api/v2/torrents/createTags`
- **文件**: `private/newtag.html:80`
- **参数**: `tags`
- **功能**: 创建新标签
- **使用场景**: 新建标签对话框

### 29. 添加标签到 Torrent
- **接口**: `POST /api/v2/torrents/addTags`
- **文件**: 
  - `private/scripts/mocha-init.js:997`
  - `private/newtag.html:60`
- **参数**: `hashes`, `tags`
- **功能**: 为 torrent 添加标签
- **使用场景**: 标签管理

### 30. 从 Torrent 移除标签
- **接口**: `POST /api/v2/torrents/removeTags`
- **文件**: 
  - `private/scripts/mocha-init.js:997`
  - `private/scripts/mocha-init.js:1009`
- **参数**: `hashes`, `tags`
- **功能**: 从 torrent 移除标签
- **使用场景**: 标签管理

### 31. 删除标签
- **接口**: `POST /api/v2/torrents/deleteTags`
- **文件**: 
  - `private/scripts/mocha-init.js:1041`
  - `private/scripts/mocha-init.js:1056`
- **参数**: `tags`
- **功能**: 删除标签
- **使用场景**: 
  - 删除选中的标签
  - 删除未使用的标签

### 32. 设置 Torrent 位置
- **接口**: `POST /api/v2/torrents/setLocation`
- **文件**: `private/setlocation.html:50`
- **参数**: `hashes`, `location`
- **功能**: 设置 torrent 保存位置
- **使用场景**: 设置位置对话框

### 33. 设置自动管理
- **接口**: `POST /api/v2/torrents/setAutoManagement`
- **文件**: 
  - `private/scripts/mocha-init.js:589`
  - `private/views/confirmAutoTMM.html:29`
- **参数**: `hashes`, `enable`
- **功能**: 启用/禁用自动 torrent 管理
- **使用场景**: 切换自动管理模式

### 34. 设置上传限速
- **接口**: `POST /api/v2/torrents/setUploadLimit`
- **文件**: `private/uploadlimit.html:68`
- **参数**: `hashes`, `limit`
- **功能**: 设置 torrent 上传速度限制
- **使用场景**: 上传限速对话框

### 35. 获取上传限速
- **接口**: `GET /api/v2/torrents/uploadLimit`
- **文件**: `private/scripts/speedslider.js:90`
- **参数**: `hashes`
- **功能**: 获取 torrent 当前上传限速
- **使用场景**: 速度滑块初始化

### 36. 设置下载限速
- **接口**: `POST /api/v2/torrents/setDownloadLimit`
- **文件**: `private/downloadlimit.html:68`
- **参数**: `hashes`, `limit`
- **功能**: 设置 torrent 下载速度限制
- **使用场景**: 下载限速对话框

### 37. 获取下载限速
- **接口**: `GET /api/v2/torrents/downloadLimit`
- **文件**: `private/scripts/speedslider.js:199`
- **参数**: `hashes`
- **功能**: 获取 torrent 当前下载限速
- **使用场景**: 速度滑块初始化

### 38. 设置分享率限制
- **接口**: `POST /api/v2/torrents/setShareLimits`
- **文件**: `private/shareratio.html:102`
- **参数**: `hashes`, `ratioLimit`, `seedingTimeLimit`
- **功能**: 设置分享率和做种时间限制
- **使用场景**: 分享率限制对话框

### 39. 切换顺序下载
- **接口**: `POST /api/v2/torrents/toggleSequentialDownload`
- **文件**: `private/scripts/mocha-init.js:380`
- **参数**: `hashes`
- **功能**: 启用/禁用顺序下载
- **使用场景**: 右键菜单切换顺序下载

### 40. 切换首尾优先下载
- **接口**: `POST /api/v2/torrents/toggleFirstLastPiecePrio`
- **文件**: `private/scripts/mocha-init.js:393`
- **参数**: `hashes`
- **功能**: 启用/禁用首尾 piece 优先下载
- **使用场景**: 右键菜单切换首尾优先

### 41. 设置超级做种
- **接口**: `POST /api/v2/torrents/setSuperSeeding`
- **文件**: `private/scripts/mocha-init.js:406`
- **参数**: `hashes`, `value`
- **功能**: 启用/禁用超级做种模式
- **使用场景**: 右键菜单切换超级做种

### 42. 设置强制启动
- **接口**: `POST /api/v2/torrents/setForceStart`
- **文件**: `private/scripts/mocha-init.js:420`
- **参数**: `hashes`, `value`
- **功能**: 启用/禁用强制启动
- **使用场景**: 右键菜单切换强制启动

### 43. 导出 Torrent 文件
- **接口**: `GET /api/v2/torrents/export`
- **文件**: `private/scripts/mocha-init.js:1170`
- **参数**: `hash`
- **功能**: 导出 .torrent 文件
- **使用场景**: 右键菜单导出 torrent

### 44. 增加/减少队列位置
- **接口**: `POST /api/v2/torrents/{topPrio|bottomPrio|increasePrio|decreasePrio}`
- **文件**: 
  - `private/scripts/mocha-init.js:1221`
  - `private/scripts/mocha-init.js:1244`
- **参数**: `hashes`
- **功能**: 调整 torrent 队列位置
- **使用场景**: 右键菜单调整优先级

---

## 传输控制接口

### 1. 获取全局上传限速
- **接口**: `GET /api/v2/transfer/uploadLimit`
- **文件**: `private/scripts/speedslider.js:35`
- **功能**: 获取全局上传速度限制
- **使用场景**: 速度滑块初始化

### 2. 设置全局上传限速
- **接口**: `POST /api/v2/transfer/setUploadLimit`
- **文件**: `private/uploadlimit.html:53`
- **参数**: `limit`
- **功能**: 设置全局上传速度限制
- **使用场景**: 全局上传限速对话框

### 3. 获取全局下载限速
- **接口**: `GET /api/v2/transfer/downloadLimit`
- **文件**: `private/scripts/speedslider.js:144`
- **功能**: 获取全局下载速度限制
- **使用场景**: 速度滑块初始化

### 4. 设置全局下载限速
- **接口**: `POST /api/v2/transfer/setDownloadLimit`
- **文件**: `private/downloadlimit.html:53`
- **参数**: `limit`
- **功能**: 设置全局下载速度限制
- **使用场景**: 全局下载限速对话框

### 5. 切换限速模式
- **接口**: `POST /api/v2/transfer/toggleSpeedLimitsMode`
- **文件**: `private/scripts/client.js:1102`
- **功能**: 在正常模式和备用限速模式之间切换
- **使用场景**: 点击限速模式切换按钮

### 6. 封禁 Peers
- **接口**: `POST /api/v2/transfer/banPeers`
- **文件**: `private/scripts/prop-peers.js:156`
- **参数**: `peers`
- **功能**: 封禁指定的 peer IP
- **使用场景**: Peers 列表中封禁 peer

---

## 同步接口

### 1. 获取主数据同步
- **接口**: `GET /api/v2/sync/maindata`
- **文件**: `private/scripts/client.js:756`
- **参数**: `rid` (请求 ID)
- **功能**: 获取增量同步数据（torrents、服务器状态、分类、标签等）
- **使用场景**: 主循环定期轮询更新数据

### 2. 获取 Torrent Peers 同步
- **接口**: `GET /api/v2/sync/torrentPeers`
- **文件**: `private/scripts/prop-peers.js:59`
- **参数**: `hash`, `rid`
- **功能**: 获取指定 torrent 的 peer 列表
- **使用场景**: 属性面板的"Peers"标签页

---

## RSS 接口

### 1. 获取 RSS 项目
- **接口**: `GET /api/v2/rss/items`
- **文件**: 
  - `private/views/rss.html:462`
  - `private/views/rssDownloader.html:453`
- **参数**: `withData`
- **功能**: 获取 RSS 订阅源和文章
- **使用场景**: RSS 页面显示订阅源

### 2. 添加 RSS Feed
- **接口**: `POST /api/v2/rss/addFeed`
- **文件**: `private/newfeed.html:45`
- **参数**: `url`, `path`
- **功能**: 添加新的 RSS 订阅源
- **使用场景**: 添加 Feed 对话框

### 3. 添加 RSS 文件夹
- **接口**: `POST /api/v2/rss/addFolder`
- **文件**: `private/newfolder.html:45`
- **参数**: `path`
- **功能**: 创建 RSS 文件夹
- **使用场景**: 添加文件夹对话框

### 4. 移动/重命名 RSS 项目
- **接口**: `POST /api/v2/rss/moveItem`
- **文件**: `private/rename_feed.html:54`
- **参数**: `itemPath`, `destPath`
- **功能**: 移动或重命名 RSS 订阅源/文件夹
- **使用场景**: 重命名 Feed 对话框

### 5. 删除 RSS 项目
- **接口**: `POST /api/v2/rss/removeItem`
- **文件**: `private/confirmfeeddeletion.html:29`
- **参数**: `path`
- **功能**: 删除 RSS 订阅源或文件夹
- **使用场景**: 确认删除 Feed 对话框

### 6. 刷新 RSS 项目
- **接口**: `POST /api/v2/rss/refreshItem`
- **文件**: `private/views/rss.html:712`
- **参数**: `itemPath`
- **功能**: 手动刷新 RSS 订阅源
- **使用场景**: 右键菜单刷新 Feed

### 7. 设置 Feed URL
- **接口**: `POST /api/v2/rss/setFeedURL`
- **文件**: `private/editfeedurl.html:55`
- **参数**: `path`, `url`
- **功能**: 修改 RSS 订阅源 URL
- **使用场景**: 编辑 Feed URL 对话框

### 8. 标记为已读
- **接口**: `POST /api/v2/rss/markAsRead`
- **文件**: 
  - `private/views/rss.html:822`
  - `private/views/rss.html:865`
- **参数**: `itemPath`, `articleId`
- **功能**: 标记 RSS 文章为已读
- **使用场景**: RSS 文章列表标记已读

### 9. 获取 RSS 规则
- **接口**: `GET /api/v2/rss/rules`
- **文件**: `private/views/rssDownloader.html:486`
- **功能**: 获取所有 RSS 自动下载规则
- **使用场景**: RSS 下载器页面

### 10. 设置 RSS 规则
- **接口**: `POST /api/v2/rss/setRule`
- **文件**: 
  - `private/views/rssDownloader.html:514`
  - `private/views/rssDownloader.html:649`
  - `private/newrule.html:43`
- **参数**: `ruleName`, `ruleDef`
- **功能**: 创建或修改 RSS 自动下载规则
- **使用场景**: RSS 下载器规则编辑

### 11. 重命名 RSS 规则
- **接口**: `POST /api/v2/rss/renameRule`
- **文件**: `private/rename_rule.html:54`
- **参数**: `ruleName`, `newRuleName`
- **功能**: 重命名 RSS 规则
- **使用场景**: 重命名规则对话框

### 12. 删除 RSS 规则
- **接口**: `POST /api/v2/rss/removeRule`
- **文件**: `private/confirmruledeletion.html:29`
- **参数**: `ruleName`
- **功能**: 删除 RSS 规则
- **使用场景**: 确认删除规则对话框

### 13. 获取匹配的文章
- **接口**: `GET /api/v2/rss/matchingArticles`
- **文件**: `private/views/rssDownloader.html:665`
- **参数**: `ruleName`
- **功能**: 获取匹配规则的 RSS 文章
- **使用场景**: RSS 下载器预览匹配结果

---

## 搜索接口

### 1. 开始搜索
- **接口**: `POST /api/v2/search/start`
- **文件**: `private/scripts/search.js:400`
- **参数**: `pattern`, `plugins`, `category`
- **功能**: 启动新的搜索任务
- **使用场景**: 搜索页面提交搜索

### 2. 停止搜索
- **接口**: `POST /api/v2/search/stop`
- **文件**: `private/scripts/search.js:425`
- **参数**: `id`
- **功能**: 停止正在运行的搜索任务
- **使用场景**: 停止搜索按钮

### 3. 删除搜索
- **接口**: `POST /api/v2/search/delete`
- **文件**: `private/scripts/search.js:253`
- **参数**: `id`
- **功能**: 删除搜索任务
- **使用场景**: 关闭搜索标签页

### 4. 获取搜索结果
- **接口**: `GET /api/v2/search/results`
- **文件**: `private/scripts/search.js:778`
- **参数**: `id`, `limit`, `offset`
- **功能**: 获取搜索结果
- **使用场景**: 搜索结果页面显示

### 5. 获取搜索插件
- **接口**: `GET /api/v2/search/plugins`
- **文件**: `private/scripts/search.js:646`
- **功能**: 获取已安装的搜索插件列表
- **使用场景**: 搜索页面插件选择器

### 6. 安装搜索插件
- **接口**: `POST /api/v2/search/installPlugin`
- **文件**: `private/views/installsearchplugin.html:70`
- **参数**: `sources`
- **功能**: 安装新的搜索插件
- **使用场景**: 安装插件对话框

### 7. 卸载搜索插件
- **接口**: `POST /api/v2/search/uninstallPlugin`
- **文件**: `private/views/searchplugins.html:133`
- **参数**: `names`
- **功能**: 卸载搜索插件
- **使用场景**: 插件管理页面

### 8. 启用/禁用搜索插件
- **接口**: `POST /api/v2/search/enablePlugin`
- **文件**: `private/views/searchplugins.html:147`
- **参数**: `names`, `enable`
- **功能**: 启用或禁用搜索插件
- **使用场景**: 插件管理页面

### 9. 更新搜索插件
- **接口**: `POST /api/v2/search/updatePlugins`
- **文件**: `private/views/searchplugins.html:157`
- **功能**: 更新所有搜索插件
- **使用场景**: 插件管理页面更新按钮

---

## 日志接口

### 1. 获取主日志
- **接口**: `GET /api/v2/log/main`
- **文件**: `private/views/log.html:345`
- **参数**: `normal`, `info`, `warning`, `critical`, `last_known_id`
- **功能**: 获取应用主日志
- **使用场景**: 日志窗口的"日志"标签页

### 2. 获取 Peer 日志
- **接口**: `GET /api/v2/log/peers`
- **文件**: `private/views/log.html:355`
- **参数**: `last_known_id`
- **功能**: 获取 peer 连接日志
- **使用场景**: 日志窗口的"Peers"标签页

---

## 接口使用统计

### 按功能模块分类统计:
- **Torrent 管理**: 44 个接口
- **传输控制**: 6 个接口
- **应用程序**: 11 个接口
- **RSS**: 13 个接口
- **搜索**: 9 个接口
- **同步**: 2 个接口
- **认证**: 2 个接口
- **日志**: 2 个接口

**总计**: 89 个不同的 HTTP 接口

### 按 HTTP 方法分类:
- **GET 请求**: 约 25 个（主要用于查询数据）
- **POST 请求**: 约 64 个（主要用于修改数据）

---

## 关键技术特点

### 1. 数据同步机制
- 使用 `/api/v2/sync/maindata` 进行增量同步
- 通过 `rid` (request ID) 参数实现增量更新
- 定期轮询（通常每秒一次）保持数据最新

### 2. 缓存机制
- 应用启动时缓存 `buildInfo`、`preferences`、`version`
- 使用 `window.qBittorrent.Cache` 对象管理缓存
- 设置更改时自动更新本地缓存

### 3. 实时更新
- Torrent 列表使用 `sync/maindata` 实时更新
- 属性面板使用定时器（10秒）刷新数据
- Peers 列表使用 `sync/torrentPeers` 增量同步

### 4. 批量操作
- 大部分 torrent 操作支持多选（通过 `hashes` 参数）
- 使用 `|` 分隔多个 hash 值
- 支持 `all` 关键字操作所有 torrent

### 5. 表单提交
- Torrent 添加使用传统表单提交（支持文件上传）
- 其他操作使用 `fetch()` API
- 使用 `URLSearchParams` 构建请求参数

### 6. 错误处理
- 检查 `response.ok` 判断请求是否成功
- 失败时通常显示错误消息或重试
- 部分操作有确认对话框

---

## 代码示例

### 示例 1: 启动 Torrent
```javascript
fetch("api/v2/torrents/start", {
    method: "POST",
    body: new URLSearchParams({
        hashes: "hash1|hash2|hash3"
    })
});
```

### 示例 2: 获取同步数据
```javascript
const url = new URL("api/v2/sync/maindata", window.location);
url.search = new URLSearchParams({
    rid: lastRequestId
});
fetch(url, {
    method: "GET",
    cache: "no-store"
})
.then(async (response) => {
    const data = await response.json();
    // 处理增量数据
});
```

### 示例 3: 设置文件优先级
```javascript
fetch("api/v2/torrents/filePrio", {
    method: "POST",
    body: new URLSearchParams({
        hash: torrentHash,
        id: fileIds.join("|"),
        priority: 1  // 0=不下载, 1=普通, 6=高, 7=最高
    })
});
```

### 示例 4: 添加 Torrent（表单提交）
```html
<form action="api/v2/torrents/add" 
      enctype="multipart/form-data" 
      method="post">
    <input type="file" name="torrents">
    <input type="text" name="savepath">
    <input type="text" name="category">
    <button type="submit">添加</button>
</form>
```

---

## 总结

qBittorrent WebUI 前端通过 89 个不同的 HTTP API 接口实现了完整的 BitTorrent 客户端功能，包括：

1. **完整的 Torrent 生命周期管理**: 添加、启动、停止、删除、重命名等
2. **精细的下载控制**: 文件优先级、限速、队列管理、顺序下载等
3. **高级功能**: RSS 订阅、搜索插件、自动下载规则等
4. **实时监控**: 通过增量同步机制实时更新 UI
5. **灵活的组织**: 分类、标签、tracker 管理等

前端代码主要使用 MooTools 框架和原生 `fetch()` API，采用模块化设计，每个功能模块对应独立的 JavaScript 文件，代码结构清晰，易于维护和扩展。
