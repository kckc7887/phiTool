# phiTool - 技术文档

## 概述

phiTool 是一个用于管理 Phigros 游戏数据的命令行工具，集成了存档管理、RKS计算、推分推荐和资源提取等功能。

## 功能列表

| 命令          | 功能       | 说明              |
| ----------- | -------- | --------------- |
| `login`     | TapTap登录 | 获取Session Token |
| `summary`   | 存档摘要    | 获取存档基本信息       |
| `save`      | 获取存档     | 获取并解密云存档        |
| `b27`       | RKS计算    | 计算Best27和Phi3   |
| `recommend` | 推分推荐     | 找到提升RKS成本最小的歌曲  |
| `extract`          | 资源提取     | 从APK提取定数表和媒体资源  |
| `taptap`           | 获取下载链接 | 获取TapTap最新APK下载链接 |
| `update-difficulty`| 更新定数表   | 删除旧数据并从APK重新提取 |

## 使用方法

### 1. 登录获取Session Token

```bash
python script-py/main.py login
```

**输出示例**:

```json
{
  "session_token": "your_session_token_here",
  "expires_in": 0
}
```

### 2. 获取存档摘要

```bash
python script-py/main.py summary <session_token>
```

### 3. 获取并解密云存档

```bash
python script-py/main.py save <session_token>
```

### 4. 获取TapTap下载链接

```bash
python script-py/main.py taptap
```

### 5. 计算Best27/RKS

```bash
python script-py/main.py b27 <session_token>
```

**输出示例**:

```json
{
  "rks": 16.13,
  "phi": [...],
  "best": [...]
}
```

### 6. 推分推荐

```bash
python script-py/main.py recommend <session_token> [--target 0.01] [--top 15]
```

### 7. 资源提取

```bash
python script-py/main.py extract [apk_path] [--metadata] [--resources]
```

### 8. 更新难度定数表

```bash
python script-py/main.py update-difficulty [apk_path]
```

**参数说明**:
- `apk_path`（可选）: APK文件路径，不指定则自动搜索 `phigros/*.apk`

**功能说明**:
1. 删除旧的 `difficulty.tsv` 文件
2. 删除旧的 `metadata` 目录
3. 从APK中重新提取元数据
4. 将新的难度定数表复制到项目根目录

**输出示例**:

```json
{
  "status": "success",
  "source": "output/metadata/difficulty.tsv",
  "destination": "../difficulty.tsv"
}
```

## 目录结构

```
phiTool/
├── script-py/
│   ├── main.py            # 命令行入口
│   ├── PhigrosLibrary.py   # 核心库（B27计算、存档解密）
│   ├── recommend.py       # 推分推荐算法
│   ├── taptap_login.py    # TapTap OAuth2登录
│   ├── taptap.py          # TapTap API
│   ├── resource.py        # Unity资源提取核心模块
│   ├── gameInformation.py # 元数据提取模块
│   ├── config.ini         # 资源提取配置文件
│   ├── typetree.json      # Unity类型树定义
│   └── log.py             # 日志模块
├── difficulty.tsv         # 难度定数表
├── output/                # 输出目录（运行时创建）
└── docs/                  # 技术文档
    └── technical.md       # 详细技术文档
```

## RKS计算公式

```
RKS = (ΣBest27 RKS + ΣPhi3 难度) / 30
```

- **Best27**: 取所有歌曲中RKS最高的27首
- **Phi3**: 取所有满分歌曲中难度定数最高的3首

## 依赖安装

```bash
pip install -r requirements.txt
```

**依赖列表**:
- `requests` - HTTP请求
- `aiohttp` - 异步HTTP请求
- `pycryptodome` - AES加密/解密
- `unitypy` - Unity资源提取
- `qrcode` - 二维码生成

## 许可证

MIT License