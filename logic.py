__author__ = 'mkrooted'
from Logic_ex import World

class Tank:
    Global_Id = 0

    def __init__(self, name, hp=100, weapon=None, abilities=None):
        self.Global_Id += 1
        self.Id = self.Global_Id
        self.Name = name
        self.Hp = hp
        self.Weapon = weapon
        if abilities is None:
            self.Abilities = {}
        else:
            self.Abilities = abilities
