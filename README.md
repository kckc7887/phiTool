# phiTool - Phigros 数据管理工具

phiTool 是一个用于管理 Phigros 游戏数据的命令行工具。

## 功能

| 命令          | 功能       | 说明              |
| ----------- | -------- | --------------- |
| `login`     | TapTap登录 | 获取Session Token |
| `player`    | 获取玩家昵称 | 获取TapTap玩家昵称     |
| `summary`   | 存档摘要    | 获取存档基本信息       |
| `save`      | 获取存档     | 获取并解密云存档        |
| `b27`       | RKS计算    | 计算Best27和Phi3   |
| `recommend` | 推分推荐     | 找到提升RKS成本最小的歌曲  |
| `extract`          | 资源提取     | 从APK提取定数表和媒体资源  |
| `taptap`           | 获取下载链接 | 获取TapTap最新APK下载链接 |
| `update-difficulty`| 更新定数表   | 删除旧数据并从APK重新提取 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 登录获取Session Token
python script-py/main.py login

# 计算RKS
python script-py/main.py b27 <session_token>

# 推分推荐
python script-py/main.py recommend <session_token>

# 资源提取
python script-py/main.py extract
```

## 技术文档

- [详细使用说明请参考技术文档](./technical.md)

## 参考项目

本项目参考了以下开源项目：

- **Phigros_Resource** - Phigros APK资源提取工具  
  [https://github.com/7aGiven/Phigros_Resource](https://github.com/7aGiven/Phigros_Resource)

- **PhigrosLibrary** - Phigros云存档解析库  
  [https://github.com/7aGiven/PhigrosLibrary](https://github.com/7aGiven/PhigrosLibrary)

## 许可证

本项目采用 **GNU General Public License v3.0** 许可证。

详细内容请参考 `LICENSE` 文件。
