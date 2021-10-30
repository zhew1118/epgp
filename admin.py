from replit import db

import cfg;
import constant
import logging
import re

async def start_new_raid(message):
  logger=logging.getLogger();

  if (cfg.admin != None):
    await message.channel.send('%s已经开始本次Raid，请稍后再试'%(cfg.admin));
  else:
    cfg.admin = message.author;
    await message.channel.send('%s开始本次Raid'%(cfg.admin));
    logger.info('%s开始本次Raid'%(cfg.admin));

async def retrive_roster(message):
  if (cfg.admin == None):
    await start_new_raid(message);

  await message.channel.send('名单%s,总计%s'%(cfg.raid_roster.values(), len(cfg.raid_roster.values())));

async def reward_ep(message):
  if (cfg.admin == None):
    await start_new_raid(message);

  ep = int(message.content.split(" ")[-1]);
  
  for author in cfg.raid_roster.keys():
    game_id = cfg.raid_roster[author];
    update_ep(game_id, ep);
    await author.send('%s EP奖励生效, 当前EP: %s,当前GP: %s'%(ep, db['%s_ep'%(game_id)], db['%s_gp'%(game_id)]));


async def add_new_member(message):    
  id = re.match(constant.add_new_member_reg, message.content, re.IGNORECASE).group(1);
  db['%s_ep'%(id)] = 0;
  db['%s_gp'%(id)] = 0;

  ep = re.findall(constant.ep_reg, message.content, re.IGNORECASE);
  gp = re.findall(constant.gp_reg, message.content, re.IGNORECASE);

  if (len(ep) == 1):
    update_ep(id, int(ep[0].split(" ")[1]));

  if (len(gp) == 1):
    update_gp(id, int(gp[0].split(" ")[1]));
  else:
    update_gp(id, 1000);

async def all_pr_list(message):
  db_keys = db.keys();
  game_id_list = [];

  for db_key in db_keys:
    match = re.fullmatch("([^ ]+)\_ep", db_key);
    if (match):
      print(db_key);
      game_id = match[1];
      if (db.get('%s_gp'%(game_id)) != None):
        game_id_list.append(game_id);
      
  pr_list = {};
  ep_list = {};
  gp_list = {};
  for game_id in game_id_list:
    ep = db['%s_ep'%(game_id)];
    gp = db['%s_gp'%(game_id)];
    if (gp != 0):
      pr_list.update({game_id: float(ep)/float(gp)});
      ep_list.update({game_id: ep});
      gp_list.update({game_id:gp});

  pr_message = 'ID  EP  GP  PR\n';
  sorted_pr_list = sorted(pr_list.items(), key=lambda x: x[1], reverse=True);
  for entry in sorted_pr_list:
    game_id = entry[0];
    pr_message += '%s  %s  %s  %s\n'%(game_id, ep_list[game_id], gp_list[game_id], entry[1]);

  await message.channel.send(pr_message);

def update_ep(game_id, ep):
  db['%s_ep'%(game_id)] = db['%s_ep'%(game_id)] + ep;
  
def update_gp(game_id, gp):
  print('update gp %s'%(gp));
  db['%s_gp'%(game_id)] = db['%s_gp'%(game_id)] + gp;
    