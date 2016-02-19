from lib import libtcodpy as libtcod
from map import Map

import math


class Game(object):

  width = 50
  height = 40
  max_room_monsters = 3

  def __init__(self):
    self.__state = 'playing'
    self.__recompute_fov = True

  def setup(self):
    libtcod.console_set_custom_font('assets/dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(self.width, self.height, 'Pyrl', False)
    self.__con = libtcod.console_new(self.width, self.height)
    self.__map = Map(self.width, self.height, self.__con)
    self.__map.setup()
    self.__generate_entities()

  def __generate_entities(self):
    player_x, player_y = self.__map.rooms[0].center()
    self.__player = self.__create_entity(player_x, player_y, '@', 'player', libtcod.white, True, Fighter(hp=30, power=5, defense=2, on_death=self.__player_death))
    self.__generate_monsters()

  def __generate_monsters(self):
    for room in self.__map.rooms:
      num_monsters = libtcod.random_get_int(0, 0, self.max_room_monsters)
      for i in xrange(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)
        if Entity.has_blocker(x, y):
          continue
        if libtcod.random_get_int(0, 0, 1) == 0:
          self.__create_entity(x, y, 'g', 'goblin', libtcod.desaturated_amber, True, Fighter(hp=12, power=2, defense=1, on_death=monster_death), BasicMonster())
        else:
          self.__create_entity(x, y, 'k', 'kobold', libtcod.light_green, True, Fighter(hp=10, power=4, defense=0, on_death=monster_death), BasicMonster())

  def __create_entity(self, x, y, char, name, color, blocks=False, fighter=None, ai=None):
    return Entity.create(x, y, char, name, color, self.__con, self.__map, blocks, fighter, ai)

  def main_loop(self):
    while not libtcod.console_is_window_closed():
      self.__render_all()
      libtcod.console_flush()
      self.__clear_all()

      action = self.__handle_keys()
      if action == 'exit':
        break
      elif self.__state == 'playing' and action != 'pass':
        for entity in Entity.entities:
          if entity.ai:
            entity.ai.take_turn()

  def __render_all(self):
    if self.__recompute_fov:
      self.__recompute_fov = False
      self.__map.compute_fov(self.__player.x, self.__player.y)

    self.__map.render()

    for entity in Entity.entities:
      if entity.name != 'player':
        entity.draw()
    self.__player.draw()

    libtcod.console_blit(self.__con, 0, 0, self.width, self.height, 0, 0, 0)

  def __clear_all(self):
    for entity in Entity.entities:
      entity.clear()

  def __handle_keys(self):
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ESCAPE:
      return 'exit'
    if self.__state == 'playing':
      if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        self.__player.move_or_attack(0, -1)
        self.__recompute_fov = True
      elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        self.__player.move_or_attack(0, 1)
        self.__recompute_fov = True
      elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        self.__player.move_or_attack(-1 ,0)
        self.__recompute_fov = True
      elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        self.__player.move_or_attack(1, 0)
        self.__recompute_fov = True
      else:
        return 'pass'

  def __player_death(self, player):
    self.__state = 'game-over'
    print 'You died!'
    player.char = '%'
    player.color = libtcod.dark_red


class Entity(object):

  entities = []
  player = None

  @classmethod
  def create(cls, x, y, char, name, color, console, map, blocks=False, fighter=None, ai=None):
    entity = Entity(x, y, char, name, color, console, map, blocks, fighter, ai)
    cls.entities.append(entity)
    if entity.name == 'player':
      cls.player = entity
    return entity

  @classmethod
  def has_blocker(cls, x, y):
    for entity in cls.entities:
      if entity.blocks and entity.x == x and entity.y == y:
        return True
    return False

  def __init__(self, x, y, char, name, color, console, map_, blocks, fighter, ai):
    self.__x = x
    self.__y = y
    self.__con = console
    self.__map = map_
    self.char = char
    self.color = color
    self.name = name
    self.blocks = blocks
    self.fighter = fighter
    if self.fighter:
      self.fighter.owner = self
    self.ai = ai
    if self.ai:
      self.ai.owner = self

  @property
  def x(self):
    return self.__x

  @property
  def y(self):
    return self.__y

  def draw(self):
    if not self.is_in_fov():
      return
    libtcod.console_set_default_foreground(self.__con, self.color)
    libtcod.console_put_char(self.__con, self.__x, self.__y, self.char, libtcod.BKGND_NONE)

  def clear(self):
    libtcod.console_put_char(self.__con, self.__x, self.__y, ' ', libtcod.BKGND_NONE)

  def is_in_fov(self):
    return self.__map.is_in_fov(self.__x, self.__y)

  def move(self, dx, dy):
    new_x = self.__x + dx
    new_y = self.__y + dy
    if not self.__map.get(new_x, new_y).blocked and not Entity.has_blocker(new_x, new_y):
      self.__x = new_x
      self.__y = new_y
      return True

  def move_or_attack(self, dx, dy):
    new_x = self.__x + dx
    new_y = self.__y + dy
    target = None
    for entity in Entity.entities:
      if entity.fighter and entity.x == new_x and entity.y == new_y:
        target = entity
        break
    if target is not None:
      print self.fighter
      self.fighter.attack(target)
    else:
      self.move(dx, dy)

  def move_towards(self, target_x, target_y):
    #vector from this object to the target, and distance
    dx = target_x - self.x
    dy = target_y - self.y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    #normalize it to length 1 (preserving direction), then round it and
    #convert to integer so the movement is restricted to the map grid
    dx = int(round(dx / distance))
    dy = int(round(dy / distance))
    if not self.move(dx, dy):
      self.move(dy, dx)

  def distance_to(self, other):
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)


class Fighter(object):

  def __init__(self, hp, power, defense, on_death=None):
    self.max_hp = hp
    self.hp = hp
    self.power = power
    self.defense = defense
    self.on_death = on_death

  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      print self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.' 
      target.fighter.take_damage(damage)

  def take_damage(self, damage):
    if damage > 0:
      self.hp -= damage
      if self.hp <= 0:
        if self.on_death:
          self.on_death(self.owner)

class BasicMonster(object):

  def take_turn(self):
    monster = self.owner
    player = Entity.player
    if monster.is_in_fov():
      if monster.distance_to(player) >= 2:
        monster.move_towards(player.x, player.y)
      else:
        monster.fighter.attack(player)

def monster_death(monster):
  print monster.name.capitalize() + ' is dead!'
  monster.char = '%'
  monster.color = libtcod.dark_red
  monster.blocks = False
  monster.fighter = monster.ai = None
  monster.name = monster.name + ' corpse'
