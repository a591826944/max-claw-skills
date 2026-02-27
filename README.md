# max-claw-skills

个人 OpenClaw Agent Skill 仓库，欢迎取用 🤖

## Skills

### [xhs-publisher](./xhs-publisher/) — 小红书云端全自动发帖

无需浏览器，纯云端 HTTP 调用，支持图文发帖。

**功能：**
- ✅ 图文笔记发布（带封面图）
- ✅ 自定义标题、正文、话题标签
- ✅ 公开 / 私密发布
- ✅ 完整签名算法实现（x-s / x-t / x-s-common）
- ✅ 多图上传

**快速上手：**

1. 将 `xhs-publisher/xhs_publish.py` 放到你的 workspace `scripts/` 目录
2. 配置你自己的小红书 Cookie 到 `credentials/xhs_cookies.json`（详见 [README](./xhs-publisher/README.md)）
3. 运行 `python3 scripts/xhs_publish.py --check` 验证

```bash
python3 scripts/xhs_publish.py \
  --title "帖子标题" \
  --content "正文内容" \
  --tags "标签1,标签2" \
  --images "封面图.png"
```

> ⚠️ Cookie 包含个人登录信息，请勿提交到代码库。`credentials/` 已在 `.gitignore` 中。

---

## 使用方式

每个 Skill 目录包含：
- `SKILL.md` — Agent 执行指南（OpenClaw 读取此文件来执行任务）
- `README.md` — 人类可读说明
- 相关脚本文件

将 Skill 目录放到你的 workspace `skills/` 下，OpenClaw 会自动识别。

## License

MIT
