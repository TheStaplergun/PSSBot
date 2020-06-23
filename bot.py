import discord
from discord.ext import commands
from data import *
import xml.etree.ElementTree as ET
import string
import wget
import os
import dict_digger
from operator import itemgetter
description = '''TheStaplergun's Bot in Python'''
bot = commands.Bot(command_prefix='$', description=description)
nameToId=dict()
roomRefs=dict()
spriteToFileId=dict()
roomSpriteId=dict()
#~ crewNameToData=dict()
crewData=dict()
#~ sWidth=dict()
#~ sHeight=dict()
dailyData=dict()
async def refreshBot():
	print('Refreshing local API data...')
	os.remove('xmlData/itemList.xml')
	os.remove('xmlData/roomSprites.xml')
	os.remove('xmlData/roomData.xml')
	os.remove('xmlData/dailyData.xml')
	os.remove('xmlData/crewData.xml')
	itemListXml = wget.download("http://api2.pixelstarships.com/ItemService/ListItemDesigns2?languageKey=en","xmlData/itemList.xml")
	roomSpritesXml = wget.download("http://api2.pixelstarships.com/FileService/ListSprites2?languageKey=en","xmlData/Sprites.xml")
	roomDataXml = wget.download("http://api2.pixelstarships.com/RoomService/ListRoomDesigns2?languageKey=en","xmlData/roomData.xml")
	dailyDataXml = wget.download("http://api2.pixelstarships.com/SettingService/GetLatestVersion2?languageKey=en","xmlData/dailyData.xml")
	crewDataXml = wget.download("http://api2.pixelstarships.com/CharacterService/ListAllCharacterDesigns2?languageKey=en","xmlData/crewData.xml")
	del itemListXml
	del roomSpritesXml
	del roomDataXml
	del dailyDataXml
	del crewDataXml
	"""initialize data"""
	roomSName=[]
	roomId=[]
	roomAttribs=[]
	SpriteIds=[]
	roomImageFileIds=[]
	roomSpriteIds=[]
	crewIds=[]
	crewDatas=[]
	dailyDataKeys=[]
	dailyDataValues=[]
	print('Parsing XML Data')
	tree = ET.parse('xmlData/roomData.xml')
	tree2 = ET.parse('xmlData/Sprites.xml')
	tree3 = ET.parse('xmlData/itemList.xml')
	tree4 = ET.parse('xmlData/dailyData.xml')
	tree5 = ET.parse('xmlData/crewData.xml')
	root = tree.getroot()
	root2 = tree2.getroot()
	root3 = tree3.getroot()
	root4 = tree4.getroot()
	root5 = tree5.getroot()
	print('Processing XML Data')
	for CharacterDesign in root5.iter('CharacterDesign'):
		crewIds.append(CharacterDesign.attrib.get('CharacterDesignId'))
		crewDatas.append(CharacterDesign.attrib)
	for Setting in root4.iter('Setting'):
		for key in Setting.attrib:
			dailyDataKeys.append(key)
			dailyDataValues.append(Setting.attrib.get(key))
	for Sprite in root2.iter('Sprite'):
		SpriteIds.append(Sprite.attrib.get('SpriteId'))
		roomImageFileIds.append(Sprite.attrib.get('ImageFileId'))
	counter=0
	for RoomDesign in root.iter('RoomDesign'):
		if not RoomDesign.attrib.get('RoomShortName'):
			roomSName.append(RoomDesign.attrib.get('RoomName'))
		else:
			roomSName.append(RoomDesign.attrib.get('RoomShortName'))

		counter+=1
		roomId.append(RoomDesign.attrib.get('RoomDesignId'))
		roomSpriteIds.append(RoomDesign.attrib.get('ImageSpriteId'))
		roomAttribs.append(RoomDesign.attrib)
	print(counter)
	print('Zipping Dictionaries')
	global nameToId
	global roomRefs
	global spriteToFileId
	global roomSpriteId
	global crewData
	global dailyData
	nameToId=dict(zip(roomSName,roomId))
	roomRefs=dict(zip(roomId,roomAttribs))
	spriteToFileId=dict(zip(SpriteIds,roomImageFileIds))
	roomSpriteId=dict(zip(roomId,roomSpriteIds))
	crewData=dict(zip(crewIds,crewDatas))
	dailyData=dict(zip(dailyDataKeys,dailyDataValues))
	del roomSName
	del roomId
	del roomAttribs
	del SpriteIds
	del roomImageFileIds
	del roomSpriteIds
	del crewIds
	del crewDatas
	del dailyDataKeys
	del dailyDataValues
intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

async def roomEmbed(checker):
	room=roomRefs.get(checker)
	test=roomSpriteId.get(checker)
	iId=spriteToFileId.get(roomSpriteId.get(checker))
	seconds=int(room.get('ConstructionTime'))
	granularity=2
	result = []

	for name, count in intervals:
		value = seconds // count
		if value:
			seconds -= value * count
			if value == 1:
				name = name.rstrip('s')
			result.append("{} {}".format(value, name))
	conTime=', '.join(result[:granularity])

	roomRRI=room.get('RootRoomDesignId')
	urlLink="http://datxcu1rnppcg.cloudfront.net/"+str(iId)+".png"
	if 'Weapon' in room.get('CategoryType'):
		embed=discord.Embed(title=room.get('RoomName'), description=room.get('RoomDescription'), color=0xff0000)
		embed.add_field(name="Reload Time", value='%.3f seconds'% (float(room.get('ReloadTime'))/40), inline=False)
		if (roomRRI=='9') or (roomRRI=='222') or (roomRRI=='150'):
			embed.add_field(name="Capacity", value=room.get('Capacity'), inline=True)
			embed.add_field(name="Manufacture Capacity", value=room.get('ManufactureCapacity'), inline=True)
		if (roomRRI=='109') or (roomRRI=='259'):
			embed.add_field(name="Shots Before Empty", value=room.get('Capacity'), inline=False)
		if (roomRRI=='6'):
			embed.add_field(name="Mineral Capacity", value=room.get('ManufactureCapacity'), inline=False)
	if 'Support' in room.get('CategoryType'):
		embed=discord.Embed(title=room.get('RoomName'), description=room.get('RoomDescription'), color=0x00f298)
	if 'Defence' in room.get('CategoryType'):
		embed=discord.Embed(title=room.get('RoomName'), description=room.get('RoomDescription'), color=0x0073f2)
	if 'Resources' in room.get('CategoryType'):
		embed=discord.Embed(title=room.get('RoomName'), description=room.get('RoomDescription'), color=0x8a8a8a)
	embed.set_thumbnail(url=urlLink)
	if int(room.get('MaxSystemPower')) > 0:
		embed.add_field(name="System HP", value=room.get('MaxSystemPower'), inline=True)
		embed.add_field(name="Power Required", value=room.get('MaxSystemPower'), inline=True)
	if int(room.get('MaxPowerGenerated')) > 0:
		embed.add_field(name="System HP", value=room.get('MaxPowerGenerated'), inline=True)
		embed.add_field(name="Power Generated", value=room.get('MaxPowerGenerated'), inline=True)
	if int(room.get('GasCost'))>0:
		embed.add_field(name="Upgrade", value="**Cost:** "+room.get('GasCost')+" <:gas:329018588684091393> **Time:** "+str(conTime), inline=False)
	if int(room.get('MineralCost'))>0:
		embed.add_field(name="Upgrade", value="**Cost:** "+room.get('MineralCost')+" <:mineral:329018481326424064> **Time:** "+str(conTime), inline=False)
	embed.add_field(name="Ship Level Required", value=room.get('MinShipLevel'), inline=True)
	embed.set_footer(text="TheStaplergun")
	await bot.say(embed=embed)

@bot.command()
async def rri(roomAbbreviation):
	checker=roomAbbreviation.upper()+":1"
	checker2=nameToId.get(checker)
	room=roomRefs.get(checker2)
	roomRRI=room.get('RootRoomDesignId')
	await bot.say(roomAbbreviation+" Root Room Design ID is: "+roomRRI)


@bot.event
async def on_ready():
	await refreshBot()
	print('Logged in as')
	print(bot.user.name)
	print('------')
	await bot.change_presence(game=discord.Game(name='Work in Progress'))

@bot.command()
async def ping():
    """Check if alive"""
    await bot.say("pong")
#~ @bot.command(pass_context=True)
#~ async def theboss(ctx):
	#~ if ctx.message.author.id == staplergunId:
		#~ await bot.say("You're the boss")
	#~ else:
		#~ await bot.say("You ain't the boss")
@bot.command()
async def dicTest():
	await bot.say(dict_digger.dig(crewData, dailyData.get('CommonCrewId'),'Rarity'))

@bot.command(pass_context=True)
@commands.has_role("Leadership")
async def dailydropship(ctx):
	embed=discord.Embed(title="Daily Dropship", description="On Today's Dropship", color=0x0373af)
	embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
	embed.set_thumbnail(url='http://datxcu1rnppcg.cloudfront.net/917.png')
	embed.add_field(name="Crew 1", value="__Name__: "+str(dict_digger.dig(crewData, dailyData.get('CommonCrewId'),'CharacterDesignName'))+"     __Tier:__ "+str(dict_digger.dig(crewData, dailyData.get('CommonCrewId'),'Rarity'))+"     Cost: <:mineral:329018481326424064>", inline=False)
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Unique':
		concVar1="Buy this for prestige at least, especially if the crew can actually improve your ship."
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Elite':
		concVar1="Elites are a waste of crew space. Don't buy this."
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Common':
		concVar1="Common's are bad. Don't buy this."
	embed.add_field(name="Conclusion", value=concVar1, inline=False)
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Unique':
		costVar="1x"
		concVar2="Never buy Unique crew for <:bux:329018551178362883>"
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Epic':
		costVar="2x"
		concVar2="Only buy this crew if it *improves* your ship, or you need it for prestige. Check your uniques and see if it can replace one."
	if dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'Rarity') == 'Hero':
		costVar="3x"
		concVar2="Only buy this if you can afford it. These can be very pricy, but a Hero is a big deal."
	embed.add_field(name="Crew 2", value="__Name__: "+str(dict_digger.dig(crewData, dailyData.get('HeroCrewId'),'CharacterDesignName'))+"     __Tier:__ "+str(dict_digger.dig(crewData, dailyData.get('CommonCrewId'),'Rarity')) +"     Cost: <:bux:329018551178362883> ("+costVar+" bux draw cost)", inline=False)
	embed.add_field(name="Conclusion", value=concVar2, inline=False)
	#~ embed.add_field(name="Tier", value='Name: '+.attrib.get('CharacterDesignName')++'\nCost: <:mineral:329018481326424064> \nConclusion: '+str(conc1), inline=True)
	#~ embed.add_field(name="Cost", value='Name: '+.attrib.get('CharacterDesignName')++'\nCost: <:mineral:329018481326424064> \nConclusion: '+str(conc1), inline=True)
	#~ 'Tier: '+dict_digger.dig(crewData, dailyData.get('CommonCrewId'),'Rarity')
	#~ embed.add_field(name="", value="", inline=False)
	#~ embed.add_field(name="", value="", inline=False)
	#~ embed.add_field(name="", value="", inline=False)
	#~ embed.add_field(name="", value="", inline=False)
	#~ embed.add_field(name="", value="", inline=True)
	embed.set_footer(text="TheStaplergun")
	await bot.say("<@&327954921074720769>")
	await bot.say(embed=embed)
@dailydropship.error
async def dailydropship_error(error, ctx):
	if 'The check functions for command room failed.' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Unauthorized Access Attempt", description="//Invalid Credentials user.id."+person, color=0x800000)
		await bot.say(embed=embed)
@bot.command()
@commands.has_role("Nod Empire")
async def market():
	embed=discord.Embed(title="Market Values", description="These prices are determined by the lowest to highest seen for recent sales. All prices are subject to change.", color=0x800000)
	embed.add_field(name="Scrap <:fe:329018582056960003>", value="10-12 <:bux:329018551178362883>/200k-275k <:gas:329018588684091393>/700k-1.2m <:mineral:329018481326424064>", inline=False)
	embed.add_field(name="Carbon <:carbon:329018560573734914>", value="8-11 <:bux:329018551178362883>/100k-225k <:gas:329018588684091393>/700k-1.2m <:mineral:329018481326424064>", inline=False)
	embed.add_field(name="Silicon <:si:329018515392561154>", value="16-20 <:bux:329018551178362883>/275-325k <:gas:329018588684091393>/850k-1.4m <:mineral:329018481326424064>", inline=False)
	embed.add_field(name="Gold <:au:329018539065475073>", value="14-18 <:bux:329018551178362883>/250k-325k <:gas:329018588684091393>/850k-1.2m <:mineral:329018481326424064>", inline=False)
	embed.add_field(name="Titanium <:ti:329018529418313739>", value="9-12 <:bux:329018551178362883>/100k-200k <:gas:329018588684091393>/700k-1.2mil <:mineral:329018481326424064>", inline=False)
	embed.add_field(name="Dark Matter/Unknown Material", value="500-2k <:bux:329018551178362883>", inline=True)
	embed.set_footer(text="TheStaplergun")
	await bot.say(embed=embed)
@market.error
async def market_error(error, ctx):
	if 'The check functions for command room failed.' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Unauthorized Access Attempt", description="//Invalid Credentials user.id."+person, color=0x800000)
		await bot.say(embed=embed)
#~ @bot.command(pass_context=True)
#~ async def ctxtest(ctx):
	#~ await bot.say(ctx.message.author.id)
	#~ await bot.say(ctx.message.author.name)
	#~ await bot.say(ctx.message.author.avatarurl)
@bot.command()
async def qtaTest(view = 'i'):
	if view == 'i':
		embed=discord.Embed(title="Qtarian Level 9", description="From Level 8 to Level 9, you gain 11 additional grids for a total of 184 grids.", color=0xa47300)
		embed.set_image(url='http://i.imgur.com/kFNAGeE.png')
		embed.set_footer(text="TheStaplergun")
		await bot.say(embed=embed)
	if view == 'e':
		embed=discord.Embed(title="Qtarian Level 9", description="The mid section circled in red will differentiate this as a level 9 Qtarian ship", color=0xa47300)
		embed.set_image(url='http://i.imgur.com/3AQ7H6Z.png')
		embed.set_footer(text="TheStaplergun")
		await bot.say(embed=embed)

@bot.command(pass_context=True)
@commands.has_role("Nod Empire")
async def room(ctx,roomAbbreviation, roomLevel='0'):
	if roomAbbreviation.upper() == 'VENT':
		checker="Service Vent Lv1"
		roomLevel=1
		if checker in nameToId:
			await roomEmbed(nameToId.get(checker))
	if roomAbbreviation.upper() == 'BEACON':
		checker="Small Beacon Lv1"
		roomLevel=1
		if checker in nameToId:
			await roomEmbed(nameToId.get(checker))
	else:
		if roomLevel=='0':
			person=ctx.message.author.id
			embed=discord.Embed(title="//Invalid Access Attempt", description="//Credentials user.id."+person+"\n        //Verify input\n        //input.**roomLevel** is required", color=0x800000)
			await bot.say(embed=embed)
		else:
			if roomAbbreviation.upper() == 'ARMOR':
				checker="Armor Lv"+roomLevel
			if roomAbbreviation.upper() == 'LIFT':
				checker="Lift Lv"+roomLevel
			if roomAbbreviation.upper() == 'GATE':
				checker="Security Gate Lv"+roomLevel
			if roomAbbreviation.upper() == 'ROCK':
				checker="Rock:1"
			else:
				checker=roomAbbreviation.upper()+":"+str(roomLevel)
			if checker in nameToId:
				await roomEmbed(nameToId.get(checker))
			else:
				await bot.say("That isn't a valid room abbreviation or level for that room!")
@room.error
async def room_error(error, ctx):
	if 'roomAbbreviation' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Invalid Access Attempt", description="//Credentials user.id."+person+"\n        //Verify input\n        //input.**roomAbbreviation** is required", color=0x800000)
		await bot.say(embed=embed)
	if 'The check functions for command room failed.' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Unauthorized Access Attempt", description="//Invalid Credentials user.id."+person, color=0x800000)
		await bot.say(embed=embed)
@bot.command(pass_context=True)
@commands.has_role("Leadership")
async def searchuser(ctx,userName):
	userData = wget.download("http://api2.pixelstarships.com/UserService/SearchUsers?searchString="+str(userName),"xmlData/temp.xml")
	tree = ET.parse('xmlData/temp.xml')
	root = tree.getroot()
	userId=[]
	for User in root.iter('User'):
		userId.append(User.attrib.get('Id'))
	del tree
	del root
	os.remove('xmlData/temp.xml')
	embed=discord.Embed(title="//User "+userName, description="\t//Ship Data: https://pssrank.net/user/"+str(userId[0]), color=0x800000)
	await bot.say(embed=embed)
@searchuser.error
async def searchuser_error(error, ctx):
	if 'userName' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Invalid Access Attempt", description="//Credentials user.id."+person+"\n        //Verify input\n        //input.**userName** is required", color=0x800000)
		await bot.say(embed=embed)
	if 'failed.' in str(error):
		person=ctx.message.author.id
		embed=discord.Embed(title="//Unauthorized Access Attempt", description="//Invalid Credentials user.id."+person, color=0x800000)
		await bot.say(embed=embed)
#~ @bot.group()
#~ async def vote():
	#~ await bot.say("In the command")
	#~ if ctx.invoked_subcommand is None:
	#~ await bot.say('Invalid vote request.')
	#~
#~ @vote.command(name='ban')
#~ async def ban(affUser : str, length : int, message : str):
	#~ await bot.say("In the subcommand")
	#~ await bot.say("A vote to ban "+ affUser+" has been started.")
    #~
@bot.command()
async def armor(capacity : int):
    await bot.say('Total damage reduction: %.0f' %(100-((1/(1+capacity/100))*100))+"%")

bot.run(TOKEN)
