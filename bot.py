import discord
import sys, os
import discord.utils
import asyncio
import sqlite3
import random
from config import settings
from Cybernator import Paginator as pag
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType


intents = discord.Intents.all()

bot = commands.Bot(command_prefix=settings['pref'], intents=intents)
bot.remove_command('help')
connect = sqlite3.connect('data.db')
cur = connect.cursor()



@bot.event
async def on_ready():
	cur.execute("""CREATE TABLE IF NOT EXISTS users (
		name TEXT,
		id INT,
		cash BIGINT,
		rep INT,
		lvl INT,
		xp INT,
		mupd INT
	)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS shop (
		id_role INT,
		cost BIGINT
	)""")

	for guild in bot.guilds:
		for member in guild.members:
			if cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
				cur.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 150, 1, 1, 100, 1)")
			else: 
				pass
	connect.commit()
	print("ID Бота - хз | Имя Бота " + settings['Name'] + ' | (connected)')

@bot.command(aliases=['rep'])
@commands.cooldown(1, 14400, commands.BucketType.user)
async def giverep(ctx, member: discord.Member = None):
	if member == None:
		giverep.reset_cooldown(ctx)
		await ctx.send(f'_**{ctx.author.name}**_, укажите человека для того, чтобы дать ему rep (репутацию)!')
	else:
		if member.id == ctx.author.id:
			giverep.reset_cooldown(ctx)
			await ctx.send(f'_**{ctx.author.name}**_, нельзя выдать самому себе репутацию!')
		else:
			igb = int(1)
			cur.execute(f"UPDATE users SET rep = rep + {igb} WHERE id = {member.id}")
			connect.commit()
			await ctx.send(f"_**{ctx.author.name}**_, Вы выдали **{member}** 1 репутацию.")

@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if (message.content.startswith(',')):
		pass
	elif (message.content.startswith('.')):
		pass
	elif (message.content.startswith('!')):
		pass
	elif (message.content.startswith('+')):
		pass
	else:
		if cur.execute("SELECT mupd FROM users WHERE id = {}".format(message.author.id)).fetchone()[0] == 3:
			igb = random.randint(30, 50)

			cur.execute(f"UPDATE users SET cash = cash + {igb} WHERE id = {message.author.id}")
			connect.commit()
		elif cur.execute("SELECT mupd FROM users WHERE id = {}".format(message.author.id)).fetchone()[0] == 2:
			igb = random.randint(15, 25)

			cur.execute(f"UPDATE users SET cash = cash + {igb} WHERE id = {message.author.id}")
			connect.commit()
		elif cur.execute("SELECT mupd FROM users WHERE id = {}".format(message.author.id)).fetchone()[0] == 1:
			igb = random.randint(3, 10)

			cur.execute(f"UPDATE users SET cash = cash + {igb} WHERE id = {message.author.id}")
			connect.commit()
		else:
			pass

@bot.event
async def on_member_join(member):
	if cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cur.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 150, 1, 1, 0)")
		connect.commit()
	else: 
		pass
@bot.command(aliases=['cash', 'mymoney', 'balance'])
async def __money(ctx, member: discord.Member = None):
	if member == None:
		await ctx.send(embed=discord.Embed(title= f'{ctx.author.name}', description=f"""Баланс -  {cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} койнов. \nРепутация: {cur.execute("SELECT rep FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}\nLVL: {cur.execute("SELECT lvl FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} XP: {cur.execute("SELECT xp FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}""", set_footer='LVL система не работает'))
	else:
		await ctx.send(embed=discord.Embed(title= f'{member.name}', description=f"""Баланс -  {cur.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} койнов. \nРепутация: {cur.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0]} \nLVL: {cur.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]} XP: {cur.execute("SELECT xp FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""", set_footer='LVL система не работает'))	


@bot.command(aliases=['givem', 'addmoney'])
@commands.has_any_role(842801561553207296)
async def award(ctx, member: discord.Member = None, amount: int = None):
	if member == None:
		await ctx.send(f'_**{ctx.author.name}**_, укажите пользователя, которому Вы хотите прибавить денег.')
	else:
		if amount == None:
			await ctx.send(f'_**{ctx.author.name}**_, укажите сумму, которому Вы хотите прибавить пользователю.')
		elif amount < 1:
			await ctx.send(f'_**{ctx.author.name}**_, укажите сумму больше 1 койна.')
		else:
			cur.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			connect.commit()
			await ctx.message.add_reaction('🎉')

@bot.command(aliases=['remmoney', 'removemoney'])
@commands.has_any_role(842801561553207296)
async def take(ctx, member: discord.Member = None, amount = None):
	if member == None:
		await ctx.send(f'_**{ctx.author.name}**_, укажите пользователя, которому Вы хотите прибавить денег.')
	else:
		if amount == None:
			await ctx.send(f'_**{ctx.author.name}**_, укажите сумму, которому Вы хотите прибавить пользователю.')
		elif amount == 'all':
			cur.execute("UPDATE users SET cash =  {} WHERE id = {}".format(0, member.id))
			connect.commit()
			await ctx.message.add_reaction('🎉')
		elif int(amount) < 1:
			await ctx.send(f'_**{ctx.author.name}**_, укажите сумму больше 1 койна.')
		else:
			cur.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
			connect.commit()
			await ctx.message.add_reaction('🎉')

@bot.command(aliases=['addtoshop', 'atshop'])
@commands.has_any_role(842801561553207296)
async def __atshop1(ctx, role: discord.Role = None, cost: int = None):
	if role == None:
		await ctx.send(f'_**{ctx.author.name}**_, укажите роль.')
	else:
		if cost == None:
			await ctx.send(f'_**{ctx.author.name}**_, укажите сумму для роли.')
		elif cost < 0:
			await ctx.send(f"_**{ctx.author.name}**_, укажите не отрицательную или не равную 0 сумму для роли.")
		else:
			cur.execute("INSERT INTO shop VALUES ({}, {})".format(role.id, cost))
			connect.commit()

			await ctx.message.add_reaction('🎉')


@bot.command(aliases=['delfromshop', 'dfshop'])
@commands.has_any_role(842801561553207296)
async def __dfshop1(ctx, role: discord.Role = None):
	if role == None:
		await ctx.send(f'_**{ctx.author.name}**_, укажите роль.')
	else:
		cur.execute("DELETE FROM shop WHERE id_role".format(role.id))
		connect.commit()

		await ctx.message.add_reaction('🎉')

@bot.command(aliases=['shop', 'buyer'])
async def __shop(ctx):
	embed = discord.Embed(title = 'Магазин ролей')

	for row in cur.execute("SELECT id_role, cost FROM shop"):
		if ctx.guild.get_role(row[0]) != None:
			embed.add_field(
				name = f"Цена - **{row[1]}** койнов",
				value = f"Роль - {ctx.guild.get_role(row[0]).mention}",
				inline = False
			)
		else: 
			pass

	await ctx.send(embed=embed)


@bot.command(aliases=['buy', 'getrole'])
async def __buyshop(ctx, role: discord.Role = None):
	if role == None:
		await ctx.send(f'_**{ctx.author.name}**_, укажите роль.')
	else: 
		if role in ctx.author.roles:
			await ctx.send(f'**{ctx.author.name}**, у вас уже есть эта роль!')
		elif cur.execute("SELECT cost FROM shop WHERE id_role = {}".format(role.id)).fetchone()[0] > cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f"**{ctx.author.name}**, у вас недостаточно денег!")
		else:
			await ctx.author.add_roles(role)
			cur.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cur.execute("SELECT cost FROM shop WHERE id_role = {}".format(role.id)).fetchone()[0], ctx.author.id))

			await ctx.message.add_reaction('🎉')

@bot.command(aliases=['mupdate', 'moneyupdate'])
async def __mupdate(ctx, member: discord.Member = None):
	if member == None:
		if cur.execute("SELECT mupd FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] == 3:
			await ctx.send('Вы уже максимально обновили свой доход от сообщений. (от 30 до 50 койнов)')
		elif cur.execute("SELECT mupd FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] == 2:
			if cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] < 100000:
				await ctx.send('У вас недостаточно денег для покупки улучшения 3 тира. ()')
			elif if cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] > 100000:
				await ctx.send('Вы купили улучшение 3 тира.')
				cur.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(int(100000), ctx.author.id))
				cur.execute("UPDATE users SET mupd = {0} WHERE id = {1}".format(int(3), ctx.author.id))
				connect.commit()
			else: 
				await ctx.send('[1] Вы стали жертвой никакого случая!')
		elif cur.execute("SELECT mupd FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] == 1:
			if cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] < 20000:
				await ctx.send('У вас недостаточно денег для покупки улучшения 3 тира. ()')
			elif if cur.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] > 20000:
				await ctx.send('Вы купили улучшение 3 тира.')
				cur.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(int(20000), ctx.author.id))
				cur.execute("UPDATE users SET mupd = {0} WHERE id = {1}".format(int(2), ctx.author.id))
				connect.commit()
			else: 
				pass
		elif cur.execute("SELECT mupd FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] == 0:
			await ctx.send('Вы забанены в боте!')
		else:
			await ctx.send('[2] Вы стали жертвой никакого случая!')
	else:
		await ctx.send('Вы не можете *приобретать улучшения* другому пользователю!')

@bot.command(aliases=['banaccesstobot', 'bantob'])
async def __bantob(ctx, member: discord.Member = None):
	if member == None:
		await ctx.send('Укажите пользователя!')
	else:
		if member.id == ctx.author.id:
			await ctx.send('Вы не можете указать себя!')
		else:
			cur.execute("UPDATE users SET mupd = {0} WHERE id = {1}".format(int(0), member.id))
			await ctx.message.add_reaction('🎉')

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send(embed = discord.Embed(description = f':x: Ошибка, {ctx.author.name}, аргументы в команде не верные!', colour = discord.Color.red()))
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send(embed = discord.Embed(description = f'Упс!.. {ctx.author.name}, участник не найден! :x:', colour = discord.Color.red()))
	elif isinstance(error, commands.MissingPermissions):
		await ctx.send(embed = discord.Embed(description = f':x: Ошибка, {ctx.author.name}, недостаточно прав!', colour = discord.Color.red()))
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(embed = discord.Embed(description = f':x: Ошибка, {ctx.author.name}, команда не найдена!', colour = discord.Color.red()))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed = discord.Embed(description = f':x: Ошибка, {ctx.author.name}, не хватает аргументов!', colour = discord.Color.red()))
	elif isinstance(error, commands.CheckFailure):
		await ctx.send(embed = discord.Embed(description = f':x: Ошибка, {ctx.author.name}, вы пишите из канала, где не включена функция NSFW!', colour = discord.Color.red()))
	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.send(embed = discord.Embed(description = f':x: Погодите! {ctx.author.name}, команда в кулдауне. Осталось {error.retry_after:.2f} секунд'))
	else:
		raise error

@bot.command(aliases = ['Help', 'help', 'HELP', 'hELP'])
async def __help (ctx):
	prefix = ','
	course = '50 рублей = 100к койнов'
	valute = 'койн'

	embed1 = discord.Embed(title='Страница 1 | Help', description = 'Страница 1 | Эта страница \nСтраница 2 | Баланс \nСтраница 3 | Магазин \nСтраница 4 | Репутация \nСтраница 5 | Синтаксис команд', colour = discord.Color.magenta())
	embed1.set_thumbnail(url = "https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
	embed1.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	embed1.set_footer(text="Бот в бета тесте.")

	embed2 = discord.Embed( title = 'Страница 2 | Баланс', description = f'Получать **койны** можно по курсу *{course}*, или же писать в чате.', colour = discord.Color.magenta() )
	embed2.set_thumbnail(url = "https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
	embed2.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	embed2.add_field( name = 'Баланс', value = f'`{prefix}cash` `{prefix}balance` `{prefix}mupdate`', inline=False)

	embed3 = discord.Embed( title = 'Страница 3 | Магазин', description = f'Сначала выберите роль которую вы хотите купить, убедитесь что у вас её нет и что вам хватает на неё валюты.', colour = discord.Color.magenta() )
	embed3.set_thumbnail(url = "https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
	embed3.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	embed3.add_field( name = 'Магазин', value = f' `{prefix}shop` `{prefix}buy`', inline=False)

	embed4 = discord.Embed( title = 'Страница 4 | Репутация', description = f'За счёт репутации строится таблица пользователей.', colour = discord.Color.magenta() )
	embed4.set_thumbnail(url = "https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
	embed4.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	embed4.add_field( name = 'Репутация', value = f' `{prefix}rep` `{prefix}giverep`', inline=False)

	embed5 = discord.Embed( title = 'Страница 5 | Синтаксис', description = f'Правильное написание команд.', colour = discord.Color.magenta() )
	embed5.set_thumbnail(url = "https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
	embed5.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	embed5.add_field( name = f'Синтаксис', value = f' `{prefix}cash <можно указать человека>` `{prefix}shop` `{prefix}buy <упоминание роли>` `{prefix}rep <упоминание человека>`', inline=False)

	embeds = [embed1, embed2, embed3, embed4, embed5]

	msg = await ctx.send(embed=embed1)

	page = pag(bot, msg, only=ctx.author, use_more=False, embeds=embeds)
	await page.start()
bot.run(settings['Token'])
