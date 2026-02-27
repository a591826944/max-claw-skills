# xhs-publisher Skill

## 小红书云端全自动发帖

无需浏览器，纯云端 HTTP 调用，支持图文发帖（带图片）。

## 能力

- ✅ 图文笔记发布（带封面图）
- ✅ 自定义标题、正文、话题标签
- ✅ 公开 / 私密发布
- ✅ 多图上传
- ✅ Cookie 有效期验证

## 快速开始

### 第一步：配置 Cookie

首次使用前需要配置你自己的小红书 Cookie：

1. 打开电脑浏览器，访问 https://creator.xiaohongshu.com 并登录
2. 按 **F12** 打开开发者工具
3. 切换到 **Application** 标签 → 左侧 **Cookies → https://creator.xiaohongshu.com**
4. 使用浏览器插件（推荐 [Cookie-Editor](https://cookie-editor.com/) 或 EditThisCookie）导出为 JSON 格式
5. 保存到 `credentials/xhs_cookies.json`

### 第二步：验证配置

```bash
python3 scripts/xhs_publish.py --check
```

输出 `✅ Cookie 有效，认证成功` 即可使用。

### 第三步：发帖

```bash
python3 scripts/xhs_publish.py \
  --title "帖子标题（≤20字）" \
  --content "帖子正文内容" \
  --tags "标签1,标签2,标签3" \
  --images "封面图.png"
```

## Cookie 文件格式

`credentials/xhs_cookies.json` 为 JSON 数组格式：

```json
[
  {"name": "a1", "value": "..."},
  {"name": "web_session", "value": "..."},
  {"name": "access-token-creator.xiaohongshu.com", "value": "..."}
]
```

> ⚠️ **注意**：Cookie 文件包含个人登录信息，请勿分享给他人，也不要提交到公开代码库。

## 技术细节

### 签名算法
小红书 API 需要三个自定义请求头：
- `x-s`：基于 URI + Body + 时间戳的 MD5 签名，经自定义 Base64 编码
- `x-t`：时间戳（毫秒）
- `x-s-common`：包含设备/客户端信息的 Base64 编码 JSON

### 图片上传流程
1. `GET /api/media/v1/upload/web/permit` → 获取上传 token 和 file_id
2. `PUT https://ros-upload.xiaohongshu.com/{file_id}` 带 `X-Cos-Security-Token` 上传图片
3. 发布时在 `image_info.images` 中引用 file_id

### 发布接口
- URL: `POST https://edith.xiaohongshu.com/web_api/sns/v2/note`
- `common.type` 必须是字符串 `"normal"`（非整数）
- 必须携带至少一张图片

## 依赖

- Python 3（标准库，无需额外安装）
- curl（系统自带）

## .gitignore

`credentials/` 目录已在 `.gitignore` 中，Cookie 文件不会被提交到代码库。
