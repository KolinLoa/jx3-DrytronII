from nonebot import get_plugin_config, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from .config import Config
import json
import os


__plugin_meta__ = PluginMetadata(
    name="bind",
    description="服务器绑定",
    usage="输入绑定+服务器名",
    config=Config,
)

config = get_plugin_config(Config)

# 定义存储绑定信息的文件路径
BINDINGS_FILE = "bindings.json"

# 初始化绑定的服务器列表
server_list = {
    "幽月轮",
    "绝代天骄",
    "梦江南",
    "唯我独尊",
    "龙争虎斗",
    "长安城",
    "乾坤一掷",
    "斗转星移",
    "剑胆琴心",
    "蝶恋花",
    "山海相逢",
    "万象长安",
    "有人赴约",
    "眉间雪",
    "破阵子",
    "天鹅坪",
    "飞龙在天",
    "青梅煮酒",

}


bind = on_command("bind", aliases={"绑定"}, priority=5, block=True, permission=GROUP_ADMIN | GROUP_OWNER)

# 创建 绑定 命令，并设置仅允许群管理员和群主权限
@bind.handle()
async def handle_function(args: Message = CommandArg()):
    server_name = args.extract_plain_text()

    if server_name in server_list:
        # 获取当前群号
        group_id = str(event.group_id)

        # 读取现有绑定数据
        if os.path.exists(BINDINGS_FILE):
            with open(BINDINGS_FILE, "r", encoding="utf-8") as f:
                bindings = json.load(f)
        else:
            bindings = {}

        # 更新绑定信息
        bindings[group_id] = server_name

         # 将更新后的数据写入 JSON 文件
        with open(BINDINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(bindings, f, ensure_ascii=False, indent=4)

        await bind.finish("绑定成功")
    else:
        await bind.finish(f"请TM的检查一下你输入的服务器名字，别TM整天想着'{server_name}'这类的名字")

@bind.permission_updater
async def _(bot, event):
    await bot.send(event, "没权限别TM瞎搞，把你家管理员叫来！")
    return False


    
