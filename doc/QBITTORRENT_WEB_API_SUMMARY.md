# qBittorrent Web API 完整指南

## 概述

qBittorrent 提供了完整的 RESTful Web API,允许通过 HTTP 请求远程控制 BitTorrent 客户端。API 版本: **v2.11.4**

## API 基础信息

### 基础 URL
```
http://localhost:8080/api/v2
```

### API 路径格式
```
/api/v2/{scope}/{action}
```

其中:
- `scope`: 控制器名称(如 torrents, app, transfer 等)
- `action`: 具体操作名称

### 认证方式

1. **登录获取 Cookie**
   ```bash
   curl -X POST http://localhost:8080/api/v2/auth/login \
     -d "username=admin&password=adminpass"
   ```

2. **后续请求携带 Cookie**
   ```bash
   curl http://localhost:8080/api/v2/torrents/info \
     --cookie "SID=your_session_id"
   ```

## API 控制器分类

### 1. Authentication (认证) - `/api/v2/auth`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | 登录获取会话 |
| `/auth/logout` | POST | 登出销毁会话 |

**登录示例:**
```bash
curl -X POST http://localhost:8080/api/v2/auth/login \
  -d "username=admin&password=adminpass"
```

---

### 2. Application (应用) - `/api/v2/app`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/app/webapiVersion` | GET | 获取 Web API 版本 |
| `/app/version` | GET | 获取 qBittorrent 版本 |
| `/app/buildInfo` | GET | 获取构建信息 |
| `/app/shutdown` | POST | 关闭 qBittorrent |
| `/app/preferences` | GET | 获取应用偏好设置 |
| `/app/setPreferences` | POST | 设置应用偏好 |
| `/app/defaultSavePath` | GET | 获取默认保存路径 |
| `/app/sendTestEmail` | POST | 发送测试邮件 |
| `/app/getDirectoryContent` | GET | 获取目录内容 |
| `/app/networkInterfaceList` | GET | 获取网络接口列表 |
| `/app/networkInterfaceAddressList` | GET | 获取网络接口地址列表 |
| `/app/cookies` | GET | 获取 Cookies |
| `/app/setCookies` | POST | 设置 Cookies |

**获取版本示例:**
```bash
curl http://localhost:8080/api/v2/app/version
# 返回: v4.5.4
```

---

### 3. Torrents (种子管理) - `/api/v2/torrents`

#### 查询操作 (GET)

| 接口 | 说明 |
|------|------|
| `/torrents/info` | 获取种子列表 |
| `/torrents/count` | 获取种子数量 |
| `/torrents/properties` | 获取种子属性 |
| `/torrents/trackers` | 获取 Tracker 列表 |
| `/torrents/webseeds` | 获取 Web Seeds |
| `/torrents/files` | 获取文件列表 |
| `/torrents/pieceHashes` | 获取分片哈希 |
| `/torrents/pieceStates` | 获取分片状态 |
| `/torrents/categories` | 获取分类列表 |
| `/torrents/tags` | 获取标签列表 |
| `/torrents/uploadLimit` | 获取上传限速 |
| `/torrents/downloadLimit` | 获取下载限速 |
| `/torrents/SSLParameters` | 获取 SSL 参数 |
| `/torrents/export` | 导出种子文件 |

**获取种子列表示例:**
```bash
curl "http://localhost:8080/api/v2/torrents/info?filter=all&sort=name" \
  --cookie "SID=your_session_id"
```

参数:
- `filter`: all, downloading, seeding, completed, paused, active, inactive, resumed, stalled
- `category`: 按分类筛选
- `tag`: 按标签筛选
- `sort`: 排序字段
- `reverse`: true/false 反向排序
- `limit`: 限制返回数量
- `offset`: 偏移量

#### 修改操作 (POST)

| 接口 | 说明 |
|------|------|
| `/torrents/add` | 添加种子 |
| `/torrents/delete` | 删除种子 |
| `/torrents/start` | 开始下载 |
| `/torrents/stop` | 停止下载 |
| `/torrents/recheck` | 重新检查 |
| `/torrents/reannounce` | 重新汇报 |
| `/torrents/rename` | 重命名种子 |
| `/torrents/renameFile` | 重命名文件 |
| `/torrents/renameFolder` | 重命名文件夹 |
| `/torrents/setLocation` | 设置保存位置 |
| `/torrents/setSavePath` | 设置保存路径 |
| `/torrents/setDownloadPath` | 设置下载路径 |
| `/torrents/setCategory` | 设置分类 |
| `/torrents/createCategory` | 创建分类 |
| `/torrents/editCategory` | 编辑分类 |
| `/torrents/removeCategories` | 删除分类 |
| `/torrents/addTags` | 添加标签 |
| `/torrents/setTags` | 设置标签 |
| `/torrents/removeTags` | 移除标签 |
| `/torrents/createTags` | 创建标签 |
| `/torrents/deleteTags` | 删除标签 |
| `/torrents/addTrackers` | 添加 Tracker |
| `/torrents/editTracker` | 编辑 Tracker |
| `/torrents/removeTrackers` | 删除 Tracker |
| `/torrents/addPeers` | 添加对等节点 |
| `/torrents/addWebSeeds` | 添加 Web Seeds |
| `/torrents/editWebSeed` | 编辑 Web Seed |
| `/torrents/removeWebSeeds` | 删除 Web Seeds |
| `/torrents/filePrio` | 设置文件优先级 |
| `/torrents/setUploadLimit` | 设置上传限速 |
| `/torrents/setDownloadLimit` | 设置下载限速 |
| `/torrents/setShareLimits` | 设置分享限制 |
| `/torrents/setSSLParameters` | 设置 SSL 参数 |
| `/torrents/increasePrio` | 提高优先级 |
| `/torrents/decreasePrio` | 降低优先级 |
| `/torrents/topPrio` | 最高优先级 |
| `/torrents/bottomPrio` | 最低优先级 |
| `/torrents/setAutoManagement` | 设置自动管理 |
| `/torrents/setSuperSeeding` | 设置超级做种 |
| `/torrents/setForceStart` | 设置强制开始 |
| `/torrents/toggleSequentialDownload` | 切换顺序下载 |
| `/torrents/toggleFirstLastPiecePrio` | 切换首尾分片优先 |

**添加种子示例:**
```bash
# 通过 URL 添加
curl -X POST http://localhost:8080/api/v2/torrents/add \
  --cookie "SID=your_session_id" \
  -d "urls=magnet:?xt=urn:btih:..." \
  -d "savepath=/downloads" \
  -d "category=movies" \
  -d "tags=hd,action"

# 通过文件上传添加
curl -X POST http://localhost:8080/api/v2/torrents/add \
  --cookie "SID=your_session_id" \
  -F "torrents=@/path/to/file.torrent" \
  -F "savepath=/downloads"
```

**添加种子参数说明:**
- `urls`: 种子 URL 或 magnet 链接(多个用换行分隔)
- `torrents`: 种子文件(multipart/form-data)
- `savepath`: 保存路径
- `category`: 分类
- `tags`: 标签(逗号分隔)
- `skip_checking`: 跳过哈希检查(true/false)
- `paused`: 暂停状态添加(true/false)
- `stopped`: 停止状态添加(true/false)
- `sequentialDownload`: 顺序下载(true/false)
- `firstLastPiecePrio`: 首尾分片优先(true/false)
- `rename`: 重命名种子
- `upLimit`: 上传限速(bytes/s, -1 为无限制)
- `dlLimit`: 下载限速(bytes/s, -1 为无限制)
- `ratioLimit`: 分享率限制
- `seedingTimeLimit`: 做种时间限制(分钟)
- `autoTMM`: 自动种子管理(true/false)
- `contentLayout`: 内容布局(Original/Subfolder/NoSubfolder)

**删除种子示例:**
```bash
curl -X POST http://localhost:8080/api/v2/torrents/delete \
  --cookie "SID=your_session_id" \
  -d "hashes=hash1|hash2|all" \
  -d "deleteFiles=true"
```

**开始/停止种子:**
```bash
# 开始
curl -X POST http://localhost:8080/api/v2/torrents/start \
  --cookie "SID=your_session_id" \
  -d "hashes=hash1|hash2|all"

# 停止
curl -X POST http://localhost:8080/api/v2/torrents/stop \
  --cookie "SID=your_session_id" \
  -d "hashes=hash1|hash2|all"
```

**设置分类:**
```bash
# 创建分类
curl -X POST http://localhost:8080/api/v2/torrents/createCategory \
  --cookie "SID=your_session_id" \
  -d "category=movies" \
  -d "savePath=/downloads/movies"

# 设置种子分类
curl -X POST http://localhost:8080/api/v2/torrents/setCategory \
  --cookie "SID=your_session_id" \
  -d "hashes=hash1|hash2" \
  -d "category=movies"
```

---

### 4. Transfer (传输) - `/api/v2/transfer`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/transfer/info` | GET | 获取传输信息(全局速度、流量等) |
| `/transfer/speedLimitsMode` | GET | 获取限速模式 |
| `/transfer/setSpeedLimitsMode` | POST | 设置限速模式 |
| `/transfer/toggleSpeedLimitsMode` | POST | 切换限速模式 |
| `/transfer/uploadLimit` | GET | 获取全局上传限速 |
| `/transfer/downloadLimit` | GET | 获取全局下载限速 |
| `/transfer/setUploadLimit` | POST | 设置全局上传限速 |
| `/transfer/setDownloadLimit` | POST | 设置全局下载限速 |
| `/transfer/banPeers` | POST | 封禁对等节点 |

**获取传输信息示例:**
```bash
curl http://localhost:8080/api/v2/transfer/info \
  --cookie "SID=your_session_id"
```

返回数据包括:
- `dl_info_speed`: 当前下载速度
- `up_info_speed`: 当前上传速度
- `dl_info_data`: 本次会话下载量
- `up_info_data`: 本次会话上传量
- `dl_rate_limit`: 下载限速
- `up_rate_limit`: 上传限速

**设置全局限速:**
```bash
# 设置上传限速为 1MB/s (1048576 bytes/s)
curl -X POST http://localhost:8080/api/v2/transfer/setUploadLimit \
  --cookie "SID=your_session_id" \
  -d "limit=1048576"

# 设置下载限速为 5MB/s
curl -X POST http://localhost:8080/api/v2/transfer/setDownloadLimit \
  --cookie "SID=your_session_id" \
  -d "limit=5242880"
```

---

### 5. Sync (同步) - `/api/v2/sync`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/sync/maindata` | GET | 获取主数据(增量同步) |
| `/sync/torrentPeers` | GET | 获取种子对等节点 |

**主数据同步示例:**
```bash
# 首次请求
curl "http://localhost:8080/api/v2/sync/maindata?rid=0" \
  --cookie "SID=your_session_id"

# 后续增量请求(使用返回的 rid)
curl "http://localhost:8080/api/v2/sync/maindata?rid=123" \
  --cookie "SID=your_session_id"
```

返回数据包括:
- `rid`: 响应 ID(用于下次请求)
- `full_update`: 是否全量更新
- `torrents`: 种子状态变化
- `torrents_removed`: 已删除的种子
- `categories`: 分类变化
- `tags`: 标签变化
- `server_state`: 服务器状态

---

### 6. RSS - `/api/v2/rss`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/rss/addFolder` | POST | 添加 RSS 文件夹 |
| `/rss/addFeed` | POST | 添加 RSS 订阅 |
| `/rss/setFeedURL` | POST | 设置订阅 URL |
| `/rss/removeItem` | POST | 删除项目 |
| `/rss/moveItem` | POST | 移动项目 |
| `/rss/items` | GET | 获取 RSS 项目 |
| `/rss/markAsRead` | POST | 标记为已读 |
| `/rss/refreshItem` | POST | 刷新项目 |
| `/rss/setRule` | POST | 设置自动下载规则 |
| `/rss/renameRule` | POST | 重命名规则 |
| `/rss/removeRule` | POST | 删除规则 |
| `/rss/rules` | GET | 获取规则列表 |
| `/rss/matchingArticles` | GET | 获取匹配的文章 |

**添加 RSS 订阅示例:**
```bash
curl -X POST http://localhost:8080/api/v2/rss/addFeed \
  --cookie "SID=your_session_id" \
  -d "url=https://example.com/rss.xml" \
  -d "path=MyFeeds/TechNews"
```

---

### 7. Search (搜索) - `/api/v2/search`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/search/start` | POST | 开始搜索 |
| `/search/stop` | POST | 停止搜索 |
| `/search/status` | GET | 获取搜索状态 |
| `/search/results` | GET | 获取搜索结果 |
| `/search/delete` | POST | 删除搜索任务 |
| `/search/plugins` | GET | 获取搜索插件列表 |
| `/search/installPlugin` | POST | 安装搜索插件 |
| `/search/uninstallPlugin` | POST | 卸载搜索插件 |
| `/search/enablePlugin` | POST | 启用/禁用插件 |
| `/search/updatePlugins` | POST | 更新插件 |

**搜索示例:**
```bash
# 开始搜索
curl -X POST http://localhost:8080/api/v2/search/start \
  --cookie "SID=your_session_id" \
  -d "pattern=ubuntu" \
  -d "plugins=all" \
  -d "category=all"

# 获取结果(使用返回的 id)
curl "http://localhost:8080/api/v2/search/results?id=1" \
  --cookie "SID=your_session_id"
```

---

### 8. Log (日志) - `/api/v2/log`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/log/main` | GET | 获取主日志 |
| `/log/peers` | GET | 获取对等节点日志 |

**获取日志示例:**
```bash
curl "http://localhost:8080/api/v2/log/main?last_known_id=-1" \
  --cookie "SID=your_session_id"
```

---

### 9. Torrent Creator (种子创建) - `/api/v2/torrentcreator`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/torrentcreator/addTask` | POST | 添加创建任务 |
| `/torrentcreator/deleteTask` | POST | 删除创建任务 |

---

## 完整使用示例

### Python 示例

```python
import requests

class QBittorrentClient:
    def __init__(self, host='http://localhost:8080', username='admin', password='adminpass'):
        self.host = host
        self.session = requests.Session()
        self.login(username, password)
    
    def login(self, username, password):
        """登录"""
        url = f'{self.host}/api/v2/auth/login'
        data = {'username': username, 'password': password}
        response = self.session.post(url, data=data)
        if response.text != 'Ok.':
            raise Exception('Login failed')
    
    def get_torrents(self, filter='all'):
        """获取种子列表"""
        url = f'{self.host}/api/v2/torrents/info'
        params = {'filter': filter}
        response = self.session.get(url, params=params)
        return response.json()
    
    def add_torrent(self, urls, savepath=None, category=None):
        """添加种子"""
        url = f'{self.host}/api/v2/torrents/add'
        data = {'urls': urls}
        if savepath:
            data['savepath'] = savepath
        if category:
            data['category'] = category
        response = self.session.post(url, data=data)
        return response.text
    
    def delete_torrent(self, hash, delete_files=False):
        """删除种子"""
        url = f'{self.host}/api/v2/torrents/delete'
        data = {
            'hashes': hash,
            'deleteFiles': str(delete_files).lower()
        }
        response = self.session.post(url, data=data)
        return response.text
    
    def start_torrent(self, hash):
        """开始种子"""
        url = f'{self.host}/api/v2/torrents/start'
        data = {'hashes': hash}
        response = self.session.post(url, data=data)
        return response.text
    
    def stop_torrent(self, hash):
        """停止种子"""
        url = f'{self.host}/api/v2/torrents/stop'
        data = {'hashes': hash}
        response = self.session.post(url, data=data)
        return response.text
    
    def get_transfer_info(self):
        """获取传输信息"""
        url = f'{self.host}/api/v2/transfer/info'
        response = self.session.get(url)
        return response.json()
    
    def set_download_limit(self, limit):
        """设置全局下载限速 (bytes/s)"""
        url = f'{self.host}/api/v2/transfer/setDownloadLimit'
        data = {'limit': limit}
        response = self.session.post(url, data=data)
        return response.text

# 使用示例
if __name__ == '__main__':
    client = QBittorrentClient()
    
    # 获取所有种子
    torrents = client.get_torrents()
    print(f"Total torrents: {len(torrents)}")
    
    # 添加种子
    magnet = "magnet:?xt=urn:btih:..."
    result = client.add_torrent(magnet, savepath="/downloads", category="movies")
    print(f"Add torrent: {result}")
    
    # 获取传输信息
    info = client.get_transfer_info()
    print(f"Download speed: {info['dl_info_speed']} bytes/s")
    print(f"Upload speed: {info['up_info_speed']} bytes/s")
    
    # 设置下载限速为 5MB/s
    client.set_download_limit(5 * 1024 * 1024)
```

### JavaScript/Node.js 示例

```javascript
const axios = require('axios');

class QBittorrentClient {
    constructor(host = 'http://localhost:8080', username = 'admin', password = 'adminpass') {
        this.host = host;
        this.client = axios.create({
            baseURL: host,
            withCredentials: true
        });
        this.login(username, password);
    }
    
    async login(username, password) {
        const response = await this.client.post('/api/v2/auth/login', 
            `username=${username}&password=${password}`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );
        if (response.data !== 'Ok.') {
            throw new Error('Login failed');
        }
    }
    
    async getTorrents(filter = 'all') {
        const response = await this.client.get('/api/v2/torrents/info', {
            params: { filter }
        });
        return response.data;
    }
    
    async addTorrent(urls, options = {}) {
        const data = new URLSearchParams();
        data.append('urls', urls);
        if (options.savepath) data.append('savepath', options.savepath);
        if (options.category) data.append('category', options.category);
        
        const response = await this.client.post('/api/v2/torrents/add', data);
        return response.data;
    }
    
    async deleteTorrent(hash, deleteFiles = false) {
        const data = new URLSearchParams();
        data.append('hashes', hash);
        data.append('deleteFiles', deleteFiles);
        
        const response = await this.client.post('/api/v2/torrents/delete', data);
        return response.data;
    }
    
    async getTransferInfo() {
        const response = await this.client.get('/api/v2/transfer/info');
        return response.data;
    }
}

// 使用示例
(async () => {
    const client = new QBittorrentClient();
    
    // 获取所有种子
    const torrents = await client.getTorrents();
    console.log(`Total torrents: ${torrents.length}`);
    
    // 添加种子
    const magnet = 'magnet:?xt=urn:btih:...';
    await client.addTorrent(magnet, { 
        savepath: '/downloads', 
        category: 'movies' 
    });
    
    // 获取传输信息
    const info = await client.getTransferInfo();
    console.log(`Download speed: ${info.dl_info_speed} bytes/s`);
})();
```

### Bash/cURL 完整示例

```bash
#!/bin/bash

HOST="http://localhost:8080"
USERNAME="admin"
PASSWORD="adminpass"
COOKIE_FILE="/tmp/qbt_cookie.txt"

# 登录
login() {
    curl -X POST "$HOST/api/v2/auth/login" \
        -d "username=$USERNAME&password=$PASSWORD" \
        -c "$COOKIE_FILE"
}

# 获取种子列表
get_torrents() {
    curl "$HOST/api/v2/torrents/info" \
        -b "$COOKIE_FILE"
}

# 添加种子
add_torrent() {
    local url=$1
    local savepath=$2
    curl -X POST "$HOST/api/v2/torrents/add" \
        -b "$COOKIE_FILE" \
        -d "urls=$url" \
        -d "savepath=$savepath"
}

# 删除种子
delete_torrent() {
    local hash=$1
    curl -X POST "$HOST/api/v2/torrents/delete" \
        -b "$COOKIE_FILE" \
        -d "hashes=$hash" \
        -d "deleteFiles=false"
}

# 获取传输信息
get_transfer_info() {
    curl "$HOST/api/v2/transfer/info" \
        -b "$COOKIE_FILE"
}

# 使用示例
login
get_torrents | jq '.'
add_torrent "magnet:?xt=urn:btih:..." "/downloads"
get_transfer_info | jq '.'
```

## 安全注意事项

1. **启用 HTTPS**: 生产环境应启用 HTTPS 加密传输
2. **强密码**: 使用强密码保护 Web UI
3. **IP 白名单**: 配置允许访问的 IP 地址范围
4. **CSRF 保护**: 默认启用,不要禁用
5. **Host Header 验证**: 防止 Host Header 攻击
6. **会话超时**: 设置合理的会话超时时间

## 配置 Web UI

在 qBittorrent 设置中:
1. 工具 → 选项 → Web UI
2. 启用 Web 用户界面
3. 设置端口(默认 8080)
4. 设置用户名和密码
5. 可选: 启用 HTTPS
6. 可选: 配置 IP 白名单

## 常见问题

### 1. 如何获取种子的 hash?
```bash
curl "http://localhost:8080/api/v2/torrents/info" \
  --cookie "SID=xxx" | jq '.[].hash'
```

### 2. 如何批量操作种子?
使用 `|` 分隔多个 hash,或使用 `all` 操作所有种子:
```bash
# 多个种子
-d "hashes=hash1|hash2|hash3"

# 所有种子
-d "hashes=all"
```

### 3. 如何监控下载进度?
使用 `/sync/maindata` 接口进行增量同步,效率更高。

### 4. 速度限制单位是什么?
所有速度限制的单位都是 **bytes/s** (字节/秒)。
- 1 MB/s = 1048576 bytes/s
- -1 表示无限制

## 相关文件位置

- **Web API 实现**: `/Users/soonco/Work/qBittorrent_514/src/webui/api/`
- **主控制器**: 
  - `torrentscontroller.cpp/h` - 种子管理
  - `appcontroller.cpp/h` - 应用设置
  - `transfercontroller.cpp/h` - 传输控制
  - `synccontroller.cpp/h` - 同步接口
  - `authcontroller.cpp/h` - 认证
  - `rsscontroller.cpp/h` - RSS 订阅
  - `searchcontroller.cpp/h` - 搜索功能
  - `logcontroller.cpp/h` - 日志
- **HTTP 服务器**: `/Users/soonco/Work/qBittorrent_514/src/base/http/`
- **Web 应用**: `/Users/soonco/Work/qBittorrent_514/src/webui/webapplication.cpp/h`

## 总结

qBittorrent Web API 提供了完整的远程控制能力,涵盖:
- ✅ 种子添加、删除、启动、停止
- ✅ 分类和标签管理
- ✅ Tracker 管理
- ✅ 文件优先级设置
- ✅ 速度限制控制
- ✅ RSS 订阅和自动下载
- ✅ 搜索功能
- ✅ 实时状态同步
- ✅ 日志查看

所有操作都通过 RESTful API 实现,支持各种编程语言和工具集成。
