from lib import libtcodpy as libtcod
from map import Map


class Game(object):

  width = 50
  height = 40

  def __init__(self):
    self.__entities = []
    self.__recompute_fov = True

  def setup(self):
    libtcod.console_set_custom_font('assets/dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(self.width, self.height, 'Pyrl', False)
    self.__create_map()
    self.__con = libtcod.console_new(self.width, self.height)
    self.__generate_entities()

  def __create_map(self):
    self.__map = Map(self.width, self.height)
    self.__map.setup()

  def __generate_entities(self):
    player_x, player_y = self.__map.rooms[0].center()
    self.__player = self.__create_entity(player_x, player_y, '@', libtcod.white)
    npc_x, npc_y = self.__map.rooms[-1].center()
    self.__create_entity(npc_x, npc_y, '@', libtcod.yellow)

  def __create_entity(self, x, y, char, color):
    entity = Entity(x, y, char, color, self.__con, self.__map)
    self.__entities.append(entity)
    return entity

  def main_loop(self):
    while not libtcod.console_is_window_closed():
      self.__render_all()

      libtcod.console_flush()

      self.__clear_all()

      exit = self.__handle_keys()
      if exit:
        break

  def __render_all(self):
    if self.__recompute_fov:
      self.__recompute_fov = False
      self.__map.compute_fov(self.__player.x, self.__player.y)

    for y in xrange(self.height):
      for x in xrange(self.width):
        visible = self.__map.is_in_fov(x, y)
        tile = self.__map.get(x, y)
        if not visible:
          if tile.explored:
            if tile.blocks_sight:
              libtcod.console_put_char_ex(self.__con, x, y, '#', libtcod.dark_grey, libtcod.black)
            else:
              libtcod.console_put_char_ex(self.__con, x, y, '.', libtcod.dark_grey, libtcod.black)
        else:
          if tile.blocks_sight:
            libtcod.console_put_char_ex(self.__con, x, y, '#', libtcod.white, libtcod.black)
          else:
            libtcod.console_put_char_ex(self.__con, x, y, '.', libtcod.white, libtcod.black)
          tile.explored = True

    for entity in self.__entities:
      entity.draw()

    libtcod.console_blit(self.__con, 0, 0, self.width, self.height, 0, 0, 0)

  def __clear_all(self):
    for entity in self.__entities:
      entity.clear()

  def __handle_keys(self):
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ESCAPE:
      return True
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      self.__player.move(0, -1)
      self.__recompute_fov = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      self.__player.move(0, 1)
      self.__recompute_fov = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      self.__player.move(-1 ,0)
      self.__recompute_fov = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      self.__player.move(1, 0)
      self.__recompute_fov = True


class Entity(object):

  def __init__(self, x, y, char, color, console, map_):
    self.__x = x
    self.__y = y
    self.__char = char
    self.__color = color
    self.__con = console
    self.__map = map_

  @property
  def x(self):
    return self.__x

  @property
  def y(self):
    return self.__y

  def draw(self):
    if not self.__map.is_in_fov(self.__x, self.__y):
      return
    libtcod.console_set_default_foreground(self.__con, self.__color)
    libtcod.console_put_char(self.__con, self.__x, self.__y, self.__char, libtcod.BKGND_NONE)

  def clear(self):
    libtcod.console_put_char(self.__con, self.__x, self.__y, ' ', libtcod.BKGND_NONE)

  def move(self, dx, dy):
    new_x = self.__x + dx
    new_y = self.__y + dy
    if not self.__map.get(new_x, new_y).blocked:
      self.__x = new_x
      self.__y = new_y
