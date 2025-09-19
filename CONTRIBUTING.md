# 🤝 贡献指南

感谢您对沃尔玛AI Agent平台项目的兴趣！我们欢迎所有形式的贡献。

## 📋 贡献类型

- 🐛 **Bug修复**
- ✨ **新功能开发**
- 📚 **文档改进**
- 🧪 **测试用例**
- 🎨 **UI/UX改进**
- 🔧 **性能优化**
- 🌐 **国际化支持**

## 🚀 快速开始

### 1. Fork 项目

点击右上角的 "Fork" 按钮，将项目复制到您的GitHub账户。

### 2. 克隆到本地

```bash
git clone https://github.com/YOUR_USERNAME/Walmart-Agent.git
cd Walmart-Agent
```

### 3. 创建功能分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b bugfix/your-bugfix-name
```

### 4. 设置开发环境

#### 后端环境设置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
```

#### 前端环境设置
```bash
cd frontend
npm install
```

#### Docker环境设置
```bash
# 一键启动所有服务
docker-compose up -d
```

## 📝 开发规范

### 代码风格

#### Python (后端)
- 使用 **PEP 8** 代码风格
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **mypy** 进行类型检查

```bash
# 安装开发工具
pip install black isort mypy flake8

# 格式化代码
black backend/
isort backend/

# 类型检查
mypy backend/
```

#### TypeScript/React (前端)
- 使用 **Prettier** 进行代码格式化
- 使用 **ESLint** 进行代码检查
- 遵循 **React Hooks** 最佳实践

```bash
# 格式化代码
npm run format
npm run lint
npm run type-check
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型 (type):**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关
- `perf`: 性能优化

**示例:**
```
feat(agents): 添加新的库存预警Agent

- 实现库存水位监控
- 添加自动补货建议
- 集成邮件通知功能

Closes #123
```

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=. --cov-report=html

# 运行特定测试
pytest tests/test_agents.py::TestRetailAnalysisAgent -v
```

### 前端测试

```bash
cd frontend

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 构建测试
npm run build
```

### 集成测试

```bash
# 启动完整服务栈
docker-compose up -d

# 等待服务启动
sleep 30

# 运行集成测试
curl -f http://localhost:8000/health
curl -f http://localhost:3000

# 清理
docker-compose down
```

## 📚 文档

### API文档
- 使用 **FastAPI** 自动生成 OpenAPI 文档
- 访问 `http://localhost:8000/docs`

### 代码文档
- Python: 使用 **Google风格** 的docstring
- TypeScript: 使用 **JSDoc** 注释

**Python示例:**
```python
async def process_message(
    self, 
    message: str, 
    context: AgentContext,
    **kwargs
) -> AgentMessage:
    """处理用户消息并返回响应.
    
    Args:
        message: 用户输入的消息
        context: Agent上下文信息
        **kwargs: 额外的参数
        
    Returns:
        AgentMessage: 处理后的消息响应
        
    Raises:
        ValueError: 当消息格式不正确时
        AgentError: 当Agent处理失败时
    """
```

**TypeScript示例:**
```typescript
/**
 * 发送聊天消息到Agent
 * @param message - 用户消息内容
 * @param agentId - 目标Agent ID
 * @returns Promise<ChatResponse> 聊天响应
 */
async function sendMessage(message: string, agentId?: string): Promise<ChatResponse> {
    // ...
}
```

## 🔍 代码审查

### Pull Request 流程

1. **创建PR**: 从您的功能分支创建PR到 `main` 分支
2. **填写模板**: 使用PR模板描述您的更改
3. **自动检查**: 确保CI/CD流水线通过
4. **代码审查**: 等待维护者审查您的代码
5. **处理反馈**: 根据反馈修改代码
6. **合并**: 审查通过后合并到主分支

### PR检查清单

- [ ] 代码遵循项目风格指南
- [ ] 添加了必要的测试用例
- [ ] 所有测试都通过
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突
- [ ] 功能完整且可用
- [ ] 性能没有显著下降

### PR模板

```markdown
## 📝 变更描述
简要描述这个PR的主要变更。

## 🔗 相关Issue
Closes #(issue number)

## 🧪 测试
- [ ] 单元测试已添加/更新
- [ ] 集成测试通过
- [ ] 手动测试完成

## 📸 截图
如果有UI变更，请添加截图。

## ✅ 检查清单
- [ ] 代码遵循项目规范
- [ ] 测试覆盖率足够
- [ ] 文档已更新
- [ ] 没有破坏性变更
```

## 🐛 Bug报告

使用 [Bug报告模板](.github/ISSUE_TEMPLATE/bug_report.md) 创建Issue，包含：

- 详细的问题描述
- 复现步骤
- 期望行为
- 环境信息
- 错误日志

## ✨ 功能请求

使用 [功能请求模板](.github/ISSUE_TEMPLATE/feature_request.md) 创建Issue，包含：

- 功能描述
- 使用场景
- 实现建议
- 优先级评估

## 🏷️ 发布流程

### 版本号规范

使用 [语义化版本](https://semver.org/lang/zh-CN/)：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的API更改
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的Bug修复

### 发布步骤

1. **更新版本号**
   ```bash
   # 更新package.json和其他版本文件
   npm version patch  # 或 minor/major
   ```

2. **更新CHANGELOG.md**
   ```bash
   # 记录本次发布的主要变更
   ```

3. **创建Release标签**
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```

4. **GitHub Release**
   - 在GitHub上创建Release
   - 添加发布说明
   - 上传构建产物

## 🌟 贡献者认可

### 贡献类型
- 💻 代码贡献
- 📖 文档贡献
- 🐛 Bug报告
- 💡 功能建议
- 🎨 设计贡献
- 🌐 翻译贡献

### 认可方式
- README中的贡献者列表
- 发布说明中的感谢
- GitHub贡献者统计
- 特殊徽章和称号

## 📞 获取帮助

如果您有任何问题：

1. 查看 [项目文档](./README.md)
2. 搜索现有 [Issues](https://github.com/0x1998s/Walmart-Agent/issues)
3. 查看 [API文档](http://localhost:8000/docs)
4. 创建新的Issue
5. 联系维护者:
   - 微信: Joeng_Jimmy
   - 邮箱: jemmy_yang@yeah.net
   - GitHub: [@0x1998s](https://github.com/0x1998s)

## 🎯 开发指南

### Agent开发
```python
# 创建新的Agent
class NewAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="新Agent",
            description="Agent功能描述",
            capabilities=[AgentCapability.DATA_ANALYSIS],
            **kwargs
        )
    
    async def process_message(self, message: str, context: AgentContext, **kwargs) -> AgentMessage:
        # 实现消息处理逻辑
        pass
```

### API端点开发
```python
# 添加新的API端点
@router.post("/new-endpoint")
async def new_endpoint(
    request: NewRequest,
    current_user: User = Depends(get_current_user)
):
    # 实现API逻辑
    pass
```

### 前端组件开发
```typescript
// 创建新的React组件
const NewComponent: React.FC<Props> = ({ prop1, prop2 }) => {
    // 实现组件逻辑
    return (
        <div>
            {/* 组件内容 */}
        </div>
    );
};
```

## 🚀 最佳实践

### 性能优化
- 使用异步处理减少阻塞
- 实现合适的缓存策略
- 优化数据库查询
- 减少不必要的网络请求

### 安全考虑
- 输入验证和清理
- 适当的权限控制
- 敏感信息保护
- API速率限制

### 可维护性
- 模块化设计
- 清晰的代码注释
- 完整的测试覆盖
- 详细的错误处理

---

**感谢您对沃尔玛AI Agent平台的贡献！** 🎉

每一个贡献都让这个项目变得更好！
