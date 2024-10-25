<div align="center">
<img width="256" src="https://i0.hdslb.com/bfs/article/f8680a29a3a702e026e288f879284562224941fa.jpg@1320w_740h.avif" alt="Drytron Logo">

# JX3-DrytronII

_基于 Nonebot 2 的多功能群聊机器人_

![Nonebot2](https://img.shields.io/badge/Nonebot2-Release_v2.3.3-brightgreen)
![GitHub](https://img.shields.io/github/license/KolinLoa/jx3-DrytronII)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![JX3API](https://img.shields.io/badge/JX3API-2024.9.25-purple)

_名字来源：Yu-Gi-Oh! Deck Drytron_

**小废废在线求饶**

</div>


## 简介

DrytronII是一个用于查询剑三基础信息的机器人，~~以后或许也不会有其他功能（bushi）~~，基于 [Nonebot 2](https://v2.nonebot.dev) 构建，数据来源目前主要来自[JX3API](https://www.jx3api.com)主要给大家带来方便和快乐。

## 部署方法

推荐是直接使用git clone的方式  
```
git clone https://github.com/KolinLoa/jx3-DrytronII.git 
```
克隆完成后，推荐使用pdm快速安装依赖
```
pip install pdm
pdm install
```
~~克隆完成后，安装所需依赖，推荐使用conda建立虚拟环境~~
 ```
pip install -r requirements.txt
pip install nonebot2[fastapi]
```
~~把env.dev内的配置文件进行修改或者不修改，粘贴进env.prod文件内，准备工作方可完成~~  
随后执行
```
nb run
```
即可启动机器人，需要连接QQ使用请参考[NapCatQQ](https://napneko.github.io/zh-CN/)。

## To Do

**完善全部API功能**  
~~**Websocket推送功能**~~  
**完善Websocket推送功能**（现有的websocket功能借助了小白老师23年写的ws插件，很多内容还没进行修正，但是可以满足使用）  
开团功能  
宏  
奇遇以及宠物查询  
  
    
**时间不是很充足，可能要延迟很久**

## 友情链接

[CloudStudio](https://ide.cloud.tencent.com) — 腾讯云免费在线IDE  
[ChatGPT](https://chatgpt.com) — 好用的AI助手  
[JX3API](https://jx3api.com) — 剑三API提供数据来源
 