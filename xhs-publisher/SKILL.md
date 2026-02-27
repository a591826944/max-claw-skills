# SKILL.md - xhs-publisher

## 激活条件

当用户说：
- "帮我发小红书"
- "发一篇小红书"
- "发布到小红书"
- 或任何涉及小红书发帖的需求

## 环境要求

- Python 3（标准库，无需额外安装）
- Cookie 文件：`credentials/xhs_cookies.json`
- 发帖脚本：`scripts/xhs_publish.py`

## 执行流程

### 1. 验证 Cookie

```bash
python3 scripts/xhs_publish.py --check
```

如果失败，提示用户刷新 Cookie。

### 2. 准备内容

**如果用户没提供图片：**
- 可使用 `image_synthesize` 工具生成封面图
- 保存到 `/workspace/imgs/xhs_cover_YYYYMMDD.png`

**文案要求：**
- 标题：≤20字，吸引眼球，带 emoji
- 正文：口语化，真实感，800-1500字
- 标签：10-15个，覆盖核心词 + 长尾词

### 3. 发布

```bash
python3 scripts/xhs_publish.py \
  --title "标题" \
  --content "正文" \
  --tags "标签1,标签2" \
  --images "图片路径.png"
```

### 4. 返回结果

成功后返回：
- note_id
- 帖子链接（https://www.xiaohongshu.com/discovery/item/{note_id}）

## 注意事项

- Cookie 中 `access-token` 有效期较短（约1个月），需定期刷新
- `web_session` 有效期约1年
- type 字段必须是字符串 `"normal"` 而非整数 `1`
- 发帖必须带至少一张图片（纯文字帖会被拒绝）
