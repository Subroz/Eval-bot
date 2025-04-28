# (c) @AbirHasan2005

import os
import io
import sys
import time
import asyncio
import aiofiles
import traceback
from configs import Config
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

ChatId = -1001228748022


Bot.send_message(ChatId, text="kek",reply_markup=ReplyKeyboardRemove(selective=True))

Bot = Client(
    name="Meme-Bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)


async def aexec(code, client, message):
    exec(
        'async def __aexec(client, message): ' +
        ''.join(f'\n {l_}' for l_ in code.split('\n'))
    )
    return await locals()['__aexec'](client, message)


@Bot.on_message(filters.command(["exec", "term"]) & filters.user(Config.USERS))
async def exec_handler(bot: Client, message: Message):
    DELAY_BETWEEN_EDITS = 0.3
    PROCESS_RUN_TIME = 100
    cmd = message.text.split(" ", 1)[-1]
    reply_to_id = message.message_id
    start_time = time.time() + PROCESS_RUN_TIME
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "No Error"
    o = stdout.decode()
    if not o:
        o = "No Output"
    else:
        _o = o.split("\n")
        o = "`\n".join(_o)
    OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**stderr:** \n`{e}`\n**Output:**\n{o}"
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=OUTPUT,
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )
    except MessageTooLong:
        file_path = f"./downloads/{str(time.time())}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        async with aiofiles.open(f"{file_path}output.txt", "w") as paste:
            await paste.write(OUTPUT)
        await bot.send_document(
            chat_id=message.chat.id,
            document=f"{file_path}output.txt",
            caption=f"EXEC Results for {message.from_user.mention}",
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )


@Bot.on_message(filters.command("eval") & filters.user(Config.USERS))
async def eval_handler(bot: Client, message: Message):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", 1)[-1]
    reply_to_ = message.message_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, bot, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=final_output,
            disable_notification=True
        )
    except MessageTooLong:
        file_path = f"./downloads/{str(time.time())}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        async with aiofiles.open(f"{file_path}output.txt", "w") as paste:
            await paste.write(final_output)
        await bot.send_document(
            chat_id=message.chat.id,
            document=f"{file_path}output.txt",
            caption=f"EXEC Results for {message.from_user.mention}",
            disable_notification=True
        )
    await status_message.delete()

Bot.run()
