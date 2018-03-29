import MySQLdb
import discord
from discord.ext import commands
import asyncio
from pokemonlist import pokemon, pokejson
from config import bot_channel, token, host, user, password, database, website, log_channel
import datetime
import calendar
import time

bot = commands.Bot(command_prefix = '!')#set prefix to !

database = MySQLdb.connect(host,user,password,database)

cursor = database.cursor()

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

print('CSPM Started.')

#raid function
@bot.command(pass_context=True)
async def raid(ctx, arg, arg2, arg3, arg4): #arg = gym name, arg2 = pokemon name, arg3 = level, arg4 = time remaining
    if ctx and ctx.message.channel.id == str(bot_channel):
        pokemon_name = str(arg2).capitalize()
        pokemon_id = find_pokemon_id(pokemon_name)
        remaining_time = get_time(int(arg4))
        current_time = datetime.datetime.utcnow()
        
        try:
            if arg.isnumeric():
                cursor.execute("SELECT id, name FROM forts WHERE id LIKE '%" + str(arg) + "%';")
            else:
                cursor.execute("SELECT id, name FROM forts WHERE name LIKE '%" + str(arg) + "%';")
            gym_data = cursor.fetchall()
            count = cursor.rowcount

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
                    gym_names += str(gym[0]) + ': ' + gym[1] +'\n'



            if ( pokemon_name == "Egg" ):
                est_end_time = remaining_time + 2700
                
                if (raid_count):
                    cursor.execute("UPDATE raids SET level='" + str(arg3) + "', time_battle='" + str(remaining_time) + "', time_end='" + str(est_end_time) + "' WHERE id='" + str(raid_id)+ "';")
                    await bot.say('Updated **Level ' + str(arg3) + ' ' + str(pokemon_name) + '**\nGym: **' + str(gym_id) + ': ' + str(gym_name) + ' Gym**\n' +
                                  'Hatches: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(est_end_time))) + '**')
                else:
                    cursor.execute("INSERT INTO raids("
                                   "id, external_id, fort_id , level, "
                                   "pokemon_id, move_1, move_2, time_spawn, "
                                   "time_battle, time_end, cp)"
                                   "VALUES "
                                   "(null, null, " + str(gym_id) + ", "
                                   + str(arg3) + ", " + str(pokemon_id) + ", null, null, "
                                   "null, " + str(remaining_time) + ", " + str(est_end_time) + ", null);")
                    await bot.say('Added **Level ' + str(arg3) + ' ' + str(pokemon_name) + '** raid at the **' + str(gym_name) + '** gym with **' + str(arg4) + '** minutes left.')
            else:
                # Update Egg to a hatched Raid Boss
                if (raid_count):
                    cursor.execute("UPDATE raids SET pokemon_id='" + str(pokemon_id) + "', level='" + str(arg3) + "', time_battle='" + str(calendar.timegm(current_time.timetuple())) + "', time_end='" + str(remaining_time) + "' WHERE id='" + str(raid_id)+ "';")
                    await bot.say('Updated **Level ' + str(arg3) + ' ' + str(pokemon_name) + '** raid.\nGym: **' + str(gym_id) + ': ' + str(gym_name) + ' Gym**\n' +
                                  'Raid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**')
                else:
                    cursor.execute("INSERT INTO raids("
                                   "id, external_id, fort_id , level, "
                                   "pokemon_id, move_1, move_2, time_spawn, "
                                   "time_battle, time_end, cp)"
                                   "VALUES "
                                   "(null, null, " + str(gym_id) + ", "
                                   + str(arg3) + ", " + str(pokemon_id) + ", null, null, "
                                   "null, " + str(calendar.timegm(current_time.timetuple())) + ", " + str(remaining_time) + ", null);")
                    await bot.say('Added **Level ' + str(arg3) + ' ' + str(pokemon_name) + '** raid at the **' + str(gym_name) + '** gym with **' + str(arg4) + '** minutes left.')

            # Execute insert into fort_sightings to supress a map error
            cursor.execute("INSERT INTO fort_sightings(fort_id, team) VALUES (" + str(gym_id) + ", null);")

            database.commit()
            
            
            if ( pokemon_name == "Egg" ):
                await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + ' reported a **Level ' + str(arg3) + ' ' + str(pokemon_name) + '** with about ' + str(arg4) + ' minutes left.\nGym: **' + str(gym_name) + ' Gym**\nHatches: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(est_end_time))) + '**') and print(str(ctx.message.author.name) + ' reported a ' + str(pokemon_name) + ' raid at ' + str(gym_name) + ' gym with ' + str(arg4) + ' minutes left.')
            else:
                await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + ' reported a **Level ' + str(arg3) + ' ' + str(pokemon_name) + ' Raid** with about ' + str(arg4) + ' minutes left.\nGym: **' + str(gym_name) + ' Gym**\nRaid Ends: **' + str(time.strftime('%I:%M %p',  time.localtime(remaining_time))) + '**') and print(str(ctx.message.author.name) + ' reported a ' + str(pokemon_name) + ' raid at ' + str(gym_name) + ' gym with ' + str(arg4) + ' minutes left.')
        except:
            database.rollback()
            if ( count > 1 ):
                await bot.say('Unsuccesful add to the map. There are multiple gyms with the word "' + str(arg) + '" in it:\n' + str(gym_names) + '\nBe a little more specific.')
            elif ( count == 0 ):
                await bot.say('No gym with the word "' + str(arg) + '" in it. Use the !list command to list all gyms available in the region.\n')
            else:
                await bot.say('Unsuccesful add to the map. !raid "*gym_name*" *pokemon_name* *raid_level* *minutes_left*\n')

@bot.command(pass_context=True)
async def list(ctx, arg): #arg = string to search
    if ctx and ctx.message.channel.id == str(bot_channel):
        try:
            if arg.isnumeric():
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE id LIKE '%" + str(arg) + "%';")
            else:
                cursor.execute("SELECT id, name, lat, lon FROM forts WHERE name LIKE '%" + str(arg) + "%';")
            data = cursor.fetchall()
            count = cursor.rowcount
            gym_names = ''
            for gym in data:
                gym_names += str(gym[0]) + ': ' + gym[1] + ' (' + str(gym[2]) + ', ' + str(gym[3]) + ')\n'
            database.commit()
            await bot.say('There are ' + str(count) + ' gyms with the word(s) "' + str(arg) + '" in it:\n' + str(gym_names))
        except:
            database.rollback()
            await bot.say('No gym with the word "' + str(arg) + '" in it OR too many to list. Try narrowing down your search.')

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
async def spawn(ctx, arg, arg2, arg3):
    if ctx and ctx.message.channel.id == str(bot_channel) and arg in pokemon:
        pokemon_id = find_pokemon_id(str(arg).capitalize())
        time = get_time(15)
        try:
            cursor.execute("INSERT INTO sightings("
                           "id, pokemon_id, spawn_id, expire_timestamp, encounter_id, lat, lon, "
                           "atk_iv, def_iv, sta_iv, move_1, move_2, gender, "
                           "form, cp, level, updated, weather_boosted_condition, weather_cell_id, weight) "
                           "VALUES (null, " + str(pokemon_id) +", null," + str(time) + ", null," + str(arg2) + ", " + str(arg3) +
                           ", null, null, null, null, null, null,"
                           " null, null, null, null, null, null, null);")
            database.commit()
            await bot.say('Successfully added your spawn to the live map.\n'
                          '*Pokemon timers are automatically given 15 minutes since the timer is unknown.*')
            await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + ' said there was a wild ' + str(arg) +
                                   ' at these coordinates: ' + str(arg2) + ', ' + str(arg3))  and print(str(ctx.message.author.name) + ' said there was a wild ' + str(arg) +
                                   ' at these coordinates: ' + str(arg2) + ', ' + str(arg3))
        except:
            await bot.say('Unsuccessful in database query, your reported spawn was not added to the live map.')
@bot.command(pass_context=True)
async def map(ctx):
    if ctx:
        await bot.say('Hey! Visit' + str(website) + ' to see our crowd-sourced spawns!')

bot.run(token)
