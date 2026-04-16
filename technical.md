# phiTool - 技术文档

## 概述

phiTool 是一个用于管理 Phigros 游戏数据的命令行工具，集成了存档管理、RKS计算、推分推荐和资源提取等功能。

## 功能列表

| 命令                  | 功能       | 说明                |
| ------------------- | -------- | ----------------- |
| `login`             | TapTap登录 | 获取Session Token   |
| `summary`           | 存档摘要     | 获取存档基本信息          |
| `save`              | 获取存档     | 获取并解密云存档          |
| `b27`               | RKS计算    | 计算Best27和Phi3     |
| `recommend`         | 推分推荐     | 找到提升RKS成本最小的歌曲    |
| `extract`           | 资源提取     | 从APK提取定数表和媒体资源    |
| `taptap`            | 获取下载链接   | 获取TapTap最新APK下载链接 |
| `update-difficulty` | 更新定数表    | 删除旧数据并从APK重新提取    |

## 使用方法

### 1. 登录获取Session Token

```bash
python script-py/main.py login
```

**输出示例**:

```json
{
  "session_token": "<your_session_token>",
  "expires_in": 0
}
```

**字段说明**:

| 字段              | 类型     | 说明                   |
| --------------- | ------ | -------------------- |
| `session_token` | string | TapTap会话令牌，用于后续API请求 |
| `expires_in`    | int    | 过期时间（0表示永不过期）        |

***

### 2. 获取存档摘要

```bash
python script-py/main.py summary <session_token>
```

**输出示例**:

```json
{
  "saveVersion": 6,
  "challengeModeRank": 442,
  "rankingScore": 16.12656593322754,
  "gameVersion": 144,
  "avatar": "鸠-AprilFool",
  "progress": [0, 0, 0, 31, 12, 4, 221, 113, 16, 39, 4, 2],
  "updateAt": "2026-04-12T08:58:24.635Z",
  "url": "https://rak3ffdi.tds1.tapfiles.cn/gamesaves/0Ms148GVYetbu3TDFlRhgpWt8deqtCq7/.save"
}
```

**字段说明**:

| 字段                  | 类型     | 说明                   |
| ------------------- | ------ | -------------------- |
| `saveVersion`       | int    | 存档版本号                |
| `challengeModeRank` | int    | 课题模式段位               |
| `rankingScore`      | float  | 当前RKS分数              |
| `gameVersion`       | int    | 游戏版本号（144表示v3.19.0）  |
| `avatar`            | string | 当前使用的头像ID            |
| `progress`          | array  | 进度数据数组               |
| `updateAt`          | string | 存档最后更新时间（ISO 8601格式） |
| `url`               | string | 存档文件的CDN链接           |

***

### 3. 获取并解密云存档

```bash
python script-py/main.py save <session_token>
```

**输出示例**:

```json
{
  "status": "success",
  "encrypted_path": "output/save/encrypted.save",
  "decrypted_path": "output/save/decrypted.json",
  "session_token": "<your_session_token>"
}
```

**字段说明**:

| 字段               | 类型     | 说明                    |
| ---------------- | ------ | --------------------- |
| `status`         | string | 操作状态（success/failure） |
| `encrypted_path` | string | 加密存档文件路径              |
| `decrypted_path` | string | 解密后的JSON文件路径          |
| `session_token`  | string | 使用的会话令牌               |

***

### 4. 获取TapTap下载链接

```bash
python script-py/main.py taptap
```

**输出示例**:

```json
{
  "version": "3.19.0.1",
  "file": "com.PigeonGames.Phigros-144.apk",
  "size": 2595745792,
  "url": "https://d.tapimg.net/market/download/com.PigeonGames.Phigros"
}
```

**字段说明**:

| 字段        | 类型     | 说明       |
| --------- | ------ | -------- |
| `version` | string | 游戏版本号    |
| `file`    | string | APK文件名   |
| `size`    | int    | 文件大小（字节） |
| `url`     | string | 下载链接     |

***

### 5. 计算Best27/RKS

```bash
python script-py/main.py b27 <session_token>
```

**输出示例**:

```json
{
  "rks": 16.13,
  "phi": [
    {
      "songId": "Cthugha.USAO",
      "level": 3,
      "difficulty": 16.1,
      "score": 1000000,
      "acc": 100.0,
      "fc": true,
      "rks": 16.1,
      "target_acc_for_001": null
    }
  ],
  "best": [
    {
      "songId": "祈-我ら神祖と共に歩む者なり-.光吉猛修VS穴山大輔VSKaiVS水野健治VS大国奏音",
      "level": 2,
      "difficulty": 16.4,
      "score": 989667,
      "acc": 99.92350006103516,
      "fc": false,
      "rks": 16.344287440412216,
      "target_acc_for_001": 100.0
    }
  ]
}
```

**字段说明**:

**顶层字段**:

| 字段     | 类型    | 说明                    |
| ------ | ----- | --------------------- |
| `rks`  | float | 综合RKS分数（四舍五入到两位小数）    |
| `phi`  | array | Phi3列表（满分歌曲中难度最高的3首）  |
| `best` | array | Best27列表（RKS贡献最高的27首） |

**歌曲对象字段**:

| 字段                   | 类型         | 说明                           |
| -------------------- | ---------- | ---------------------------- |
| `songId`             | string     | 歌曲ID（格式：歌曲名.作者）              |
| `level`              | int        | 难度等级（0=EZ, 1=HD, 2=IN, 3=AT） |
| `difficulty`         | float      | 难度定数                         |
| `score`              | int        | 分数（0-1000000）                |
| `acc`                | float      | 准确率（0-100）                   |
| `fc`                 | bool       | 是否Full Combo                 |
| `rks`                | float      | 该歌曲的RKS贡献值                   |
| `target_acc_for_001` | float/null | 提升0.01 RKS所需的目标准确率（满分时为null） |

***

### 6. 推分推荐

```bash
python script-py/main.py recommend <session_token> [--target 0.01] [--top 15]
```

**参数说明**:

| 参数         | 类型    | 默认值  | 说明       |
| ---------- | ----- | ---- | -------- |
| `--target` | float | 0.01 | 目标RKS提升值 |
| `--top`    | int   | 15   | 推荐歌曲数量   |

**输出示例**:

```json
{
  "current_rks": 16.1265671353457,
  "target_rks": 16.14,
  "recommendations": [
    {
      "songId": "Lyrith迷宮リリス.ユメミド",
      "level": 2,
      "difficulty": 16.1,
      "current_acc": 99.86,
      "target_acc": 100.0,
      "acc_needed": 0.14,
      "cost_score": 24.43,
      "expected_rks": 16.1,
      "is_in_best27": true,
      "current_rks": 16.0,
      "rks_gain": 0.01,
      "max_possible_gain": 0.01
    }
  ]
}
```

**字段说明**:

**顶层字段**:

| 字段                | 类型    | 说明                             |
| ----------------- | ----- | ------------------------------ |
| `current_rks`     | float | 当前RKS分数                        |
| `target_rks`      | float | 目标RKS分数（current\_rks + target） |
| `recommendations` | array | 推荐歌曲列表（按成本排序）                  |

**推荐对象字段**:

| 字段                  | 类型     | 说明               |
| ------------------- | ------ | ---------------- |
| `songId`            | string | 歌曲ID             |
| `level`             | int    | 难度等级             |
| `difficulty`        | float  | 难度定数             |
| `current_acc`       | float  | 当前准确率            |
| `target_acc`        | float  | 目标准确率（达到目标RKS所需） |
| `acc_needed`        | float  | 需要提升的准确率         |
| `cost_score`        | float  | 推分成本分数（越低越好）     |
| `expected_rks`      | float  | 达到目标准确率后的RKS贡献   |
| `is_in_best27`      | bool   | 是否已在当前Best27中    |
| `current_rks`       | float  | 当前RKS贡献          |
| `rks_gain`          | float  | 预计RKS提升值         |
| `max_possible_gain` | float  | 最大可能提升值          |

***

### 7. 资源提取

```bash
python script-py/main.py extract [apk_path] [--metadata] [--resources]
```

**参数说明**:

| 参数             | 说明                  |
| -------------- | ------------------- |
| `apk_path`（可选） | APK文件路径，不指定则自动搜索或下载 |
| `--metadata`   | 仅提取元数据（难度定数表等）      |
| `--resources`  | 仅提取媒体资源（头像、曲绘）      |

**输出示例**:

```json
{
  "status": "success",
  "apk_path": "phigros/Phigros_3.19.0.1.apk",
  "extracted": {
    "avatar": 45,
    "illustration": 120,
    "metadata": 2
  }
}
```

***

### 8. 更新难度定数表

```bash
python script-py/main.py update-difficulty [apk_path]
```

**参数说明**:

| 参数             | 说明                               |
| -------------- | -------------------------------- |
| `apk_path`（可选） | APK文件路径，不指定则自动搜索 `phigros/*.apk` |

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

***

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
└── technical.md           # 技术文档
```

## RKS计算公式

```
RKS = (ΣBest27 RKS + ΣPhi3 难度) / 30
```

- **Best27**: 取所有歌曲中RKS最高的27首
- **Phi3**: 取所有满分(1000000分)歌曲中难度定数最高的3首

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

GNU General Public License v3.0
