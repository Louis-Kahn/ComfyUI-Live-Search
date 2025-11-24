# 📦 发布到 ComfyUI Registry 指南

本文档说明如何将 ComfyUI-Live-Search 发布到 Comfy Registry (ComfyUI-Manager 的后端)。

## 📋 前置准备

### 1. 创建 Publisher 账户

1. 访问 [Comfy Registry](https://registry.comfy.org)
2. 注册并创建一个 Publisher 账户
3. 记下你的 **Publisher ID** (在个人资料页面 `@` 符号后面)

### 2. 生成 API Key

1. 访问 [Registry Nodes 页面](https://registry.comfy.org/nodes)
2. 点击你的 Publisher
3. 创建新的 API Key
4. **重要**: 保存 API Key,丢失后需要重新创建

### 3. 填写 Publisher ID

编辑 `pyproject.toml` 文件:

```toml
[tool.comfy]
PublisherId = "your-publisher-id"  # 替换为你的实际 Publisher ID
DisplayName = "Live Search Agent"
Icon = ""  # 可选: 图标 URL
```

## 🚀 发布方式

### 方式一: 使用 Comfy CLI (手动发布)

#### 安装 comfy-cli

```bash
pip install comfy-cli
```

#### 发布节点

```bash
comfy node publish
```

系统会提示输入 API Key:

```
API Key for publisher 'your-publisher-id': ****************************************************
...Version 1.0.0 Published.
See it here: https://registry.comfy.org/your-publisher-id/comfyui-live-search
```

**注意**:
- API Key 输入时是隐藏的
- Windows 用户建议右键粘贴,避免额外的 `\x16` 字符
- 使用 Ctrl+V 可能会在末尾添加额外字符

---

### 方式二: 使用 GitHub Actions (自动发布) ⭐ 推荐

#### 步骤 1: 设置 GitHub Secret

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 在 **Repository secrets** 下点击 **New repository secret**
4. 名称填写: `REGISTRY_ACCESS_TOKEN`
5. 值填写: 你的 API Key
6. 点击 **Add secret**

#### 步骤 2: GitHub Action 已配置

本项目已包含 `.github/workflows/publish_to_registry.yml`,它会:
- ✅ 在你推送 `pyproject.toml` 更新时自动触发
- ✅ 自动发布新版本到 Registry
- ✅ 也可以手动触发 (Actions 标签页 → 选择 workflow → Run workflow)

#### 步骤 3: 测试自动发布

1. 修改 `pyproject.toml` 中的 `version`:
   ```toml
   version = "1.0.1"  # 更新版本号
   ```

2. 提交并推送:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 1.0.1"
   git push
   ```

3. 访问 GitHub 仓库的 **Actions** 标签页
4. 查看 "Publish to Comfy Registry" 工作流执行情况
5. 发布成功后,访问 https://registry.comfy.org/your-publisher-id/comfyui-live-search

## 📝 版本管理

### 语义化版本 (Semantic Versioning)

版本号格式: `MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更 (如 `1.0.0` → `2.0.0`)
- **MINOR**: 向后兼容的功能新增 (如 `1.0.0` → `1.1.0`)
- **PATCH**: 向后兼容的问题修复 (如 `1.0.0` → `1.0.1`)

### 发布新版本

1. 更新 `pyproject.toml` 中的 `version`
2. 提交并推送 (如果使用 GitHub Actions)
3. 或运行 `comfy node publish` (如果使用 CLI)

### 弃用版本

如果某个版本有问题:

1. 访问 [Registry 网站](https://registry.comfy.org)
2. 找到你的节点和版本
3. 点击 **More Actions** → **Deprecate**
4. 用户会看到弃用提示并被鼓励升级

## ✅ 发布后

一旦发布成功:

- ✅ 你的节点会出现在 **ComfyUI-Manager** 中
- ✅ 用户可以通过 Manager 搜索并安装
- ✅ 节点会经过安全扫描,通过后显示验证标记 ✓
- ✅ 支持版本锁定和语义化升级
- ✅ Workflow JSON 会记录使用的节点版本

## 🔗 相关链接

- [Comfy Registry](https://registry.comfy.org)
- [官方发布文档](https://docs.comfy.org/registry/publishing)
- [官方规范文档](https://docs.comfy.org/registry/specifications)
- [安全标准](https://docs.comfy.org/registry/standards)

## ❓ 常见问题

**Q: 我的 Publisher ID 可以更改吗?**  
A: 不可以,Publisher ID 是全局唯一且不可变的。

**Q: 发布后可以删除版本吗?**  
A: 不可以,但可以弃用 (deprecate) 版本。

**Q: 发布后多久会出现在 ComfyUI-Manager?**  
A: 通常是立即生效,最多几分钟。

**Q: 如何更新节点描述或图标?**  
A: 修改 `pyproject.toml` 并发布新版本。

