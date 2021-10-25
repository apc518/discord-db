# ddb

A persistant file storage solution using a discord channel.

### Installation:

```sh
cd /path/to/my/discord/bot
curl https://raw.githubusercontent.com/apc518/discord-db/master/ddb.py > ddb.py
```

### Usage

```python
import discord
from discord.ext import commands

import ddb

client = commands.Bot("!")

DDB_CHANNEL_ID = 1234567890

@client.event
async def on_ready():
    print("bot is ready")

    # you dont have to call ddb.init in on_ready
    # but you must not do so EARLIER than when on_ready is called
    await ddb.init(client, client.get_channel(DDB_CHANNEL_ID))
```