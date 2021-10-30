from replit import db

import cfg;
import logging
import util

# User will use this to login into the raid
async def member_login(message):
  logger=logging.getLogger();
      
  if (cfg.admin == None):
    await message.channel.send('管理员还未开始本次Raid, 请稍后再试');
    return;

  game_id = message.content.split(" ")[1];
  
  if (util.is_valid_game_id(game_id) == False):
    await message.channel.send('您的epgp存在问题, 请联系本次管理员%s'%(cfg.admin));
  else:
    if (cfg.raid_roster.get(message.author) !=  None):
      await message.channel.send('用户已经登陆');
    else:
      cfg.raid_roster.update({message.author: game_id});
      login_message = '用户 %s 已经登陆, EP: %s, GP: %s'%(game_id, db['%s_ep'%(game_id)], db['%s_gp'%(game_id)]);
      await message.channel.send(login_message);

      logger.info(login_message);

# User will use this to check the pr in Raid
async def raid_pr_list(message):
  if (cfg.admin == None):
    await message.channel.send('管理员还未开始本次Raid, 请稍后再试');
    return;

  if (cfg.raid_roster.get(message.author) ==  None):
    await message.channel.send('您还未加入本次Raid');
    return;

  pr_list = {};
  ep_list = {};
  gp_list = {};
  for author in cfg.raid_roster.keys():
    game_id = cfg.raid_roster[author];
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
    

  
