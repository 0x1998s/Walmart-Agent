@echo off
REM 🛒 沃尔玛AI Agent平台 - Windows启动脚本
REM Walmart AI Agent Platform - Windows Startup Script

echo 🛒 启动沃尔玛AI Agent平台...
echo ================================

REM 设置编码
chcp 65001 > nul

REM 检查Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 检查Node.js
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo ✅ Node.js环境检查通过

REM 创建必要目录
if not exist "data\uploads" mkdir "data\uploads"
if not exist "logs" mkdir "logs"
if not exist "configs\chromadb" mkdir "configs\chromadb"

echo ✅ 目录创建完成

REM 生成环境配置文件
if not exist ".env" (
    echo # 🛒 沃尔玛AI Agent平台环境配置 > .env
    echo # Walmart AI Agent Platform Environment Configuration >> .env
    echo. >> .env
    echo # 基础配置 >> .env
    echo APP_NAME="沃尔玛AI Agent平台" >> .env
    echo DEBUG=false >> .env
    echo ENVIRONMENT=production >> .env
    echo LOG_LEVEL=INFO >> .env
    echo. >> .env
    echo # 数据库配置 >> .env
    echo DATABASE_URL=postgresql://walmart_admin:walmart_secure_2024@localhost:5432/walmart_ai_agent >> .env
    echo REDIS_URL=redis://:walmart_redis_2024@localhost:6379/0 >> .env
    echo. >> .env
    echo # AI模型配置 ^(请填入真实的API密钥^) >> .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo CHATGLM_API_KEY=your_chatglm_api_key_here >> .env
    echo DEEPSEEK_API_KEY=your_deepseek_api_key_here >> .env
    echo. >> .env
    echo # 安全配置 >> .env
    echo SECRET_KEY=walmart-ai-agent-super-secret-key-2024 >> .env
    
    echo ✅ 生成环境配置文件 .env
)

REM 安装Python依赖
echo 📦 安装Python依赖...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)
cd ..
echo ✅ Python依赖安装完成

REM 安装Node.js依赖
echo 📦 安装Node.js依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Node.js依赖安装失败
    pause
    exit /b 1
)
cd ..
echo ✅ Node.js依赖安装完成

REM 启动后端服务
echo 🚀 启动后端API服务...
cd backend
start "Walmart-Agent-Backend" python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
cd ..

REM 等待后端服务启动
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak > nul

REM 启动前端服务
echo 🚀 启动前端开发服务器...
cd frontend
start "Walmart-Agent-Frontend" npm run dev
cd ..

REM 等待前端服务启动
echo ⏳ 等待前端服务启动...
timeout /t 15 /nobreak > nul

echo.
echo 🎉 沃尔玛AI Agent平台启动完成！
echo.
echo 📍 访问地址：
echo    前端管理界面: http://localhost:3000
echo    后端API文档: http://localhost:8080/api/v1/docs
echo    系统健康检查: http://localhost:8080/health
echo.
echo 💡 提示：
echo    - 请在浏览器中访问上述地址
echo    - 如需停止服务，请关闭对应的命令行窗口
echo    - 日志信息会显示在各自的窗口中
echo.

pause
