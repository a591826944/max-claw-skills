# xhs-publisher Skill

## 小红书云端自动发帖

无需浏览器，纯云端 HTTP 调用，支持图文发帖（带图片）。

## 能力

- ✅ 图文笔记发布（带封面图）
- ✅ 自定义标题、正文、话题标签
- ✅ 公开 / 私密发布
- ✅ 多图上传
- ✅ Cookie 有效期验证

## 使用方式

### CLI

```bash
# 验证 Cookie 是否有效
python3 scripts/xhs_publish.py --check

# 发布带图片的帖子
python3 scripts/xhs_publish.py \
  --title "帖子标题（≤20字）" \
  --content "帖子正文内容" \
  --tags "标签1,标签2,标签3" \
  --images "封面图.png"

# 私密发布（测试用）
python3 scripts/xhs_publish.py \
  --title "测试标题" \
  --content "测试内容" \
  --private
```

### Agent 用法

直接告诉 Agent：「帮我发一篇小红书，主题是 XXX」，Agent 会自动完成文案撰写、图片处理和发布。

## 配置

Cookie 文件放在 `credentials/xhs_cookies.json`（JSON 数组格式）。

获取方式：
1. 登录 [creator.xiaohongshu.com](https://creator.xiaohongshu.com)
2. F12 → Application → Cookies → 复制所有 cookie 为 JSON 格式保存

Cookie 有效期约1年（web_session），需到期前刷新。

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
