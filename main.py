from lib import libtcodpy as libtcod
 

class Game(object):

  width = 40
  height = 30

  def __init__(self):
    self.__entities = []

  def setup(self):
    libtcod.console_set_custom_font('assets/dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(self.width, self.height, 'Pyrl', False)
    self.__con = libtcod.console_new(self.width, self.height)
    self.__generate_entities()

  def main_loop(self):
    while not libtcod.console_is_window_closed():
      for entity in self.__entities:
        entity.draw()

      libtcod.console_blit(self.__con, 0, 0, self.width, self.height, 0, 0, 0)
      libtcod.console_flush()

      for entity in self.__entities:
         entity.clear()

      exit = self.__handle_keys()
      if exit:
        break

  def __handle_keys(self):
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ESCAPE:
      return True
    
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      self.__player.move(0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      self.__player.move(0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      self.__player.move(-1 ,0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      self.__player.move(1, 0)


  def __generate_entities(self):
    self.__player = self.__create_entity(self.width/2, self.height/2, '@', libtcod.white)
    self.__create_entity(self.width/2 - 5, self.height/2, '@', libtcod.yellow)

  def __create_entity(self, x, y, char, color):
    entity = Entity(x, y, char, color, self.__con)
    self.__entities.append(entity)
    return entity


class Entity(object):

  def __init__(self, x, y, char, color, console):
    self.__x = x
    self.__y = y
    self.__char = char
    self.__color = color
    self.__con = console

  def draw(self):
    libtcod.console_set_default_foreground(self.__con, self.__color)
    libtcod.console_put_char(self.__con, self.__x, self.__y, self.__char, libtcod.BKGND_NONE)

  def clear(self):
    libtcod.console_put_char(self.__con, self.__x, self.__y, ' ', libtcod.BKGND_NONE)

  def move(self, dx, dy):
    self.__x += dx
    self.__y += dy


if __name__ == "__main__":
  game = Game()
  game.setup()
  game.main_loop()
