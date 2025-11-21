import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# =============================
# Flask 保活伺服器（Render 使用）
# =============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()


# =============================
# Discord Intents
# =============================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =============================
# 你的設定
# =============================
ANNOUNCE_CHANNEL_ID = 1440378309094543482  # 公告頻道
PING_ROLE_ID = 1440603989279506432        # 要 @ 的身分組


# =============================
# 公告指令
# =============================
@bot.command()
async def 公告(ctx):
    # 刪除使用者傳的 "!公告"
    try:
        await ctx.message.delete()
    except:
        pass

    ask = await ctx.send("📝 **請輸入公告內容：**")

    def check_msg(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check_msg, timeout=120)
        content = msg.content

        try:
            await msg.delete()
        except:
            pass

        ask_ping = await ctx.send("🔔 **是否要 @身分組？**（👍 = 要，👎 = 不要）")
        await ask_ping.add_reaction("👍")
        await ask_ping.add_reaction("👎")

        def check_react(reaction, user):
            return user == ctx.author and reaction.message.id == ask_ping.id

        reaction, user = await bot.wait_for("reaction_add", check=check_react, timeout=60)
        ping_text = f"<@&{PING_ROLE_ID}> " if reaction.emoji == "👍" else ""

        ask_pin = await ctx.send("📌 **是否要釘選公告？**（📌 = 要，❌ = 不要）")
        await ask_pin.add_reaction("📌")
        await ask_pin.add_reaction("❌")

        def check_react2(reaction, user):
            return user == ctx.author and reaction.message.id == ask_pin.id

        reaction2, user2 = await bot.wait_for("reaction_add", check=check_react2, timeout=60)
        want_pin = (reaction2.emoji == "📌")

        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel is None:
            await ctx.send("❌ 找不到公告頻道")
            return

        sent = await channel.send(f"{ping_text}📢 **公告：**\n{content}")

        if want_pin:
            await sent.pin()

        try:
            await ask.delete()
            await ask_ping.delete()
            await ask_pin.delete()
        except:
            pass

        await ctx.author.send("✅ 你的公告已成功發布！")

    except Exception as e:
        await ctx.send("❌ 發生錯誤或超時，請重新輸入 `!公告`")
        print(e)


# =============================
# 啟動 BOT（環境變數）
# =============================
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("❌ DISCORD_TOKEN environment variable is not set!")

# ---- 啟動 Flask 保活 + 啟動 Bot ----
keep_alive()
bot.run(TOKEN)
