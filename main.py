from replit import db

import admin
import cfg
import constant
import discord
import distribute
import os
import re
import user

import logging

logging.basicConfig(filename="test_log1.log", 
					format='%(asctime)s %(message)s', );
logger=logging.getLogger();
logger.setLevel(logging.INFO);


client = discord.Client();

@client.event
async def on_ready():
  initialize_global_vars();

  print('CF Senior EPGP start');

@client.event
async def on_message(message):
  if(message.author == client.user):
    return;
  
  if(match_keywork(constant.admin_reg, message)):
    await on_admin_message(message);
  elif(match_keywork(constant.dis_reg, message)):
    await on_distribution_message(message);
  else:
    await on_user_message(message);


async def on_user_message(message):
  if(match_keywork(constant.login_reg, message)):
    await user.member_login(message);
  elif(match_keywork(constant.raid_pr_list_reg, message)):
    await user.raid_pr_list(message);
  elif(match_keywork(constant.main_spec_reg, message)):
    await distribute.main_spec_response(message);
  else:
    await message.author.send('''
      指令              用途
      Login 游戏ID      进入Raid
      Raid PR          查看当前Raid中所有人的PR信息
      Main Spec        需求当前装备
      1                需求当前装备

      Admin指令（只有管理员可以使用）
      Admin 具体指令
      Dis 具体指令
    ''');

async def on_admin_message(message):
  if (str(message.author) not in os.environ['admin_token']):
    await message.channel.send('您不是管理员');

  if(match_keywork(constant.start_new_raid_reg, message)):
    await admin.start_new_raid(message);
  elif(match_keywork(constant.add_new_member_reg, message)):
    await admin.add_new_member(message);
  elif(match_keywork(constant.reward_ep, message)):
    await admin.reward_ep(message);
  elif(match_keywork(constant.retrive_roster, message)):
    await admin.retrive_roster(message);
  elif(message.content.startswith('all pr')):
    await admin.all_pr_list(message);
  else:
    await message.author.send('');

async def on_distribution_message(message):
  if (str(message.author) not in os.environ['admin_token']):
    await message.channel.send('您不是管理员');

  if(match_keywork(constant.announcement_reg, message)):
    await distribute.announcement(message);
  elif(match_keywork(constant.dis_cancel_reg, message)):
    await distribute.cancel(message);
  elif(match_keywork(constant.dis_confirm_reg, message)):
    await distribute.confirm(message);
  else:
    await message.author.send('''
      指令              用途
      Dis 物品 GP       准备分配物品
      Dis confirm [-percent 20|50] [-id 游戏ID] 确认分配物品
      Dis cancel       取消当前分配
    ''');

def match_keywork(keyword, message):
  return re.fullmatch(keyword, message.content, re.IGNORECASE);

def initialize_global_vars():
  cfg.admin = None;
  cfg.raid_roster = {};
  cfg.main_spec = None;
  cfg.current_item = None;
  cfg.current_winner = None;
  cfg.is_distributing = False;
  cfg.item_gp = None;

client.run(os.environ['discord_token']);