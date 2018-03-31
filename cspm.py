import MySQLdb
import discord
from discord.ext import commands
import asyncio
from pokemonlist import pokemon, pokejson
from config import bot_channel, token, host, user, password, database, website, log_channel, instance_id
import datetime
import calendar
import time

bot = commands.Bot(command_prefix = '!')#set prefix to !

database = MySQLdb.connect(host,user,password,database)

cursor = database.cursor()

print('CSPM Started for ' + str(instance_id))

def find_pokemon_id(name):
    if name == 'Nidoran-F':
        return 29
    elif name == 'Nidoran-M':
        return 32
    elif name == 'Mr-Mime':
        return 122
    elif name == 'Ho-Oh':
        return 250
    elif name == 'Mime-Jr':
        return 439
    else:
        name = name.split('-')[0]
        for k in pokejson.keys():
            v = pokejson[k]
            if v == name:
                return int(k)
        return 0

def get_time(minute):
    future = datetime.datetime.utcnow() + datetime.timedelta(minutes=minute)
    return calendar.timegm(future.timetuple())

def get_team_id(raw_team):
    gym_team_id = 0
    
    if raw_team.isnumeric and ( raw_team >= '0' ) and ( raw_team <= '3' ):
        gym_team_id = int(raw_team)
    else:
        team_name = str(raw_team).capitalize()
        if ( team_name in 'Mystic' ) or ( team_name in 'Blue' ):
           gym_team_id = 1
        elif ( team_name in 'Valor' ) or ( team_name in 'Red' ):
           gym_team_id = 2
        elif ( team_name in 'Instinct')  or ( team_name in 'Yellow' ):
           gym_team_id = 3
        else:
           gym_team_id = 0
    return gym_team_id

def get_team_name(team_id):
    if ( team_id == 1 ):
        team_name = 'Mystic'
    elif ( team_id == 2 ):
        team_name = 'Valor'
    elif ( team_id == 3 ):
        team_name = 'Instinct'
    else:
        team_name = 'Unknown'
    return team_name

#raid function
@bot.command(pass_context=True)
async def raid(ctx, raw_gym_name, raw_pokemon_name, raw_raid_level, raw_time_remaining, raw_team):
    if ctx and ctx.message.channel.id == str(bot_channel):
        pokemon_name = str(raw_pokemon_name).capitalize()
        pokemon_id = find_pokemon_id(pokemon_name)
        remaining_time = get_time(int(raw_time_remaining))
        current_time = datetime.datetime.utcnow()
        gym_team_id = get_team_id(raw_team)
        
        try:
            if raw_gym_name.isnumeric():
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE id LIKE '" + str(raw_gym_name) + "';")
            else:
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE name LIKE '%" + str(raw_gym_name) + "%';")
            gym_data = cursor.fetchall()
            count = cursor.rowcount

            # Single gym_id is returned so check if a raid exists for it
            if ( count == 1 ):
                gym_id = gym_data[0][0]
                gym_name = gym_data[0][1]
                cursor.execute("SELECT id, fort_id, time_end FROM raids WHERE fort_id='" + str(gym_id) + "' AND time_end>'" + str(calendar.timegm(current_time.timetuple())) + "';")
                raid_data = cursor.fetchall()
                raid_count = cursor.rowcount
 
                if (raid_count):
                    raid_id = raid_data[0][0]
                    raid_fort_id = raid_data[0][1]
                    raid_time_end = raid_data[0][2]
            else:
                gym_names = ''
                raid_count = 0
                for gym in gym_data:
                    gym_names += str(gym[0]) + ': ' + gym[1] + ' (' + str(gym[2]) + ', ' + str(gym[3]) + ')\n'



            if ( pokemon_name == "Egg" ):
                est_end_time = remaining_time + 2700
                
                if (raid_count):
                    cursor.execute("UPDATE raids SET level='" + str(raw_raid_level) + "', time_battle='" + str(remaining_time) + "', time_end='" + str(est_end_time) + "' WHERE id='" + str(raid_id)+ "';")
                    await bot.say('Updated **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + '**' +
                                  '\nGym: **' + str(gym_id) + ': ' + str(gym_name) + ' Gym' + '**' +
                                  '\nHatches: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                                  '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(est_end_time))) + '**' +
                                  '\nTeam: **' + str(get_team_name(gym_team_id)) + '**')
                else:
                    cursor.execute("INSERT INTO raids("
                                   "id, external_id, fort_id , level, "
                                   "pokemon_id, move_1, move_2, time_spawn, "
                                   "time_battle, time_end, cp)"
                                   "VALUES "
                                   "(null, null, " + str(gym_id) + ", "
                                   + str(raw_raid_level) + ", " + str(pokemon_id) + ", null, null, "
                                   "null, " + str(remaining_time) + ", " + str(est_end_time) + ", null);")
                    await bot.say('Added new **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + '**' +
                                  '\nGym: **' + str(gym_name) + ' Gym' + '**' +
                                  '\nHatches: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                                  '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(est_end_time))) + '**' +
                                  '\nTime Left: **' + str(raw_time_remaining) + '** minutes.' +
                                  '\nTeam: **' + str(get_team_name(gym_team_id)) + '**')
                    await bot.send_message(discord.Object(id=log_channel),
                        '----------------------------------------------------' +
                        '\nReport: **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + '**' +
                        '\nGym: **' + str(gym_name) + ' Gym' + '**' +
                        '\nHatches: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                        '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(est_end_time))) + '**' +
                        '\nTeam: **' + str(get_team_name(gym_team_id)) + '**' +
                        '\nReported by: __' + str(ctx.message.author.name) + '__' +
                        '\n\nhttps://www.google.com/maps?q=loc:' + str(gym_data[0][2]) + ',' + str(gym_data[0][3]) )
                    print(str(ctx.message.author.name) + ' reported a ' + str(pokemon_name) + ' raid at ' + str(gym_name) + ' gym with ' + str(raw_time_remaining) + ' minutes left.')
            else:
                # Update Egg to a hatched Raid Boss
                if (raid_count):
                    cursor.execute("UPDATE raids SET pokemon_id='" + str(pokemon_id) + "', level='" + str(raw_raid_level) + "', time_battle='" + str(calendar.timegm(current_time.timetuple())) + "', time_end='" + str(remaining_time) + "' WHERE id='" + str(raid_id)+ "';")
                    await bot.say('Updated **Level ' + str(raw_raid_level) + ' Egg to ' + str(pokemon_name) + ' Raid' + '**' +
                                  '\nGym: **' + str(gym_id) + ': ' + str(gym_name) + ' Gym' + '**' +
                                  '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                                  '\nTeam: **' + str(get_team_name(gym_team_id)) + '**')
                    await bot.send_message(discord.Object(id=log_channel),
                        '----------------------------------------------------' +
                        '\nReport: **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + ' Raid' + '**' +
                        '\nGym: **' + str(gym_name) + ' Gym**' +
                        '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                        '\nTeam: **' + str(get_team_name(gym_team_id))+ '**' +
                        '\nReported by: __' + str(ctx.message.author.name) + '__' +
                        '\n\nhttps://www.google.com/maps?q=loc:' + str(gym_data[0][2]) + ',' + str(gym_data[0][3]) )
                else:
                    cursor.execute("INSERT INTO raids("
                                   "id, external_id, fort_id , level, "
                                   "pokemon_id, move_1, move_2, time_spawn, "
                                   "time_battle, time_end, cp)"
                                   "VALUES "
                                   "(null, null, " + str(gym_id) + ", "
                                   + str(raw_raid_level) + ", " + str(pokemon_id) + ", null, null, "
                                   "null, " + str(calendar.timegm(current_time.timetuple())) + ", " + str(remaining_time) + ", null);")
                    await bot.say('Added new **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + ' Raid' + '**' +
                                  '\nGym: **' + str(gym_name) + ' Gym**' +
                                  '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                                  '\nTime Left: **' + str(raw_time_remaining) + '** minutes.' +
                                  '\nTeam: **' + str(get_team_name(gym_team_id)) + '**')
                    await bot.send_message(discord.Object(id=log_channel),
                        '----------------------------------------------------' +
                        '\nReport: **Level ' + str(raw_raid_level) + ' ' + str(pokemon_name) + ' Raid' + '**' +
                        '\nGym: **' + str(gym_name) + ' Gym**' +
                        '\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**' +
                        '\nTeam: **' + str(get_team_name(gym_team_id))+ '**' +
                        '\nReported by: __' + str(ctx.message.author.name) + '__' +
                        '\n\nhttps://www.google.com/maps?q=loc:' + str(gym_data[0][2]) + ',' + str(gym_data[0][3]) )
                    print(str(ctx.message.author.name) + ' reported a ' + str(pokemon_name) + ' raid at ' + str(gym_name) + ' gym (' + str(get_team_name(gym_team_id)) + ') with ' + str(raw_time_remaining) + ' minutes left.')
            # Check if fort_id exists in fort_sightings.  If so update the entry, otherwise enter as a new entry.
            cursor.execute("SELECT id, fort_id, team FROM fort_sightings WHERE fort_id='" + str(gym_id) + "';")
            fs_count = cursor.rowcount
            if (fs_count):
                cursor.execute("UPDATE fort_sightings SET team='" + str(gym_team_id) + "' WHERE fort_id='" + str(gym_id) + "';")
            else:
                cursor.execute("INSERT INTO fort_sightings(fort_id, team, last_modified) VALUES (" + str(gym_id) + ", " + str(gym_team_id) + ", " + str(calendar.timegm(current_time.timetuple())) + ");")

            database.commit()
            
        except:
            database.rollback()
            if ( count > 1 ):
                await bot.say('Unsuccesful add to the map. There are multiple gyms with the word "' + str(raw_gym_name) + '" in it:\n' + str(gym_names) + '\nBe a little more specific.')
            elif ( count == 0 ):
                await bot.say('No gym with the word "' + str(raw_gym_name) + '" in it. Use the !list command to list all gyms available in the region.\n')
            else:
                await bot.say('Unsuccesful add to the map. !raid "*gym_name*" *pokemon_name* *raid_level* *minutes_left*\n')

@raid.error
async def handle_missing_raid_arg(ctx, error):
    await bot.say('Unsuccesful add to the map. Missing arguments. !raid  "*gym_name*"  *pokemon_name*  *raid_level*  *minutes_left*  *gym_team*\n')

@bot.command(pass_context=True)
async def list(ctx, raw_gym_name):
    if ctx and ctx.message.channel.id == str(bot_channel):
        try:
            if raw_gym_name.isnumeric():
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE id LIKE '%" + str(raw_gym_name) + "%';")
            else:
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE name LIKE '%" + str(raw_gym_name) + "%';")
            data = cursor.fetchall()
            count = cursor.rowcount
            gym_names = ''
            for gym in data:
                gym_names += str(gym[0]) + ': ' + gym[1] + ' (' + str(gym[2]) + ', ' + str(gym[3]) + ')\n'
            database.commit()
            await bot.say('There are ' + str(count) + ' gyms with the word(s) "' + str(raw_gym_name) + '" in it:\n' + str(gym_names))
        except:
            database.rollback()
            await bot.say('No gym with the word "' + str(raw_gym_name) + '" in it OR too many to list. Try narrowing down your search.')

@list.error
async def handle_missing_arg(ctx, error):
    try:
        cursor.execute("SELECT id, name, lat, lon FROM forts;")
        data = cursor.fetchall()
        count = cursor.rowcount
        gym_names = ''
        for gym in data:
            gym_names += str(gym[0]) + ': ' + gym[1] + ' (' + str(gym[2]) + ', ' + str(gym[3]) + ')\n'
        database.commit()
        await bot.say('There are ' + str(count) + ' gyms in the region:\n' + str(gym_names))
    except:
        database.rollback()
        await bot.say('No gyms found OR too many to list.  Try narrowing down your search.')
  

@bot.command(pass_context=True)
async def map(ctx):
    if ctx:
        await bot.say('Visit' + str(website) + ' to see our crowd-sourced Raids!')


@bot.command(pass_context=True)
async def helpme(ctx):
    if ctx:
        help_embed=discord.Embed(
            title='PoGoSD CSPM Help',
            description='**Mapping Raids:**\n'
                        'To add a raid to the live map, use the following command:\n'
                        '`!raid <gym_name or gym_id> <pokemon_name> <raid_level> <minutes remaining> <gym team>`\n'
                        'Example: `!raid "Fave Bird Mural" Lugia 5 45 Instinct`\n\n'
                        'Example: `!raid mural lugia 5 45 inst`\n\n'
                        'Example: `!raid 55 lugia 5 45 yel`\n\n'
                        '*To see raids that are crowdsourced, please make sure you tick the raids option in layers (top right)*\n\n'
                        '**List Gyms:**\n'
                        'This will help you search for gym names and ids:\n'
                        '`!list <search_string or number>`\n'
                        'Example: `!list 55`\n'
                        'Result: `55: Name of a Gym`',
            color=3447003
        )
        await bot.say(embed=help_embed)

bot.run(token)
