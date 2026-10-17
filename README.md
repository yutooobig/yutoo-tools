# 项目合集（单仓库聚合）

用一个仓库、一个站点，把所有纯静态小项目挂在同一个域名下的不同子路径：

```
https://你的域名/                   → 导航首页（预渲染的静态 HTML）
https://你的域名/projects/demo-a/   → 项目 A
https://你的域名/projects/demo-b/   → 项目 B
```

零依赖、零运行时 JS 依赖：首页是构建时生成的静态 HTML，卡片全部写在 HTML 里，禁用 JavaScript 也能正常显示和跳转。搜索框是一点渐进增强，仅在有 JS 时生效。

## 目录结构

```
site-hub/
├── _template.html          # 首页模板（改样式改这里）
├── build.py                # 读 projects.json，生成 index.html
├── index.html              # 生成的首页，不要手改，会被覆盖
├── projects.json           # 项目清单
├── 404.html
├── _headers                # Cloudflare 响应头（GitHub Pages 忽略）
├── _redirects              # Cloudflare 重定向规则（GitHub Pages 忽略）
├── add-project.py          # 一键把别的仓库拉进来
├── projects/
│   ├── demo-a/
│   └── demo-b/
└── .github/workflows/pages.yml
```

## 加一个新项目

**方式一：直接丢进目录（最简单）**

```
projects/我的工具/index.html   ← 就这一步，首页自动收录
```

目录里只要有 `index.html` 就会被扫到，标题默认用目录名。

**方式二：想自定义标题、描述、标签**

在 `projects.json` 加一条（`name` 必须和目录名一致）：

```json
{
  "name": "我的工具",
  "title": "卡片上显示的标题",
  "desc": "一句话描述",
  "tags": ["工具"]
}
```

也可以放外链项目，不占 `projects/` 目录：

```json
{ "name": "外部站", "title": "另一个站", "url": "https://example.com/" }
```

**方式三：从已有 GitHub 仓库拉**

```bash
python3 add-project.py https://github.com/你的用户名/你的项目 "我的工具"
```

克隆到 `projects/你的项目/`、删掉 `.git`、注册到 `projects.json`、扫描绝对路径引用，最后自动重跑 `build.py`。

## ⚠️ 改完必须重新构建

首页 `index.html` 是 `build.py` 生成出来的静态 HTML，**不是实时读 `projects.json`**。改了项目文件或 json，要跑一次：

```bash
python3 build.py
```

然后**硬刷新**浏览器（Mac `Cmd+Shift+R` / Windows `Ctrl+F5`），否则可能还是缓存里的旧页面。

首页页脚会显示「构建于 2026-10-17 15:30」这样的时间戳。**刷新后时间戳没变，就是没构建成功或者被缓存了。**

不�` 生成出来的静态 HTML，**不是实时读 `projects.json`**。改了项目文件或 json，要跑一次：

```bash
python3 build.py
```

然后**硬刷新**浏览器（Mac `Cmd+Shift+R` / Windows `Ctrl+F5`），否则可能还是缓存里的旧页面。

首页页脚会显示「构建于 2026-10-17 15:30」这样的时间戳。**刷新后时间戳没变，就是没构建成功或者被缓存了。**

不想手动跑就执行 `./serve.sh`，它会先构建再起服务。

## 本地预览

```bash
cd site-hub
chmod +x serve.sh
./serve.sh          # 构建 + 起服务，一条命令
# 打开 http://localhost:8080
```

Windows 或不想用脚本：

```bash
python build.py
python -m http.server 8080
```

纯静态，也可以直接双击 `index.html` 打开（已不再依赖 fetch）。

## 部署到 GitHub Pages

1. 新建仓库，把所有内容推到 `main`（记得把生成的 `index.html` 一起提交）
2. Settings → Pages → Source 选 **GitHub Actions**
3. 地址为 `https://用户名.github.io/仓库名/`

工作流里可以在上传前加一步 `python3 build.py`，这样不用手动生成：

```yaml
      - run: python3 build.py
```

> 项目页带 `/仓库名/` 前缀，站点内部全部用相对路径，不需要改任何东西。

## 部署到 Cloudflare Pages

- 连接 Git 仓库
- Framework preset：`None`
- Build command：留空（`index.html` 已提交）或填 `python3 build.py`
- Build output directory：`/`

命令行：

```bash
npx wrangler pages deploy . --project-name=site-hub
```

## 四个必须知道的坑

**1. 绝对路径会 404（最常见的白屏原因）**

`<script src="/app.js">`、`<link href="/style.css">`、`fetch('/data.json')` 一旦放到子路径下就指到域名根，直接 404。改成 `./app.js`、`style.css`、`./data.json`。

**2. 目录要带尾斜杠**

链接一律写 `/projects/xxx/`。不带斜杠时，页面里的相对路径可能被解析成 `/projects/app.js`。

**3. 别把带 `functions/` 或 `_worker.js` 的项目直接拷进来**

Cloudflare Pages 会把这些当 Functions/Worker 执行，异常即 `Error 1101`。纯静态项目不需要它们，拷之前先删掉。注意这跟项目里浏览器端跑的 `<script>` 完全无关，客户端 JS 随便用。

**4. 「返回合集」要数清层级**

`projects/demo-a/index.html` 在 `/projects/demo-a/` 下，回首页是 `../../`（上两级）。写成 `../` 只会退到 `/projects/`，那里没有 index.html，就是 404。

子页面每深一层再加一个 `../`：

| 页面位置 | 返回首页写 |
|---|---|
| `/projects/foo/` | `../../` |
| `/projects/foo/sub/` | `../../../` |

不想数层级的话，用一段小 JS 自动算（适配根路径和 `/仓库名/` 两种部署）：

```js
var i = location.pathname.indexOf('/projects/');
if (i > -1) {
  document.querySelector('.back').href = location.pathname.slice(0, i + 1);
}
```

## 关于 1101

`Error 1101: Worker threw exception` = 服务端 JS 逻辑接管请求时抛了异常。排查顺序：

1. 仓库里是否有 `functions/`、`_worker.js`、`_middleware.js`、`_routes.json` → 删掉
2. 看实时日志拿堆栈：`npx wrangler pages deployment tail --project-name 项目名`
3. 新建只有 `index.html` 的空白项目测试 → 也报说明是账号/平台侧问题
4. 用 `*.pages.dev` 裸域名访问，排除自定义域与缓存干扰
�带尾斜杠**

链接一律写 `/projects/xxx/`。不带斜杠时，页面里的相对路径可能被解析成 `/projects/app.js`。

**3. 别把带 `functions/` 或 `_worker.js` 的项目直接拷进来**

Cloudflare Pages 会把这些当 Functions/Worker 执行，异常即 `Error 1101`。纯静态项目不需要它们，拷之前先删掉。注意这跟项目里浏览器端跑的 `<script>` 完全无关，客户端 JS 随便用。

**4. 「返回合集」要数清层级**

`projects/demo-a/index.html` 在 `/projects/demo-a/` 下，回首页是 `../../`（上两级）。写成 `../` 只会退到 `/projects/`，那里没有 index.html，就是 404。

子页面每深一层再加一个 `../`：

| 页面位置 | 返回首页写 |
|---|---|
| `/projects/foo/` | `../../` |
| `/projects/foo/sub/` | `../../../` |

不想数层级的话，用一段小 JS 自动算（适配根路径和 `/仓库名/` 两种部署）：

```js
var i = location.pathname.indexOf('/projects/');
if (i > -1) {
  document.querySelector('.back').href = location.pathname.slice(0, i + 1);
}
```

## 关于 1101

`Error 1101: Worker threw exception` = 服务端 JS 逻辑接管请求时抛了异常。排查顺序：

1. 仓库里是否有 `functions/`、`_worker.js`、`_middleware.js`、`_routes.json` → 删掉
2. 看实时日志拿堆栈：`npx wrangler pages deployment tail --project-name 项目名`
3. 新建只有 `index.html` 的空白项目测试 → 也报说明是账号/平台侧问题
4. 用 `*.pages.dev` 裸域名访问，排除自定义域与缓存干扰
