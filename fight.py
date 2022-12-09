import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
import os
import json 
import datetime
import dateutil.parser
import uuid
import asyncio
from random import randint

dist_duels = []
list_interaction = []

class duel_member:
    def __init__(self, inv) :
        self.name = inv["name"]
        self.hp = inv["hp"]
        self.armor_name = inv["armor"][0]
        self.armor_point = inv["armor"][1]
        self.weapon_name = inv["weapon"][0]
        self.weapon_point = inv["weapon"][1]
        self.heal = inv["heal"]

def date_is(date):
    dtnow = datetime.datetime.now(tz=None)
    return date <= dtnow

def timer_30s(user_id1, user_id2, uuidf):
    
    with open("timer.json", "r") as read_file:
        timer = json.load(read_file)
        
    if user_id1 in timer or user_id2 in timer or uuidf in timer:
        return False
    else:
        dt = datetime.datetime.now(tz = None) + datetime.timedelta(seconds=30) 
        timer[uuidf] = [dt.isoformat(), user_id1, user_id2]
        with open("timer.json", "w") as json_file:
            json.dump(timer, json_file, indent=4)
    return True

class fight(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot 
        self.list_interaction = []
        self.dist_duels = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('КулькоБОТ'))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.t30s.is_running():
            self.t30s.start()

    @tasks.loop(seconds=1)
    async def t30s(self):
        global list_interaction
        #import json
        with open("timer.json", "r") as read_file:
            timer = json.load(read_file)
        if timer != {} or timer != None:
            temp_list = timer
            for uuidf in temp_list:
                times = dateutil.parser.parse(timer[uuidf][0])
                times = date_is(times)
                if times == True:
                    del timer[uuidf]
                    with open("timer.json", "w") as json_file:
                        json.dump(timer, json_file, indent=4)
                    if len(list_interaction) != 0:
                        interaction: discord.Interaction = list_interaction[int(uuidf)]   
                        await interaction.edit_original_response(content="Время вышло!")
                        del list_interaction[int(uuidf)] 
                    break      

    @app_commands.command(name="дуэль", description="Вызвать человека на дуэль")
    async def duel(self, interaction: discord.Interaction, target: discord.User) -> None:
        global list_interaction
        with open("timer.json", "r") as read_file:
            timer = json.load(read_file)
        is_decline = 0
        if interaction.user.id == target.id:
            await interaction.response.send_message(content="Вы не можете вызвать на битву самого себя!", ephemeral=True)
            return 0
        if dist_duels != []:
            for x in dist_duels:
                if interaction.user.id in x:
                    await interaction.response.send_message(content="Вы уже сражаетесь!", ephemeral=True)
                    return 0
                elif target.id in x:
                    await interaction.response.send_message(content="Упомянутый пользователь уже сражается!", ephemeral=True)
                    return 0   

        emb = discord.Embed(title="Дуэль", description=f"{target.name} был вызван на дуэль.\nЧтобы принять заявку, напишите **/принять**\nЧтобы отклонить заявку, напишите **/отклонить**", colour=0x303136)
        emb.set_footer(text="У вас 30 секунд")
        generate_uuid = str(len(list_interaction))
        timer_30s(user_id1=interaction.user.id, user_id2=target.id, uuidf=generate_uuid)
        list_interaction.append(interaction)
        await interaction.response.send_message(content=f"{interaction.user.mention}, {target.mention}", embed=emb)

    @app_commands.command(name="отклонить", description="Отклонить заявку на дуэль")
    async def duel_decline(self, interaction: discord.Interaction) -> None:
        with open("timer.json", "r") as read_file:
            timer = json.load(read_file)
        is_decline = 0
        if timer != {} or timer != None:
            temp_list = timer
            for uuidf in temp_list:
                if timer[uuidf][1] == interaction.user.id or timer[uuidf][2] == interaction.user.id:
                    del timer[uuidf]
                    with open("timer.json", "w") as json_file:
                        json.dump(timer, json_file, indent=4)
                    interaction2: discord.Interaction = list_interaction[int(uuidf)]   
                    await interaction2.edit_original_response(content="Пользователь отменил дуэль", embed=None, view=None)
                    del list_interaction[int(uuidf)]   
                    is_decline = 1
                    await interaction.response.send_message(content="Вы отклонили дуэль", ephemeral=True)
                    break
                if not is_decline:
                    await interaction.response.send_message(content="Вас не вызывали не на одну дуэль, либо таймер истёк", ephemeral=True)
        else:
            await interaction.response.send_message(content="Вас не вызывали не на одну дуэль, либо таймер истёк", ephemeral=True)

    @app_commands.command(name="принять", description="Принять заявку на дуэль")
    async def duel_start(self, interaction: discord.Interaction) -> None:
        global dist_duels
        with open("timer.json", "r") as read_file:
            timer = json.load(read_file)
        is_start = 0
        if timer != {} or timer != None:
            temp_list = timer
            for uuidf in temp_list:
                if timer[uuidf][2] == interaction.user.id:
                    with open("timer.json", "w") as json_file:
                        json.dump(timer, json_file, indent=4)
                    interaction2: discord.Interaction = list_interaction[int(uuidf)]   
                    await interaction2.edit_original_response(content="Пользователь принял заявку", embed=None, view=None)
                    del list_interaction[int(uuidf)]   
                    is_start = 1

                    with open("inv.json", "r") as read_file:
                        inv = json.load(read_file)
                    uuidf = str(uuidf)
                    inv_default1 = {"name": f"<@{timer[uuidf][1]}>", "hp": 30, "armor": ["Нет", 0], "weapon": ["Кулаки", 5], "heal": 0}
                    inv_default2 = {"name": f"<@{timer[uuidf][2]}>", "hp": 30, "armor": ["Нет", 0], "weapon": ["Кулаки", 5], "heal": 0}
                    m1 = duel_member(inv[str(timer[uuidf][1])] if str(timer[uuidf][1]) in inv else inv_default1)
                    m2 = duel_member(inv[str(timer[uuidf][2])] if str(timer[uuidf][2]) in inv else inv_default2)
                    # dist have: [0] - id 1 member [1] - id 2 member [2] - turn [3] - class, have inv 1 member [4] - class, have inv 2 member [5 or -1] - interaction
                    dist_duel = [timer[uuidf][1], timer[uuidf][2], 0, m1, m2, interaction]
                    dist_duels.append(dist_duel)
                    await interaction.response.send_message(content=f"<@{timer[uuidf][1]}> <@{timer[uuidf][2]}>", embed=discord.Embed(title="Дуэль", description=f"Очередь <@{dist_duel[int(dist_duel[2])]}>\nHP {m1.name}: {m1.hp}❤/{m1.armor_point}🛡\nHP {m2.name}: {m2.hp}❤/{m2.armor_point}🛡\n/удар - ударить\n/леч - лечится\n/сдаться - уйти с поражением из битвы"), ephemeral=False)
                    del timer[uuidf]
                    break
                if not is_start:
                    await interaction.response.send_message(content="Вас не вызывали не на одну дуэль, либо таймер истёк", ephemeral=True)
        else:
            await interaction.response.send_message(content="Вас не вызывали не на одну дуэль, либо таймер истёк", ephemeral=True)

    @app_commands.command(name="удар", description="Ударить противника")
    async def duel_is_fight(self, interaction: discord.Interaction) -> None:
        global dist_duels
        dcode = 0
        dist_duel = None
        for x in dist_duels:
            if interaction.user.id in x:
                if x[x[2]] == interaction.user.id:
                    dcode = 1
                    # dist have: [0] - id 1 member [1] - id 2 member [2] - turn [3] - class, have inv 1 member [4] - class, have inv 2 member [5 or -1] - interaction
                    dist_duel = x
                else:
                    dcode = 2

        emb = None
        eph = True
        edit = False
        if dcode == 1:
            content = f"<@{dist_duel[0]}> <@{dist_duel[1]}>"
            m1 = dist_duel[3]
            m2 = dist_duel[4]  
            edit = True          
            if dist_duel[2]:
                p = abs(randint(m2.weapon_point-10, m2.weapon_point))
                m1.armor_point -= p
                if m1.armor_point <=0:
                    m1.hp += m1.armor_point
                    m1.armor_point = 0
                dist_duel[2] = 0
                if m1.hp <= 0:
                    emb = discord.Embed(title="Дуэль", description=f"<@{dist_duel[1]}> победил!")
                    eph = False
                    i = -1
                    for x in dist_duels:
                        i += 1
                        if interaction.user.id in x:
                            if x[x[2]] == interaction.user.id:
                                del dist_duels[i]
                else:
                    emb = discord.Embed(title="Дуэль", description=f"Удар!\nОчередь <@{dist_duel[int(dist_duel[2])]}>\nHP {m1.name}: {m1.hp}❤/{m1.armor_point}🛡\nHP {m2.name}: {m2.hp}❤/{m2.armor_point}🛡\n/удар - ударить\n/леч - лечится\n/сдаться - уйти с поражением из битвы")
                    eph = False
                    await interaction.response.send_message(content=f"Вы нанесли {p} урона", ephemeral=True) 
            else:
                p = abs(randint(m1.weapon_point-10, m1.weapon_point))
                m2.armor_point -= p
                if m2.armor_point <=0:
                    m2.hp += m2.armor_point
                    m2.armor_point = 0
                dist_duel[2] = 1
                if m2.hp <= 0:
                    emb = discord.Embed(title="Дуэль", description=f"<@{dist_duel[0]}> победил!")
                    eph = False
                    i = -1
                    for x in dist_duels:
                        i += 1
                        if interaction.user.id in x:
                            if x[x[2]] == interaction.user.id:
                                del dist_duels[i]
                else:
                    emb = discord.Embed(title="Дуэль", description=f"Удар!\nОчередь <@{dist_duel[int(dist_duel[2])]}>\nHP {m1.name}: {m1.hp}❤/{m1.armor_point}🛡\nHP {m2.name}: {m2.hp}❤/{m2.armor_point}🛡\n/удар - ударить\n/леч - лечится\n/сдаться - уйти с поражением из битвы")
                    eph = False
                    await interaction.response.send_message(content=f"Вы нанесли {p} урона", ephemeral=True) 

        elif dcode == 2:
            content = "Сейчас не ваша очередь!"
        else:
            content = "Дуэль не найдена"
        if edit:
            edit_interaction = dist_duel[5]
            i = -1
            for x in dist_duels:
                i += 1
                if interaction.user.id in x:
                    if x[x[2]] == interaction.user.id:
                        dist_duel[3] = m1
                        dist_duel[4] = m2
                        dist_duels[i] = dist_duel

            await edit_interaction.edit_original_response(content=content, embed=emb, view=None)
        else:
            await interaction.response.send_message(content=content, embed=emb, ephemeral=eph)

    @app_commands.command(name="леч", description="Вылечится")
    async def duel_is_heal(self, interaction: discord.Interaction) -> None:
        global dist_duels
        dcode = 0
        dist_duel = None
        for x in dist_duels:
            if interaction.user.id in x:
                if x[x[2]] == interaction.user.id:
                    dcode = 1
                    # dist have: [0] - id 1 member [1] - id 2 member [2] - turn [3] - class, have inv 1 member [4] - class, have inv 2 member [5 or -1] - interaction
                    dist_duel = x
                else:
                    dcode = 2

        emb = None
        eph = True
        edit = False
        if dcode == 1:
            content = f"<@{dist_duel[0]}> <@{dist_duel[1]}>"
            m1 = dist_duel[3]
            m2 = dist_duel[4]
            edit = True          
            if dist_duel[2]:
                if m2.heal != 0:
                    m2.hp += m2.heal
                    dist_duel[2] = 0
                    emb = discord.Embed(title="Дуэль", description=f"Использование лекарства\nОчередь <@{dist_duel[int(dist_duel[2])]}>\nHP {m1.name}: {m1.hp}❤/{m1.armor_point}🛡\nHP {m2.name}: {m2.hp}❤/{m2.armor_point}🛡\n/удар - ударить\n/леч - лечится\n/сдаться - уйти с поражением из битвы")
                    eph = False 
                    await interaction.response.send_message(content=f"Вы вылечили себе {m2.heal}хп", ephemeral=True) 
                    m2.heal = 0
                else:
                    await interaction.response.send_message(content="У вас нет лекарств!", ephemeral=True)
                    return 0
            else:
                if m1.heal != 0:
                    m1.hp += m1.heal
                    dist_duel[2] = 1
                    emb = discord.Embed(title="Дуэль", description=f"Использование лекарства\nОчередь <@{dist_duel[int(dist_duel[2])]}>\nHP {m1.name}: {m1.hp}❤/{m1.armor_point}🛡\nHP {m2.name}: {m2.hp}❤/{m2.armor_point}🛡\n/удар - ударить\n/леч - лечится\n/сдаться - уйти с поражением из битвы")
                    eph = False
                    await interaction.response.send_message(content=f"Вы вылечили себе {m1.heal}хп", ephemeral=True) 
                    m1.heal = 0
                else:
                    await interaction.response.send_message(content="У вас нет лекарств!", ephemeral=True)
                    return 0

        elif dcode == 2:
            content = "Сейчас не ваша очередь!"
        else:
            content = "Дуэль не найдена"
        if edit:
            edit_interaction = dist_duel[5]
            i = -1
            for x in dist_duels:
                i += 1
                if interaction.user.id in x:
                    if x[x[2]] == interaction.user.id:
                        dist_duel[3] = m1
                        dist_duel[4] = m2
                        dist_duels[i] = dist_duel
            await edit_interaction.edit_original_response(content=content, embed=emb, view=None)
        else:
            await interaction.response.send_message(content=content, embed=emb, ephemeral=eph)

    @app_commands.command(name="сдаться", description="Покинуть дуэль")
    async def duel_is_end(self, interaction: discord.Interaction) -> None:
        global dist_duels
        dcode = 0
        dist_duel = None
        for x in dist_duels:
            if interaction.user.id in x:
                    dcode = 1
                    # dist have: [0] - id 1 member [1] - id 2 member [2] - turn [3] - class, have inv 1 member [4] - class, have inv 2 member [5 or -1] - interaction
                    dist_duel = x


        emb = None
        eph = True
        edit = False
        if dcode == 1:  
            content = f"<@{dist_duel[0]}> <@{dist_duel[1]}>"
            m1 = dist_duel[3]
            m2 = dist_duel[4]
            edit = True          
            eph = False
            emb = discord.Embed(description=f"{interaction.user.mention} сдался\n")
            await interaction.response.send_message(content="Вы сдались", ephemeral=True)
            
        else:
            content = "Дуэль не найдена"
        if edit:
            edit_interaction = dist_duel[5]
            i = -1
            for x in dist_duels:
                i += 1
                if interaction.user.id in x:
                    if x[x[2]] == interaction.user.id:
                        del dist_duels[i]
            await edit_interaction.edit_original_response(content=content, embed=emb)
        else:
            await interaction.response.send_message(content=content, embed=emb, ephemeral=eph)


    @app_commands.command(name="персонаж", description="Просмотр информации о персонаже")
    async def info(self, interaction: discord.Interaction, target: discord.Member = None) -> None:
        member = interaction.user if target is None else target

        with open("inv.json", "r") as read_file:
            inv = json.load(read_file)
        if str(member.id) in inv:
            user_inv = inv[str(member.id)]
            emb = discord.Embed(title=user_inv["name"], description=f"Здоровье: {user_inv['hp']}❤\nБроня: {user_inv['armor'][0]}, {user_inv['armor'][1]}🛡\nОружие: {user_inv['weapon'][0]}, {user_inv['weapon'][1]}🗡\nАптечка: {user_inv['heal']}🩹", colour=0x303136)
        else:
            emb = discord.Embed(title="Нет имени", description=f"Здоровье: 30❤\nБроня: нет, 0🛡\nОружие: нет, 5🗡\nАптечка: 0🩹", colour=0x303136)
        await interaction.response.send_message(embed=emb)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="создать_персонажа", description="Создать персонажа для дуэли")
    @app_commands.describe(target = "Кому создать персонажа", name = "Имя персонажа", hp = "Здоровье персонажа", armor_name = "Название брони", armor_point = "Количество поглощаемого урона", weapon_name = "Название оружия", weapon_point = "Количество урона", heal = "Количество восстанавливаемого здоровья")
    async def create(self, interaction: discord.Interaction, target: discord.User, name: str, hp: int, armor_name: str, armor_point: int, weapon_name: str, weapon_point: int, heal: int) -> None:
        with open("inv.json", "r") as read_file:
            inv = json.load(read_file)
        inv[target.id] = {"name": name, "hp": hp, "armor": [armor_name, armor_point], "weapon": [weapon_name, weapon_point], "heal": heal}
        with open("inv.json", "w") as json_file:
            json.dump(inv, json_file, indent=4)
        user_inv = inv[target.id]
        emb = discord.Embed(title=user_inv["name"], description=f"Здоровье: {user_inv['hp']}❤\nБроня: {user_inv['armor'][0]}, {user_inv['armor'][1]}🛡\nОружие: {user_inv['weapon'][0]}, {user_inv['weapon'][1]}🗡\nАптечка: {user_inv['heal']}🩹", colour=0x303136)
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @create.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            emb = discord.Embed(title="Ошибка", description='У вас недостаточно прав на выполнение данной команды!', colour = 0x333333)
            await ctx.response.send_message(embed=emb, ephemeral = True)
		    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fight(bot))
        
