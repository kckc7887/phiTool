# phiTool - Phigros 数据管理工具
# Copyright (C) 2026 Chnynnya
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import sys
from UnityPy import Environment
import zipfile
from io import BytesIO
from log import init_console_logger
import logging

DEBUG = False

# GameInformation 的字段布局随游戏版本变化，类型树定义必须与 APK 匹配：
# typetree.json 对应 3.19.x，typetree.4.0.0.json 对应 4.0.0 及以后。
# 按顺序尝试，取第一个能完整读出对象的定义。
TYPETREE_FILES = ("typetree.json", "typetree.4.0.0.json")


def load_typetrees(files=TYPETREE_FILES):
    typetrees = []
    for name in files:
        if not os.path.isfile(name):
            continue
        with open(name, encoding="utf8") as f:
            typetrees.append((name, json.load(f)))
    if not typetrees:
        raise FileNotFoundError("缺少类型树定义文件：%s" % "、".join(files))
    return typetrees


def read_objects(env, typetree):
    """按给定类型树读取元数据对象，布局不匹配时抛异常。"""
    GameInformation = None
    Collections = None
    Tips = None
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        script_name = data.m_Script.get_obj().read().name
        if script_name == "GameInformation":
            GameInformation = obj.read_typetree(typetree["GameInformation"])
        elif script_name == "GetCollectionControl":
            Collections = obj.read_typetree(typetree["GetCollectionControl"], True)
        elif script_name == "TipsProvider":
            Tips = obj.read_typetree(typetree["TipsProvider"], True)
    if GameInformation is None:
        raise ValueError("APK 中没有 GameInformation 对象")
    return GameInformation, Collections, Tips


def run(path, logger, output_dir="info"):
    os.makedirs(output_dir, exist_ok=True)
    env = Environment()
    with zipfile.ZipFile(path) as apk:
        with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
            env.load_file(BytesIO(f.read()), name="assets/bin/Data/globalgamemanagers.assets")
        with apk.open("assets/bin/Data/level0") as f:
            env.load_file(BytesIO(f.read()))

    failures = []
    for name, typetree in load_typetrees():
        try:
            GameInformation, Collections, Tips = read_objects(env, typetree)
        except Exception as error:
            failures.append("%s：%s" % (name, error))
            continue
        logger.info("使用类型树 %s" % name)
        break
    else:
        raise RuntimeError("没有匹配该 APK 的类型树定义：\n%s" % "\n".join(failures))

    difficulty = []
    table = []
    for key, songs in GameInformation["song"].items():
        if key == "otherSongs":
            continue
        for song in songs:
            if len(song["difficulty"]) == 5:
                song["difficulty"].pop()
            if song["difficulty"][-1] == 0.0:
                song["difficulty"].pop()
                song["charter"].pop()
            for i in range(len(song["difficulty"])):
                song["difficulty"][i] = str(round(song["difficulty"][i], 1))
            song["songsId"] = song["songsId"][:-2]
            difficulty.append([song["songsId"]]+song["difficulty"])
            table.append((song["songsId"], song["songsName"], song["composer"], song["illustrator"], *song["charter"]))

    logger.info(difficulty)
    logger.info(table)

    with open(os.path.join(output_dir, "difficulty.tsv"), "w", encoding="utf8") as f:
        for item in difficulty:
            f.write("\t".join(map(str, item)))
            f.write("\n")

    with open(os.path.join(output_dir, "info.tsv"), "w", encoding="utf8") as f:
        for item in table:
            f.write("\t".join(item))
            f.write("\n")

    single = []
    illustration = []
    for key in GameInformation["keyStore"]:
        if key["kindOfKey"] == 0:
            single.append(key["keyName"])
        elif key["kindOfKey"] == 2 and key["keyName"] != "Introduction" and key["keyName"] not in single:
            illustration.append(key["keyName"])

    with open(os.path.join(output_dir, "single.txt"), "w", encoding="utf8") as f:
        for item in single:
            f.write("%s\n" % item)

    with open(os.path.join(output_dir, "illustration.txt"), "w", encoding="utf8") as f:
        for item in illustration:
            f.write("%s\n" % item)
    logger.info(single)
    logger.info(illustration)

    D = {}
    for item in Collections.collectionItems:
        if item.key in D:
            D[item.key][1] = item.subIndex
        else:
            D[item.key] = [item.multiLanguageTitle.chinese, item.subIndex]

    with open(os.path.join(output_dir, "collection.tsv"), "w", encoding="utf8") as f:
        for key, value in D.items():
            f.write("%s\t%s\t%s\n" % (key, value[0], value[1]))

    with open(os.path.join(output_dir, "avatar.txt"), "w", encoding="utf8") as avatar:
        with open(os.path.join(output_dir, "tmp.tsv"), "w", encoding="utf8") as tmp:
            for item in Collections.avatars:
                avatar.write(item.name)
                avatar.write("\n")
                tmp.write("%s\t%s\n" % (item.name, item.addressableKey[7:]))

    with open(os.path.join(output_dir, "tips.txt"), "w", encoding="utf8") as f:
        for tip in Tips.tips[0].tips:
            f.write(tip)
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) == 1 and os.path.isdir("/data/"):
        import subprocess
        r = subprocess.run("pm path com.PigeonGames.Phigros",stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,shell=True)
        file_path = r.stdout[8:-1].decode()
    else:
        file_path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(file_path, init_console_logger())
