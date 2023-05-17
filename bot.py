import disnake
import sys, os, asyncio, sqlite3 as sql3, random
from config import *
from disnake import Intents
from database import *
from Cybernator import Paginator as Pages
from disnake.ext import commands, tasks
from disnake.ext.commands import cooldown, BucketType

bot = commands.Bot(command_prefix=settings['pref'], intents=Intents.all())
bot.remove_command('help')
db = Database()
cash_range = {}
xp_range = {}
max_update = updates["max_tier"]

ch_log_enable = logging["enable"]
if ch_log_enable: ch_log_ids = logging["channel_id"]


def Log(func='anyway', txt='error'):
    _syntx = f'[{func}] {txt}'
    if ch_log_enable:
        for id_ in ch_log_ids:
            chan = bot.get_channel(id_)
            chan.send(_syntx)
    print(_syntx)


def calculate_xp_to_newlvl(xpNow, lvlNew):
    base_xp, max_lvl, xp_needed = settings["base_xp"], settings["max_lvl"], 0
    if lvlNew >= max_lvl:
        return 0
    for level in range(1, lvlNew):
        xp_needed += base_xp * level * 5.0
    return round(xp_needed)


@bot.event
async def on_ready():
    print(f"ID Бота - {bot.user.id} | Имя Бота - {bot.user.name} | (connected)")

    for i in range(1, max_update):
        cash = updates['tier{}_money'.format(i)]
        cash_range[i] = cash
        exp = xp['tier{}'.format(i)]
        xp_range[i] = exp
    for guild in bot.guilds:
        for member in guild.members:
            if not db.check_user(member.id):
                db.register_user(member)


@bot.command(aliases=['rep'])
@commands.cooldown(1, 14400, commands.BucketType.user)
async def giverep(ctx, member: disnake.Member = None):
    if not member:
        giverep.reset_cooldown(ctx)
        await ctx.send(f'_**{ctx.author.name}**_, укажите человека для того, чтобы дать ему rep (репутацию)!')
    else:
        if member.id == ctx.author.id:
            giverep.reset_cooldown(ctx)
            await ctx.send(f'_**{ctx.author.name}**_, нельзя выдать самому себе репутацию!')
        else:
            db.give_reputation(member)
            await ctx.send(f"_**{ctx.author.name}**_, Вы выдали **{member}** 1 репутацию.")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith(tuple(',.!+@$%^&*')):
        pass
    else:
        update_value = db.get_update(message.author)
        if update_value in cash_range:
            to_cash = random.randint(*cash_range[update_value])
            to_xp = random.randint(*xp_range[update_value])
            db.give_cash(message.author, to_cash)
            db.give_exp(message.author, to_xp)


@bot.event
async def on_member_join(member):
    if not db.check_user(member.id):
        db.register_user(member)


@bot.event
async def on_member_remove(member):
    db.delete_user(member)


@tasks.loop(minutes=10)
async def checker():
    for row in db.get_users_all():
        calc = calculate_xp_to_newlvl(row["xp"], row["lvl"] + 1)
        if calc == 0:
            return
        if row["xp"] >= calc:
            Log("Checker", f"{row['xp']} >= {calc}")
            db.set_level(row["id"], row["lvl"] + 1)
            user = bot.get_user(row["id"])
            if user:
                try:
                    await user.send(f"Вы достигли {row['lvl'] + 1} уровня! Так держать!")
                finally:
                    Log("Checker", f"{user.display_name} поднял уровень")


@bot.command(aliases=['cash', 'balance', 'profile'])
async def __money(ctx, member: disnake.Member = None):
    if not member:
        member = ctx.author
    user = db.get_user_all(member)
    cash, rep, lvl, xp = user["cash"], user["rep"], user["lvl"], user["xp"]
    update = user["_update"]
    embed = disnake.Embed(title=f'{member.name}',
                          description=f" Баланс - {cash} {walletcase['I_m']} \nРепутация: {rep} \nLVL: {lvl} | XP: {xp} "
                                      f"\nОбновление: {update}")
    embed.set_footer(text=f'2023 © {bot.user.display_name}')
    await ctx.send(embed=embed)


@bot.command(aliases=['addmoney'])
@commands.has_any_role(*settings['admin_roles'])
async def award(ctx, member: disnake.Member = None, amount: int = None):
    if not member:
        await ctx.send(f'_**{ctx.author.name}**_, укажите пользователя, которому Вы хотите прибавить денег.')
    else:
        if not amount:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму, которому Вы хотите прибавить пользователю.')
        elif amount <= 1:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму больше 1 койна.')
        else:
            db.give_cash(member, amount)
            await ctx.message.add_reaction('🎉')


@bot.command(aliases=['removemoney'])
@commands.has_any_role(*settings['admin_roles'])
async def take(ctx, member: disnake.Member = None, amount: int = None):
    if member == None:
        await ctx.send(f'_**{ctx.author.name}**_, укажите пользователя, которому Вы хотите убавить денег.')
    else:
        if not amount:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму, которому Вы хотите убавить пользователю.')
        elif amount == 'all':
            db.set_cash(member, 0)
            await ctx.message.add_reaction('🎉')
        elif amount < 1:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму больше 1 койна.')
        else:
            db.remove_cash(member, amount)
            await ctx.message.add_reaction('🎉')


@bot.command(aliases=['addtoshop', 'atshop'])
@commands.has_any_role(*settings['admin_roles'])
async def __atshop1(ctx, role: disnake.Role = None, channel: disnake.TextChannel = None, cost: int = None):
    if role and channel:
        if not cost:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму для роли.')
        elif cost <= 0:
            await ctx.send(f"_**{ctx.author.name}**_, укажите не отрицательную или не равную 0 сумму для роли.")
        else:
            db.shop_add(role.id, channel.id, cost)
            await ctx.message.add_reaction('🎉')

    elif role and not channel:
        if not cost:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму для роли.')
        elif cost <= 0:
            await ctx.send(f"_**{ctx.author.name}**_, укажите не отрицательную или не равную 0 сумму для роли.")
        else:
            db.shop_add(role.id, amount=cost)
            await ctx.message.add_reaction('🎉')

    elif channel and not role:
        if not cost:
            await ctx.send(f'_**{ctx.author.name}**_, укажите сумму для канала.')
        elif cost <= 0:
            await ctx.send(f"_**{ctx.author.name}**_, укажите не отрицательную или не равную 0 сумму для канала.")
        else:
            db.shop_add(channel.id, amount=cost)
            await ctx.message.add_reaction('🎉')
    elif not channel and not role:
        await ctx.send(f'_**{ctx.author.name}**_, укажите канал или роль.')


@bot.command(aliases=['deletefromshop', 'dfshop'])
@commands.has_any_role(*settings['admin_roles'])
async def __dfshop1(ctx, role: disnake.Role = None, channel: disnake.TextChannel = None):
    if role:
        db.shop_remove(role=role.id)
        await ctx.message.add_reaction('🎉')
    elif channel:
        db.shop_remove(role=channel.id)
        await ctx.message.add_reaction('🎉')
    else:
        await ctx.send(f'_**{ctx.author.name}**_, укажите роль или канал для удаления.')


@bot.command(aliases=['shop'])
async def __shop(ctx: disnake.Message):
    if settings['shop_desc_enable']:
        embed = disnake.Embed(title='Магазин ролей и каналов',
                              description='Здесь можно купить роль или доступ к каналу.')
    else:
        embed = disnake.Embed(title='Магазин ролей и каналов')
    channel_ = role_ = False
    channel_id = role_id = cost = 0
    for row in db.shop_get_all():
        if ctx.guild.get_role(row["id_role"]) is not None:
            role_ = True
            role_id = row["id_role"]
            cost = row["cost"]
        if ctx.guild.get_channel(row["id_channel"]) is not None:
            channel_ = True
            channel_id = row["id_channel"]
            cost = row["cost"]
        if role_ and channel_:
            embed.add_field(
                name=f"Цена - **{cost}** {walletcase['I_m']}",
                value=f"Роль - {ctx.guild.get_role(role_id).mention}"
                      f"\nКанал - #{ctx.guild.get_channel(row['id_channel'])}",
                inline=False
            )
        elif role_ and not channel_:
            embed.add_field(
                name=f"Цена - **{cost}** {walletcase['I_m']}",
                value=f"Роль - {ctx.guild.get_role(role_id).mention}",
                inline=False
            )
        elif channel_ and not role_:
            embed.add_field(
                name=f"Цена - **{cost}** {walletcase['I_m']}",
                value=f"Канал - #{ctx.guild.get_channel(channel_id)}",
                inline=False
            )
    await ctx.send(embed=embed)


@bot.command(aliases=['buy', 'getrole'])
async def __buyshop(ctx: disnake.Member, role: disnake.Role = None, channel: disnake.TextChannel = None):
    money = db.get_money(ctx.author)
    if role:
        price = db.shop_get_price(role.id)
        if role in ctx.author.roles:
            await ctx.send(f'**{ctx.author.name}**, у вас уже есть эта роль!')
        elif price > money:
            await ctx.send(f"**{ctx.author.name}**, у вас недостаточно денег!")
        elif price <= money:
            await ctx.author.add_roles(role)
            await ctx.message.add_reaction('🎉')
            await ctx.send(
                f"🎉 Поздравляем, **{ctx.author.name}**, вы купили роль {ctx.guild.get_role(role.id).mention}!")
    elif channel:
        price = db.shop_get_price(channel.id)
        if role in ctx.author.roles:
            await ctx.send(f'**{ctx.author.name}**, вы уже в состаите в данном канале!')
        elif price > money:
            await ctx.send(f"**{ctx.author.name}**, у вас недостаточно денег!")
        elif price <= money:
            await channel.set_permissions(ctx.author, read_messages=True)
            await ctx.message.add_reaction('🎉')
            await ctx.send(
                f"🎉 Поздравляем, **{ctx.author.name}**, вы купили роль {ctx.guild.get_channel(channel.id).mention}!")
    else:
        await ctx.send(f":x: **{ctx.author.name}**, упомяните роль или канал для получения доступа")


@bot.command(aliases=['update', 'moneyupdate'])
async def __mupdate(ctx):
    member = ctx.author
    update = db.get_update(member.id)
    money = db.get_money(member)
    max_update = updates["max_tier"]
    if not member:
        if update >= max_update:  # Проверяем, достиг ли пользователь максимального количества улучшений
            await ctx.send('Вы уже максимально обновили свой доход от сообщений.')
        else:
            for i in range(update + 1, max_update + 1):  # Цикл для покупки улучшений в порядке возрастания
                cost = updates['cost_tier{}'.format(i)]  # Получаем стоимость текущего улучшения
                if money < cost:
                    await ctx.send('У вас недостаточно денег для покупки улучшения {} тира.'.format(i))
                else:
                    await ctx.send('Вы купили улучшение {} тира.'.format(i))
                    db.remove_cash(member, cost)
                    db.set_update(member, i)


@bot.command(aliases=['banWallet'])
@commands.has_any_role(*settings['admin_roles'])
async def __bantob(ctx, member: disnake.Member = None):
    if not member:
        await ctx.send(':x: Укажите пользователя!')
    else:
        if member.id == ctx.author.id:
            await ctx.send(':x: Вы не можете указать себя!')
        else:
            db.set_update(member, 0)
            await ctx.message.add_reaction('🎉')

    # @bot.event
    # async def on_command_error(ctx, error):
    """if isinstance(error, commands.BadArgument):
        await ctx.send(embed=disnake.Embed(description=f':x: Ошибка, {ctx.author.name}, аргументы в команде не верны!',
                                           colour=disnake.Color.red()))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(embed=disnake.Embed(description=f':x: Упс!.. {ctx.author.name}, участник не найден! :x:',
                                           colour=disnake.Color.red()))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=disnake.Embed(description=f':x: Ошибка, {ctx.author.name}, недостаточно прав!',
                                           colour=disnake.Color.red()))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=disnake.Embed(description=f':x: Ошибка, {ctx.author.name}, команда не найдена!',
                                           colour=disnake.Color.red()))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=disnake.Embed(description=f':x: Ошибка, {ctx.author.name}, не хватает аргументов!',
                                           colour=disnake.Color.red()))
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(embed=disnake.Embed(
            description=f':x: Ошибка, {ctx.author.name}, вы пишите из канала, где не включена функция NSFW!',
            colour=disnake.Color.red()))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=disnake.Embed(
            description=f':x: Погодите! {ctx.author.name}, команда в кулдауне. Осталось {error.retry_after:.2f} секунд'))
    else:"""
    # raise error


@bot.command(aliases=['Help', 'help', 'HELP', 'hELP'])
async def __help(ctx: disnake.ext.commands.Context):
    prefix = settings["pref"]

    embed1 = disnake.Embed(title='Страница 1 | Help',
                           description='Страница 1 | Эта страница \nСтраница 2 | Баланс \nСтраница 3 | Магазин \nСтраница 4 | Репутация \nСтраница 5 | Синтаксис команд',
                           colour=disnake.Color.magenta())
    embed1.set_thumbnail(url="https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
    embed1.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed1.set_footer(text="Бот в бета тесте.")

    embed2 = disnake.Embed(title='Страница 2 | Баланс',
                           description=f'Получать **{walletcase["KG"]}** можно двумя способами:\n1. купить за реальные деньги \n2. Писать в чате',
                           colour=disnake.Color.magenta())
    embed2.set_thumbnail(url="https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
    embed2.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed2.add_field(name='Баланс', value=f'`{prefix}cash` `{prefix}balance` `{prefix}update`', inline=False)

    embed3 = disnake.Embed(title='Страница 3 | Магазин',
                           description=f'Сначала выберите роль (или канал) которую вы хотите купить, убедитесь что у вас её нет и вам хватает на неё валюты.',
                           colour=disnake.Color.magenta())
    embed3.set_thumbnail(url="https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
    embed3.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed3.add_field(name='Магазин', value=f' `{prefix}shop` `{prefix}buy`', inline=False)

    embed4 = disnake.Embed(title='Страница 4 | Репутация',
                           description=f'За счёт репутации строится таблица пользователей.',
                           colour=disnake.Color.magenta())
    embed4.set_thumbnail(url="https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
    embed4.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed4.add_field(name='Репутация', value=f' `{prefix}rep`', inline=False)

    embed5 = disnake.Embed(title='Страница 5 | Синтаксис', description=f'Правильное написание команд.',
                           colour=disnake.Color.magenta())
    embed5.set_thumbnail(url="https://icons.iconarchive.com/icons/alecive/flatwoken/128/Apps-Help-icon.png")
    embed5.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed5.add_field(name=f'Синтаксис',
                     value=f'`{prefix}cash <можно указать человека>` \n`{prefix}shop` \n`{prefix}buy <упоминание роли>` \n`{prefix}rep <упоминание человека>`',
                     inline=False)

    embeds = [embed1, embed2, embed3, embed4, embed5]
    msg = await ctx.send(embed=embed1)

    page = Pages(bot, msg, only=ctx.author, use_more=False, embeds=embeds)
    await page.start()


checker.start()
bot.run(settings['Token'])
