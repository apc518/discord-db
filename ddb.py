import os

import discord
from discord.ext import commands

if "ddb" not in os.listdir():
	os.mkdir("ddb")
if "temp" not in os.listdir("ddb"):
	os.mkdir("ddb/temp")


client = None # the bot client itself
db_ch = None # database channel
db_dict = {} # key: filename (string), value: messag id (int)

dirmsg = None

async def init(client_ : commands.Bot, channel : discord.TextChannel, verbose=False):
	""" initalizes ddb with the client object from discord.py and the database channel"""
	global client, db_ch, dirmsg
	client = client_
	db_ch = channel
	pins = await channel.pins()
	if len(pins) == 0:
		dirmsg = await channel.send(content=":")
		await dirmsg.pin()
	elif len(pins) == 1:
		dirmsg = pins[0]
	else:
		print(f"[ddb] Two or more messages are pinned in ddb channel with id {db_ch.id}. This will likely cause issues.")
		dirmsg = pins[0]
	print(dirmsg.content)
	await refresh(verbose=verbose)

async def download(filename : str):
	""" not for external use
		used to download a file from the discord channel into the local ddb/temp folder
	"""
	if filename in db_dict:
		newfile = open(f"ddb/temp/{filename}", "wb")
		msg = await db_ch.fetch_message(db_dict[filename])
		tmp_bytes = await msg.attachments[0].read()
		newfile.write(tmp_bytes)
		newfile.close()
	else:
		raise Exception("[ddb] Tried to download but couldn't find file in database.")

async def upload(filename : str):
	""" not for external use
		used to upload a file from the local ddb/temp folder into the discord channel
	"""
	global dirmsg
	if filename in os.listdir("ddb/temp"):
		up_msg = await db_ch.send(file=discord.File(f"ddb/temp/{filename}"))
		new_content = "\n".join([x for x in dirmsg.content.split("\n") if x != "" and not x.startswith(filename) and len(x.split(":")) == 2 and x.split(":")[1].isdigit()] + [f"{filename}:{up_msg.id}"])
		await dirmsg.edit(content=new_content)
		await refresh()
	else:
		raise Exception("[ddb] Tried to upload but couldn't find file locally.")

async def delete(filename : str):
	""" used to delete a file from the discord channel """
	if filename in db_dict:
		# delete the message that contains the file
		# msg = await db_ch.fetch_message(db_dict[filename])
		# await msg.delete()
		# rewrite the directory message without the file
		global dirmsg
		old_content = dirmsg.content
		lines = [x for x in old_content.split("\n") if x != ""]
		for line in lines:
			if line.startswith(filename):
				lines.remove(line)
				break
		await dirmsg.edit(content="\n".join(lines))
		await refresh()
	else:
		raise FileNotFoundError(f"[ddb] Requested file: {filename} could not be found.")
	
async def refresh(verbose=False):
	""" uses the directory message with id `dirmsg_id` to refresh 
		the internal db_dict dictionary
	"""
	global db_dict, dirmsg
	db_dict = {}
	kv_pairs = [x for x in dirmsg.content.split("\n") if x != "" and len(x.split(":")) == 2 and x.split(":")[1].isdigit()]
	for pair in kv_pairs:
		db_dict[pair.split(":")[0]] = int(pair.split(":")[1])
	
	if verbose:
		print(f"[ddb] refreshed: {db_dict=}")

async def ddb_open(filename : str, method="r"):
	""" limited substitute for python's open()"""
	if filename in db_dict:
		if filename in os.listdir("ddb/temp"):
			os.remove(f"ddb/temp/{filename}")
		await download(filename)
		return open(f"ddb/temp/{filename}", method)
	else:
		if method.startswith("w"):
			file = open(f"ddb/temp/{filename}", method)
			await upload(filename)
			return file
		else:
			raise FileNotFoundError(f"[ddb] Requested file: {filename} could not be found.")

async def contains(filename : str):
	return filename in db_dict

async def save(filename : str):
	""" save a file from the local system in the discord channel"""
	if filename in os.listdir("ddb/temp"):
		await upload(filename)
	else:
		raise FileNotFoundError(f"[ddb] Requested file: {filename} could not be found.")

async def overwrite_dirmsg(newstring):
	""" dangerous, use with caution
		unconditionally overwrites the directory message.
		this may cause some files in the database to become inaccessible
	"""
	global dirmsg
	await dirmsg.edit(content=newstring)
