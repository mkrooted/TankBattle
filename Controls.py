from msvcrt import getwch
import os
from Logic_ex import Tile_Laser, Tile_Wall, Tile_Floor, Tile_Glass, Gun, show_world, Character, World, Armor


def attack(pl: Character, world: World, target):
    damage = pl.fire(target, pl.Current_Gun if pl.Current_Gun is not None else pl.take_any_gun())


def statusbar_generate(pl: Character):
    statusbar = "[HP: {0}][Location{1}][Weapon: {2}][Armor: {3}][Ammo: {4}][Press \'h\' for help]".format(
        str(pl.Hp),
        str(pl.Pos),
        str(pl.Current_Gun.Name if pl.Current_Gun is not None else pl.take_any_gun()),
        str(pl.Armor.Name if pl.Armor is not None else None),
        str(pl.Current_Gun.Ammo if pl.Current_Armor is not None else None)
    )
    return statusbar


def itembar_generate(pl: Character, world: World):
    statusbar = ""
    if pl.item_available(world):
        for i in pl.show_item_available(world):
            statusbar += i.Name + '\n'
    return statusbar


def normal(world: World, pl: Character):
    os.system('setterm -cursor off')
    print()
    direction = "down"
    flag = "none"
    while flag == "none":
        os.system('cls')
        pl.update()
        show_world(world, pl)
        print(statusbar_generate(pl))
        print(itembar_generate(pl, world))
        ch = getwch()
        if ch == "w" or ch == "W":
            world.player_shift(pl, "up")
        elif ch == "a" or ch == "A":
            world.player_shift(pl, "left")
        elif ch == "s" or ch == "S":
            world.player_shift(pl, "down")
        elif ch == "d" or ch == "D":
            world.player_shift(pl, "right")
        elif ch == "e" or ch == "E":
            if pl.item_available(world):
                pl.take(world)
            elif pl.nearest(pl.fov(direction, pl.Current_Gun.Range, world), world.Entity_list):
                attack(pl, world, pl.nearest(pl.fov(direction, pl.Current_Gun.Range, world), world.Entity_list,
                                             ["Hostile", "Tile"]))
        elif ch == "`":
            print("GoodBye!")
            flag = "ExitKey"
