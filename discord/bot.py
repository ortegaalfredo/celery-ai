#
# Simple discord BOT that receives prompts and return the answer from LLaMA 13B
#

import discord
from discord.ext import commands
from typing import Tuple
import os,re
import sys
import torch
import time
import json
from pathlib import Path
from fairscale.nn.model_parallel.initialize import initialize_model_parallel
from llama import ModelArgs, Transformer, Tokenizer, LLaMA



def setup_model_parallel() -> Tuple[int, int]:
    local_rank = int(os.environ.get("LOCAL_RANK", -1))
    world_size = int(os.environ.get("WORLD_SIZE", -1))

    torch.distributed.init_process_group("nccl")
    initialize_model_parallel(world_size)
    torch.cuda.set_device(local_rank)

    # seed must be the same in all processes
    torch.manual_seed(1)
    return local_rank, world_size


def load(
    ckpt_dir: str,
    tokenizer_path: str,
    local_rank: int,
    world_size: int,
    max_seq_len: int,
    max_batch_size: int,
) -> LLaMA:
    start_time = time.time()
    checkpoints = sorted(Path(ckpt_dir).glob("*.pth"))
    assert world_size == len(
        checkpoints
    ), f"Loading a checkpoint for MP={len(checkpoints)} but world size is {world_size}"
    ckpt_path = checkpoints[local_rank]
    print("Loading")
    checkpoint = torch.load(ckpt_path, map_location="cpu")
    with open(Path(ckpt_dir) / "params.json", "r") as f:
        params = json.loads(f.read())
    model_args: ModelArgs = ModelArgs(
        max_seq_len=max_seq_len, max_batch_size=max_batch_size, **params
    )
    tokenizer = Tokenizer(model_path=tokenizer_path)
    model_args.vocab_size = tokenizer.n_words
    torch.set_default_tensor_type(torch.cuda.HalfTensor)
    model = Transformer(model_args)
    torch.set_default_tensor_type(torch.FloatTensor)
    model.load_state_dict(checkpoint, strict=False)

    generator = LLaMA(model, tokenizer)
    print(f"Loaded in {time.time() - start_time:.2f} seconds")
    return generator

def init():
    ckpt_dir = "../llama/data/13B"
    tokenizer_path = "../llama/data/tokenizer.model"
    max_seq_len = 512
    max_batch_size = 32
    global generator
    local_rank, world_size = setup_model_parallel()
    if local_rank > 0:
        sys.stdout = open(os.devnull, "w")

    generator = load(
        ckpt_dir, tokenizer_path, local_rank, world_size, max_seq_len, max_batch_size
    )

intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", help_command=None,intents=intents)

@bot.command()
async def info(ctx):
    print('info')
    await ctx.send(ctx.guild)
    await ctx.send(ctx.author)

@bot.event
async def on_ready() -> None:
    print(f"Bot {bot.user} launched.")
    await bot.change_presence(activity=discord.Game(name="global thermonuclear war")) 


@bot.command()
async def raw(ctx,*args):
    temperature= 0.8
    top_p= 0.95
    arguments = ' '.join(args)
    prompts = [
        arguments
    ]
    print(prompts)
    results = generator.generate(
        prompts, max_gen_len=256, temperature=temperature, top_p=top_p
    )

    local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if local_rank == 0:
        return

    for result in results:
        await ctx.send(result)

@bot.command()
async def ask(ctx,*args):
    temperature= 0.8
    top_p= 0.95
    arguments = ' '.join(args)
    arguments='The answer for the question "%s" would be: ' % arguments
    prompts = [
        arguments
    ]
    print(prompts)
    results = generator.generate(
        prompts, max_gen_len=1024, temperature=temperature, top_p=top_p
    )

    local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if local_rank == 0:
        return

    for result in results:
        await ctx.send(result)


@bot.event
async def on_message(message):
    temperature= 0.9
    top_p= 0.95
    if message.author == bot.user:
        return

    botid=("<@%d>" % bot.user.id)
    if message.content.startswith(botid):
        query = message.content.lower()[len(botid):].strip()
        if (query.startswith('raw ')):
            query = query[4:]
        else:
            query ='The answer for the question "%s" would be: ' % query
        prompts = [query]
        print(prompts)
        results = generator.generate(
            prompts, max_gen_len=400, temperature=temperature, top_p=top_p
            )

        local_rank = int(os.environ.get("LOCAL_RANK", -1))
        if local_rank == 0:
            return

        for result in results:
            msg = f"{message.author.mention} %s" % result
            if len(msg)>1500:
                for i in range(0,len(msg),1500):
                    await message.channel.send(msg[i:i+1500])
            else:
                await message.channel.send(msg)


init()
bot.run('xxxxxxxxxxxxxxxxxx')
