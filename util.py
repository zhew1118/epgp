from replit import db

def is_valid_game_id(game_id):
  return (db.get('%s_ep'%(game_id)) != None) & (db.get('%s_gp'%(game_id)) != None);