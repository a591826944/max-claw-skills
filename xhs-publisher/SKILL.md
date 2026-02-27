# SKILL.md - xhs-publisher

## 激活条件

当用户说：
- "帮我发小红书"
- "发一篇小红书"
- "发布到小红书"
- 或任何涉及小红书发帖的需求

## 首次使用 - 必须先配置 Cookie

**在发帖之前，先检查 Cookie 是否已配置：**

```bash
python3 scripts/xhs_publish.py --check
```

如果输出 `❌ Cookie 无效或已过期` 或文件不存在，按以下步骤引导用户配置：

---

### 获取小红书 Cookie（引导用户操作）

告诉用户：

> 需要你提供小红书的登录 Cookie，步骤如下：
>
> 1. 打开电脑浏览器，访问 https://creator.xiaohongshu.com
> 2. 登录你的小红书账号
> 3. 按 **F12** 打开开发者工具
> 4. 切换到 **Application（应用程序）** 标签
> 5. 左侧找到 **Cookies → https://creator.xiaohongshu.com**
> 6. 把所有 cookie 导出为 JSON 数组格式（可以用浏览器插件 "EditThisCookie" 或 "Cookie-Editor" 导出）
> 7. 把导出的 JSON 文件发给我

收到 Cookie 文件后，保存到 `credentials/xhs_cookies.json`（如目录不存在则创建）。

再次运行 `python3 scripts/xhs_publish.py --check` 验证。

---

## Cookie 文件格式

`credentials/xhs_cookies.json` 为 JSON 数组，每个元素包含 `name` 和 `value` 字段：

```json
[
  {"name": "a1", "value": "你的a1值"},
  {"name": "web_session", "value": "你的web_session值"},
  {"name": "access-token-creator.xiaohongshu.com", "value": "你的access-token值"}
]
```

关键 Cookie：
- `a1`：设备标识，长期有效
- `web_session`：会话 token，有效期约1年
- `access-token-creator.xiaohongshu.com`：创作者平台 token，有效期约1个月

---

## 发帖流程

### 1. 验证 Cookie

```bash
python3 scripts/xhs_publish.py --check
```

### 2. 准备内容

- 标题：≤20字，吸引眼球，带 emoji
- 正文：口语化，真实感，400-600字
- 标签：10个左右，覆盖核心词 + 长尾词
- 图片：至少1张（小红书不接受纯文字帖）

### 3. 发布

```bash
python3 scripts/xhs_publish.py \
  --title "标题" \
  --content "正文" \
  --tags "标签1,标签2,标签3" \
  --images "图片路径.png"
```

### 4. 私密发布（测试用）

```bash
python3 scripts/xhs_publish.py \
  --title "测试" \
  --content "测试内容" \
  --images "图片路径.png" \
  --private
```

---

## 注意事项

- `access-token` 有效期较短（约1个月），失效后需重新获取
- `web_session` 有效期约1年
- 发帖必须带至少一张图片（纯文字帖会被拒绝，返回 -9999）
- `common.type` 字段必须是字符串 `"normal"`（非整数 `1`）
- Cookie 文件路径：`credentials/xhs_cookies.json`（相对于 workspace 根目录）
