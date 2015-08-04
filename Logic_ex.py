import random  # For randomize
from copy import copy

__author__ = 'mkrooted'  # Me
combined_armor_hp = lambda armor1, armor2: armor1.Hp + armor2.Hp if armor1.Hp + armor2.Hp <= 100 else 100


class Gun:
    def __init__(self, name: str, damage=5, fire_range=1, ammo=10, clipsize=5, dmg_spread=0.5):
        self.Dmg_spread = dmg_spread  # Damage spread
        self.Name = name  # Weapon name
        self.Damage = damage  # Avg damage
        self.Range = fire_range  # Fire range
        self.Ammo = ammo  # Starting ammo
        self.clipSize = clipsize  # Clipsize
        self.Ammo -= self.clipSize  # Reload while initializing
        self.Clip = self.clipSize  #

    def __str__(self):
        return self.Name

    # Returns random damage + or - damage*ratio
    def fire(self):
        self.Ammo -= 1
        ratio = random.uniform(-1 * self.Dmg_spread, self.Dmg_spread)
        result = self.Damage + self.Damage * ratio
        return result

    # Ammo+clip; Ammo-clipsize; Clip=clipsize;
    def reload(self):
        self.Ammo += self.Clip
        self.Ammo -= self.clipSize
        self.Clip = self.clipSize


class Armor:
    def __init__(self, name: str, hp=100, resistance: float=0.5):
        self.Name = name  # Armor name
        self.Resistance = resistance  # Resistance ratio
        self.Hp = hp  # Armor HP

    # Takes damage and returns damage*ratio
    def resist(self, damage):
        self.Hp -= damage
        return damage * self.Resistance

    # Return HP if alive; Return False if not
    def alive(self):
        if self.Hp > 0:
            return self.Hp
        else:
            return False

    def get_name(self):
        return self.Name


class Character:
    def __init__(self, name: str, x, y, hp=100, armor: Armor=None, inventory=None, ch_type="Player"):
        """

        :type armor: Armor
        """
        if inventory is None:
            self.Inventory = []
        else:
            self.Inventory = inventory
        self.Armor = armor
        self.Hp = hp
        self.Name = name
        self.Type = ch_type
        self.Pos = [x, y]
        self.Current_Gun = None
        self.Current_Armor = None

    # Using armor (if available) and takes damage
    def damaged(self, damage):
        if self.Armor is not None:
            self.Hp -= self.Armor.resist(damage)
        else:
            self.Hp -= damage
        if not self.Armor.alive():
            self.Armor = None

    # Return HP if alive; Return False if not
    def alive(self):
        if self.Hp > 0:
            return self.Hp
        else:
            return False

    # Return True if current tile has item
    def item_available(self, world):
        if world.area[self.Pos[1]][self.Pos[0]].Item is not None:
            return True
        else:
            return False

    def show_item_available(self, world):
        if self.item_available(world):
            return world.area[self.Pos[1]][self.Pos[0]].Item
        else:
            return None

    # Pop all items from tile you are standing on and appends to self.Inventory. If armor - wear it
    def take(self, world):
        if self.item_available(world):
            if isinstance(world.area[self.Pos[1]][self.Pos[0]].Item[0], Armor):
                i = world.area[self.Pos[1]][self.Pos[0]].Item[0]
                if self.Armor is None:
                    self.Armor = world.area[self.Pos[1]][self.Pos[0]].take_item()
                else:
                    if self.Armor is not None and i.Resistance > self.Armor.Resistance:
                        self.Armor = world.area[self.Pos[1]][self.Pos[0]].take_item()
                    elif self.Armor is not None and i.Resistance == self.Armor.Resistance and i.Hp > self.Armor.Hp:
                        self.Armor.Hp += i.Hp
                        world.area[self.Pos[1]][self.Pos[0]].take_item()
            else:
                self.Inventory.append(world.area[self.Pos[1]][self.Pos[0]].take_item())

    # target position in tuple (x, y) format
    def near(self, target_pos, distance=1):
        x_range = range(self.Pos[0] - distance, self.Pos[0] + distance)
        y_range = range(self.Pos[1] - distance, self.Pos[1] + distance)
        if target_pos[0] in x_range and target_pos[1] in y_range:
            return True
        else:
            return False

    def fov(self, direction, distance, world):
        distance_right = distance_left = distance_down = distance_up = distance
        # Optimize distance to prevent index going out of list
        # Optimize X
        if self.Pos[0] - distance < 0:
            distance_left = distance - abs(self.Pos[0] - distance)
        elif self.Pos[0] + distance > world.X:
            distance_right = distance - (self.Pos[0] + distance) - world.X
        # Optimize Y
        if self.Pos[1] - distance < 0:
            distance_up = distance - abs(self.Pos[0] - distance)
        elif self.Pos[1] + distance > world.X:
            distance_down = distance - (self.Pos[1] + distance) - world.Y
        distances = {"up": distance_up, "down": distance_down, "left": distance_left, "right": distance_right}
        fov = []
        counter = -1
        if direction == "up":
            for i in range(self.Pos[1], self.Pos[1] - distances["up"]):
                counter += 1
                for ii in range(self.Pos[0] - distances["left"] + counter, self.Pos[0] + distances["right"] - counter):
                    fov.append((ii, i))
        elif direction == "down":
            for i in range(self.Pos[1], self.Pos[1] + distances["down"]):
                counter += 1
                for ii in range(self.Pos[0] - distances["left"] + counter, self.Pos[0] + distances["right"] - counter):
                    fov.append((ii, i))
        elif direction == "left":
            for i in range(self.Pos[0], self.Pos[0] - distances["left"]):
                counter += 1
                for ii in range(self.Pos[1] - distances["up"] + counter, self.Pos[1] + distances["down"] - counter):
                    fov.append((ii, i))
        elif direction == "left":
            for i in range(self.Pos[0], self.Pos[0] + distances["right"]):
                counter += 1
                for ii in range(self.Pos[1] - distances["up"] + counter, self.Pos[1] + distances["down"] - counter):
                    fov.append((ii, i))
        return fov

    def get_armor_name(self):
        """
        :rtype : str
        """
        return self.Armor.get_name()

    def nearest(self, distance_or_fov, entity_list: dict, ch_type="Hostile"):
        """
        :type distance_or_fov: int or list
        """
        nearest = (-1, -1)
        if type(distance_or_fov) is int:
            distance = distance_or_fov
            are_near = []
            for i in entity_list.keys():
                if self.near(i, distance) and entity_list[i].Type in ch_type:
                    are_near.append(i)
            for i in are_near:
                if abs(i[0] - self.Pos[0]) <= nearest[0] and abs(i[1] - self.Pos[1]) <= nearest[1]:
                    nearest = i
        elif type(distance_or_fov) is list:
            fov = distance_or_fov
            in_fov = []
            for i in entity_list.keys():
                if i in fov and entity_list[i].Type in ch_type:
                    in_fov.append(i)
            for i in in_fov:
                if abs(i[0] - self.Pos[0]) <= nearest[0] and abs(i[1] - self.Pos[1]) <= nearest[1]:
                    nearest = i
        lmb_return = lambda tuple_: None if tuple_[0] == tuple_[1] == -1 else tuple_
        return lmb_return(nearest)

    # if near return weapon's damage
    def fire(self, enemy_pos, gun_name=None):
        if gun_name is None:
            gun_name = self.Current_Gun
        obj = self.gun_by_name(gun_name)
        if obj.Clip > 0 and self.near(enemy_pos, obj.Range):
            return obj.fire()
        elif obj.Clip <= 0:
            return "Ammo"
        elif not self.near(enemy_pos, obj.Range):
            return "Far"

    def change_gun(self, step=1, flag=None):
        """
        :type flag: None or int
        """
        for i in self.Inventory:
            if isinstance(i, Gun):  # if i is Gun
                if flag is None and i == self.Current_Gun:
                    flag = 0
                if flag is not None and flag < step:
                    self.Current_Gun = i
                    flag += 1

    def take_any_gun(self):
        for i in self.Inventory:
            if isinstance(i, Gun):
                self.Current_Gun = i
                return i
            else:
                return None

    def gun_by_name(self, name):
        for i in self.Inventory:
            if i is Gun and i.Name == name:
                return i
        return None

    def update(self):
        if self.Current_Gun is not None:
            self.Current_Gun = self.take_any_gun()


class Tile:
    # Achtung equals Tile's damage
    # If Tile don't deal damage Achtung = False
    def __init__(self, legend, name, destroyable=False, walkable=False, achtung=False, hp=None, item: list=None):
        """:type achtung: bool or int"""
        self.Legend = legend
        self.Item = item
        self.Achtung = achtung
        self.Hp = hp
        self.Walkable = walkable
        self.Destroyable = destroyable
        self.Name = name

    # Take damage
    def damaged(self, damage):
        if self.Destroyable:
            self.Hp -= damage

    # Hit character; Return damage
    def hit(self):
        if self.Achtung is not False:
            return self.Achtung

    # Pop item from Tile.item
    def take_item(self):
        item = self.Item.pop(0)
        if not self.Item:
            self.Legend = " "
        return item

# Items' declarations
BFG = Gun("BFG10K", 25, 10, 12, 4, 1)
NRGArmor = Armor("Energy armor", 100, 1)

# Tiles' declarations
Tile_Wall = Tile("#", "Wall")  # Not Walkable, indestructible
Tile_Floor = Tile(" ", "Floor", False, True)  # Empty
Tile_Laser = Tile("X", "Laser", True, True, 25, 25)  # Attacking, walkable, destructible
Tile_Glass = Tile("@", "Glass", True, False, False, 50)  # Not walkable, destructible
Dropped_BFG = Tile("B", "Dropped BFG10K", False, True, False, None, [BFG])  # Test
Dropped_Armor = Tile("A", "Dropped Energy Armor", False, True, False, None, [NRGArmor])  # Test


class World:
    def __init__(self, x, y, tile: Tile=Tile_Floor, player_pos=None):
        if not player_pos:
            player_pos = [1, 1]
        self.Entity_list = {}
        self.X = x  # Max X
        self.Y = y  # Max Y
        self.PPos = player_pos  # Player position, syncs with Player object
        self.area = []  # Tiles storage
        self.Map = []  # Visualisation of self.area
        a = []  # Temporal
        for i in range(0, self.X + 1):  # Creating line of "tile"s
            a.append(tile)
        for i in range(0, self.Y + 1):  # Creating 2D array of those lines
            self.area.append(copy(a))

    # side values: "right", "down"
    # Need to be Fixed!!! (Don't work)
    def new_line(self, side, tile: Tile=Tile_Floor):
        if side == "down":
            a = []
            for i in range(0, self.X + 1):
                a.append(tile)
            self.area.append(a)
            self.Y += 1
        elif side == "right":
            for i in self.area:
                i.append(tile)
            self.X += 1

    # Fills area with specified tile
    def fill(self, x1, y1, x2, y2, tile: Tile):
        for i in range(y1, y2 + 1):
            for ii in range(x1, x2 + 1):
                self.area[i][ii] = tile

    # Creates "Walls" of specified tiles
    def walls(self, x1, y1, x2, y2, tile: Tile=Tile_Wall):
        for i in range(x1, x2 + 1):
            self.area[y1][i] = tile
            self.area[y2][i] = tile
        for i in range(y1, y2 + 1):
            self.area[i][x1] = tile
            self.area[i][x2] = tile

    # Changes tile in specified position
    def dot(self, x, y, tile: Tile):
        self.area[y][x] = tile

    # updates self.map
    def map_update(self, player: Character):
        self.Map = []
        a = []
        o = -1
        for i in range(0, self.Y + 1):
            o += 1
            a.clear()
            for ii in range(0, self.X + 1):
                if (i, ii) != (player.Pos[1], player.Pos[0]):
                    a.append(self.area[i][ii].Legend)
                else:
                    a.append('M')
            self.Map.append(copy(a))

    # move player by x steps in x direction
    # direction values: up, down, left, right
    def player_shift(self, player: Character, direction, steps=1):
        if direction == "left" and (self.PPos[0] - steps) >= 0 and self.area[self.PPos[1]][
                    self.PPos[0] - steps].Walkable:
            self.PPos[0] -= steps
            player.Pos[0] = self.PPos[0]
        elif direction == "right" and self.PPos[0] + steps <= self.X and self.area[self.PPos[1]][
                    self.PPos[0] + steps].Walkable:
            self.PPos[0] += steps
            player.Pos[0] = self.PPos[0]
        elif direction == "up" and (self.PPos[1] - steps) >= 0 and self.area[self.PPos[1] - steps][
            self.PPos[0]].Walkable:
            self.PPos[1] -= steps
            player.Pos[1] = self.PPos[1]
        elif direction == "down" and self.PPos[1] + steps <= self.Y and self.area[self.PPos[1] + steps][
            self.PPos[0]].Walkable:
            self.PPos[1] += steps
            player.Pos[1] = self.PPos[1]

    def entity_update(self):
        for i in self.area:
            for ii in i:
                if ii.Hp is not None:
                    self.add_entity((ii.X, ii.Y), ii)

    def add_entity(self, location, obj):
        self.Entity_list[location] = obj

    def edit_entity(self, location=None, obj=None):
        if location is not None or obj is not None:
            self.del_entity(location, obj)
            self.add_entity(location, obj)

    def del_entity(self, location=None, obj=None):
        if location is None and obj is None:
            for i in self.Entity_list.keys():
                del self.Entity_list[i]
        elif location is None:
            for i in self.Entity_list.items():
                if i[1] == obj:
                    del self.Entity_list[i[0]]
        else:
            del self.Entity_list[location]


def show_world(obj: World, player: Character):
    obj.map_update(player)
    a = []
    for i in range(0, obj.X + 1):  # Numbers on X-axis
        a.append(str(i))
    print("   ", str(a))
    a = -1
    for i in obj.Map:  # Map with Y-axis
        a += 1
        print(a, " ", i)
