from replit import db

import admin
import asyncio
import cfg
import re
import util

# Announce the loot
async def announcement(message):
  if (cfg.is_distributing == True):
    await cfg.admin.send('Last item still in progress, please cancel or confirm');
    return;

  cfg.is_distributing = True;
  cfg.current_item = message.content.split(" ")[1];
  cfg.item_gp = int(message.content.split(" ")[2]);
  cfg.main_spec = {};

  for author in cfg.raid_roster.keys():
    await author.send('%s %s \n Reply 1 for main spec'%(cfg.current_item, cfg.item_gp));

  await asyncio.sleep(30);
  await _calculate_result(); 

# User main spec the loot
async def main_spec_response(message):
  if (cfg.is_distributing == False):
    await message.author.send('现在没有正在分配物品');
    return;
  
  if (cfg.main_spec == None):
    await message.author.send('当前物品已经结算完毕');
    return;

  if (message.author in cfg.main_spec.keys()):
    await message.author.send('您已经参与本次Loot分配');
    return;

  game_id = cfg.raid_roster[message.author];
  if (db['%s_gp'%(game_id)] == 0):
    await message.author.send('您的gp 有问题请联系%s'%{cfg.admin});
    return;
  
  pr = float(db['%s_ep'%(game_id)])/float(db['%s_gp'%(game_id)]);

  cfg.main_spec.update({message.author: pr});

async def cancel(message):
  if (cfg.is_distributing == False):
    await message.author.send('现在没有正在分配物品');
    return;

  if (cfg.current_winner == None):
    await message.author.send('当前物品还未结算完毕');
    return;

  _reset();
  for author in cfg.raid_roster.keys():
    await author.send('本次Loot已经取消');

async def confirm(message):
  if (cfg.is_distributing == False):
    await message.author.send('现在没有正在分配物品');
    return;

  if (cfg.current_winner == None):
    await message.author.send('当前物品还未结算完毕');
    return;

  game_id_match = re.findall("-id ([^ ]+)", message.content, re.IGNORECASE);
  
  if (len(game_id_match) == 1):
    game_id = game_id_match[0].split(" ")[1];

    if (game_id not in cfg.raid_roster.values()):
      await message.author.send('当前Raid无法找到%s'%(game_id));
      return;
    else:
      cfg.current_winner = cfg.raid_roster.keys()[cfg.raid_roster.values().index(game_id)];

  if (cfg.current_winner == '无人'):
    await message.author.send('无法分配流拍物品，请取消 或者指定分配人');
    return;

  final_gp = cfg.item_gp;
  gp_percent = re.findall("-percent ([0-9]+)", message.content, re.IGNORECASE);
  
  if (len(gp_percent) == 1):
    percent = int(gp_percent[0].split(" ")[1]);
    if (percent == 20 | percent == 50):
      final_gp *= float(percent)/100.0;
      final_gp = int(final_gp);
    else:
      await message.author.send('非预设折扣,只能接受20%或者50%');
      return;

  admin.update_gp(cfg.raid_roster[cfg.current_winner], final_gp);

  for author in cfg.raid_roster.keys():
    await author.send('本次%s已经分配给%s花费GP%s'%(cfg.current_item, cfg.raid_roster[cfg.current_winner], final_gp));

  await cfg.current_winner.send('消费%s, 总GP%s'%(final_gp, db['%s_gp'%(cfg.raid_roster[cfg.current_winner])]));
  
  _reset();
  

async def _calculate_result():
  highest_pr = 0;
  winner = None;

  main_spec = cfg.main_spec.copy();
  cfg.main_spec = None;

  for author in main_spec.keys():
    pr = main_spec[author];
    if (pr > highest_pr):
      highest_pr = pr;
      winner = author;

  if (winner != None):
    all_string = '参与者\n';
    winner_string = '\n获胜者\n';
    for author in cfg.raid_roster.keys():
      if (author in main_spec.keys()):
        all_string += 'id: %s, pr: %s\n'%(cfg.raid_roster[author], main_spec[author]);     
      if (author == winner):
        winner_string += 'id: %s, pr: %s'%(cfg.raid_roster[author], main_spec[author]);

    for author in cfg.raid_roster.keys():
      await author.send(all_string + winner_string);

    # Make sure all the message has been sent before set winner, otherwise other operation may happen during the messaging process.
    cfg.current_winner = winner;
  else:
    for author in cfg.raid_roster.keys():
      await author.send('本次Loot无人GP需求');

    # Make sure all the message has been sent before set winner, otherwise other operation may happen during the messaging process.
    cfg.current_winner = '无人';

  await cfg.admin.send('结算完毕 请确认分配或取消');

def _reset():
  cfg.main_spec = None;
  cfg.current_item = None;
  cfg.current_winner = None;
  cfg.is_distributing = False;
  cfg.item_gp = None;