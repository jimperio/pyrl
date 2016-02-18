from lib import libtcodpy as libtcod


class Map(object):

  room_max_size = 8
  room_min_size = 4
  max_rooms = 50
  torch_radius = 10
  light_walls = True
  fov_algorithm = 0 # default

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.__map = [[Tile(True) for x in xrange(self.width)] for y in xrange(self.height)]
    self.__rooms = []

  def setup(self):
    self.__generate_rooms()
    self.__fov_map = libtcod.map_new(self.width, self.height)
    for y in range(self.height):
      for x in range(self.width):
        tile = self.__map[y][x]
        libtcod.map_set_properties(self.__fov_map, x, y, not tile.blocks_sight, not tile.blocked)

  def get(self, x, y):
    return self.__map[y][x]

  @property
  def rooms(self):
    return self.__rooms

  def compute_fov(self, x, y):
    libtcod.map_compute_fov(self.__fov_map, x, y, self.torch_radius, self.light_walls, self.fov_algorithm)

  def is_in_fov(self, x, y):
    return libtcod.map_is_in_fov(self.__fov_map, x, y)

  def __generate_rooms(self):
    rooms = []
    for i in xrange(self.max_rooms):
      w = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
      h = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
      x = libtcod.random_get_int(0, 1, self.width - w - 2)
      y = libtcod.random_get_int(0, 1, self.height - h - 2)
      new_room = Rect(x, y, w, h)
      intersects = False
      for prev_room in rooms:
        if new_room.intersects(prev_room):
          intersects = True
          break
      if intersects:
        continue
      self.create_room(new_room)
      if len(rooms) > 0:
        prev_x, prev_y = rooms[-1].center()
        new_x, new_y = new_room.center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          self.create_tunnel(prev_x, new_x, y=prev_y)
          self.create_tunnel(prev_y, new_y, x=new_x)
        else:
          self.create_tunnel(prev_y, new_y, x=prev_x)
          self.create_tunnel(prev_x, new_x, y=new_y)
      rooms.append(new_room)
    self.__rooms = rooms

  def create_room(self, room):
    for x in xrange(room.x1, room.x2 + 1):
      for y in xrange(room.y1, room.y2 + 1):
        self.__map[y][x].make_passable()

  def create_tunnel(self, c1, c2, x=None, y=None):
    assert x is not None or y is not None
    if x is not None:
      for y in xrange(min(c1, c2), max(c1, c2) + 1):
        self.__map[y][x].make_passable()
    else:
      for x in xrange(min(c1, c2), max(c1, c2) + 1):
        self.__map[y][x].make_passable()


class Tile(object):

  def __init__(self, blocked=False, blocks_sight=None):
    self.blocked = blocked
    if blocks_sight is None:
      blocks_sight = blocked
    self.blocks_sight = blocks_sight
    self.explored = False

  def make_passable(self):
    self.blocked = False
    self.blocks_sight = False


class Rect(object):

  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h

  def center(self):
    center_x = (self.x1 + self.x2) / 2
    center_y = (self.y1 + self.y2) / 2
    return center_x, center_y

  def intersects(self, rect):
    return (self.x1 <= rect.x2 and self.x2 >= rect.x1 and
            self.y1 <= rect.y2 and self.y2 >= rect.y1)
