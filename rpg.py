
import json
import os
import random
import time

CLASSES = {
    "1": {"name":"Warrior","hp":180,"mana":45,"attack":22,"defense":14,"crit":.08,"skills":[("Slash",8,1.6),("Shield Bash",12,1.25),("Rage",15,1),("Earthquake",25,2.8)]},
    "2": {"name":"Mage","hp":115,"mana":120,"attack":27,"defense":5,"crit":.12,"skills":[("Fireball",12,1.7),("Ice Blast",18,2),("Thunder Strike",25,2.5),("Meteor",40,3.8)]},
    "3": {"name":"Archer","hp":135,"mana":75,"attack":21,"defense":9,"crit":.20,"skills":[("Multi Shot",10,1.5),("Poison Arrow",15,1.8),("Explosive Arrow",24,2.5),("Sniper Shot",32,3.4)]},
    "4": {"name":"Assassin","hp":105,"mana":80,"attack":29,"defense":5,"crit":.28,"skills":[("Backstab",10,1.9),("Smoke Bomb",15,1),("Shadow Strike",23,2.7),("Instant Kill",40,4.5)]}
}
RARITIES = {"Common":(1.0,0,1),"Uncommon":(1.1,.02,2),"Rare":(1.3,.05,5),"Super Rare":(1.5,.08,10),"Epic":(1.8,.12,20),"Mythical":(2.2,.18,35),"Legendary":(2.8,.25,50)}
WEAPONS = [
("Wooden Sword","Common",5,20,1),("Rusty Axe","Common",6,22,1),("Training Bow","Common",5,20,1),("Apprentice Wand","Common",6,24,1),
("Iron Sword","Uncommon",10,55,3),("Steel Axe","Rare",14,110,6),("Long Bow","Rare",12,100,6),("Crystal Blade","Super Rare",19,220,10),
("Shadow Dagger","Super Rare",20,240,10),("Lightning Bow","Super Rare",18,230,10),("Flame Sword","Epic",25,400,15),("Ice Spear","Epic",24,390,15),
("Thunder Hammer","Epic",28,450,18),("Phoenix Blade","Mythical",34,750,25),("Demon Slayer","Mythical",37,850,30),("Celestial Staff","Mythical",35,820,30),
("Dragon King's Sword","Legendary",45,1400,40),("Blade of Eternity","Legendary",48,1600,45),("Bow of the Gods","Legendary",43,1500,40),("Void Reaper","Legendary",50,1800,50)]
ARMORS = [
("Cloth Tunic","Common",3,5,0,0,25),("Leather Vest","Common",5,10,0,0,35),("Iron Armor","Uncommon",8,20,0,.01,70),
("Ranger's Garb","Rare",9,15,5,.03,120),("Mageweave Robe","Rare",5,10,20,.02,125),("Knight Plate","Super Rare",15,45,0,.05,240),
("Shadow Suit","Super Rare",10,20,10,.08,260),("Frostguard Mail","Epic",18,60,10,.08,430),("Stormcaller Robes","Epic",10,20,45,.06,450),
("Phoenix Armor","Mythical",23,100,25,.12,800),("Demon Lord Plate","Legendary",30,150,20,.18,1400),("Celestial Aegis","Legendary",27,120,50,.20,1550)]
POTIONS = [
("Small Health Potion","health",50,20),("Medium Health Potion","health",100,40),("Large Health Potion","health",250,80),("Giant Health Potion","health",500,150),("Ultimate Health Potion","health",-1,250),
("Small Mana Potion","mana",30,20),("Medium Mana Potion","mana",75,45),("Large Mana Potion","mana",150,90),("Giant Mana Potion","mana",300,160),("Ultimate Mana Potion","mana",-1,250),
("Balanced Tonic","mixed",60,65),("Traveler's Elixir","mixed",120,120),("Warrior's Draught","attack",8,75),("Guardian's Brew","defense",8,75),("Eagle Eye Elixir","crit",.15,90)]
ENEMIES = [(n,l) for l,names in [(1,["Goblin","Wolf","Slime","Zombie","Skeleton"]),(11,["Orc","Bandit","Troll","Dark Archer","Giant Spider"]),(21,["Vampire","Werewolf","Necromancer","Ice Golem","Fire Demon"]),(31,["Sand Wraith","Scorpion Queen","Desert Raider"]),(41,["Cursed Knight","Grave Witch","Ruins Sentinel"]),(51,["Lava Beast","Ashen Drake","Magma Spider"]),(61,["Frost Wolf","Glacier Ogre","Ice Witch"]),(71,["Sky Harpy","Cloud Serpent"]),(81,["Storm Elemental","Shadow Knight"]),(91,["Doom Hound","Demon Acolyte"])] for n in names]
BOSSES = {10:"Goblin King",20:"Forest Guardian",30:"Ancient Golem",40:"Vampire Lord",50:"Dragon Rider",60:"Demon General",70:"Ice Titan",80:"Shadow Emperor",90:"Celestial Dragon",100:"Ancient Demon King"}
REGIONS = ["Village","Forest","Cave","Desert","Ruins","Castle","Volcano","Frozen Mountain","Sky Temple","Demon Realm"]


class Player:
    def __init__(self,name,class_key):
        c=CLASSES[class_key]; self.name=name; self.player_class=c["name"]; self.level=1; self.exp=0; self.exp_next=100
        self.max_hp=c["hp"]; self.hp=self.max_hp; self.max_mana=c["mana"]; self.mana=self.max_mana
        self.attack=c["attack"]; self.defense=c["defense"]; self.crit=c["crit"]; self.gold=100
        self.weapon={"name":"Wooden Sword","rank":"Common","damage":5,"crit_bonus":0,"price":20,"required_level":1}
        self.armor=None; self.inventory=[]; self.potions={"Small Health Potion":2,"Small Mana Potion":1}
        self.bosses=[]; self.enemies=0; self.weapons=["Wooden Sword"]; self.rare_items=[]; self.region=0
    def gain_exp(self,n):
        self.exp+=n; print(f"You gained {n} EXP.")
        # The next boss gates progression: level 10 must be cleared before level 11, etc.
        level_cap = min(100, (len(self.bosses) + 1) * 10)
        while self.exp>=self.exp_next and self.level<level_cap:
            self.exp-=self.exp_next; self.level+=1; self.exp_next=int(self.exp_next*1.18)
            self.max_hp+=12; self.max_mana+=6; self.attack+=3; self.defense+=2; self.hp=self.max_hp; self.mana=self.max_mana
            print(f"LEVEL UP! You reached level {self.level}; your stats increased.")
            if self.level%5==0: print("Milestone: class skills become stronger!")
        if self.level>=100: self.exp=0
    def stats(self):
        print(f"\n{self.name} the {self.player_class} | Level {self.level} | EXP {self.exp}/{self.exp_next}")
        print(f"HP {self.hp}/{self.max_hp} | Mana {self.mana}/{self.max_mana} | Attack {self.attack+self.weapon['damage']} | Defense {self.defense+(self.armor['defense'] if self.armor else 0)}")
        print(f"Critical chance {100*(self.crit+self.weapon.get('crit_bonus',0)):.1f}% | Gold {self.gold}")
        print(f"Weapon: {self.weapon['name']} | Armor: {self.armor['name'] if self.armor else 'None'}")
        print(f"Enemies defeated: {self.enemies} | Bosses defeated: {len(self.bosses)}")
    def to_dict(self): return self.__dict__
    @classmethod
    def from_dict(cls,d):
        key=next(k for k,v in CLASSES.items() if v["name"]==d["player_class"]); p=cls(d["name"],key); p.__dict__.update(d); return p


import random

def enemy_for(level,boss=False):
    if boss:
        name=BOSSES[level]; hp=280+level*42
        return {"name":name,"level":level,"boss":True,"hp":hp,"max_hp":hp,"attack":18+level*3,"defense":5+level,"exp":180+level*18,"gold":100+level*12,"turn":0}
    options=[x for x in ENEMIES if x[1]<=level]; name=random.choice(options)[0]; hp=35+level*12
    return {"name":name,"level":level,"boss":False,"hp":hp,"max_hp":hp,"attack":7+level*2,"defense":level//3,"exp":25+level*8,"gold":random.randint(8,20)+level*3,"turn":0}

def potion_menu(p):
    choices=[(n,c) for n,c in p.potions.items() if c>0]
    if not choices: print("No potions available."); return False
    for i,(n,c) in enumerate(choices,1): print(f"{i}. {n} x{c}")
    s=input("Potion number (0 cancel): ").strip()
    if s=="0": return False
    if not s.isdigit() or not 1<=int(s)<=len(choices): print("Invalid choice."); return False
    name=choices[int(s)-1][0]; _,kind,amount,_=next(x for x in POTIONS if x[0]==name)
    if kind=="health":
        v=p.max_hp-p.hp if amount==-1 else min(amount,p.max_hp-p.hp); p.hp+=v; print(f"Restored {v} HP.")
    elif kind=="mana":
        v=p.max_mana-p.mana if amount==-1 else min(amount,p.max_mana-p.mana); p.mana+=v; print(f"Restored {v} Mana.")
    elif kind=="mixed":
        p.hp+=min(amount,p.max_hp-p.hp); p.mana+=min(amount,p.max_mana-p.mana); print("Restored HP and Mana.")
    else:
        p.__dict__.setdefault("buffs",{})[kind]=amount; p.buffs[kind+"_turns"]=3; print(f"{kind.title()} buff active for 3 turns.")
    p.potions[name]-=1; return True

def inventory(p):
    while True:
        print("\n--- INVENTORY ---")
        print("Weapon:",p.weapon["name"],"| Armor:",p.armor["name"] if p.armor else "None")
        for i,it in enumerate(p.inventory,1): print(f"{i}. {it['rank']} {it['name']} ({it['kind']}) - {it['price']} gold")
        print("1 Equip  2 Sell  3 Drop  4 Unequip armor  0 Back")
        c=input("Choose: ").strip()
        if c=="0": return
        if c=="4":
            if p.armor: p.inventory.append(p.armor); p.armor=None; print("Armor unequipped.")
            else: print("No armor equipped.")
            continue
        if c not in ("1","2","3") or not p.inventory: print("Invalid choice or inventory empty."); continue
        s=input("Item number: ").strip()
        if not s.isdigit() or not 1<=int(s)<=len(p.inventory): print("Invalid item."); continue
        it=p.inventory.pop(int(s)-1)
        if c=="1":
            if it["kind"]=="weapon":
                if it["required_level"]>p.level: print("Level too low."); p.inventory.append(it)
                else: p.weapon=it; print("Equipped",it["name"])
            elif it["kind"]=="armor":
                if p.armor: p.inventory.append(p.armor)
                p.armor=it; print("Equipped",it["name"])
        elif c=="2":
            gold=max(1,it["price"]//2); p.gold+=gold; print(f"Sold for {gold} gold.")
        else: print("Dropped",it["name"])

def shop(p):
    while True:
        print(f"\nVillage Shop | Gold: {p.gold}\n1 Weapons  2 Armor  3 Potions  4 Sell gear  0 Exit")
        c=input("Choose: ").strip()
        if c=="0": return
        if c=="1":
            stock=[x for x in WEAPONS if x[4]<=p.level]
            for i,(n,r,d,price,req) in enumerate(stock,1): print(f"{i}. {n} [{r}] damage {d} - {price}g")
            s=input("Number (0 cancel): ").strip()
            if s=="0": continue
            if not s.isdigit() or not 1<=int(s)<=len(stock): print("Invalid."); continue
            n,r,d,price,req=stock[int(s)-1]
            if p.gold<price: print("Not enough gold."); continue
            p.gold-=price; p.inventory.append({"kind":"weapon","name":n,"rank":r,"damage":d,"crit_bonus":RARITIES[r][1],"price":price,"required_level":req}); print("Purchased",n)
        elif c=="2":
            for i,(n,r,de,hp,ma,cr,price) in enumerate(ARMORS,1): print(f"{i}. {n} [{r}] DEF+{de} HP+{hp} Mana+{ma} - {price}g")
            s=input("Number (0 cancel): ").strip()
            if s=="0": continue
            if not s.isdigit() or not 1<=int(s)<=len(ARMORS): print("Invalid."); continue
            n,r,de,hp,ma,cr,price=ARMORS[int(s)-1]
            if p.gold<price: print("Not enough gold."); continue
            p.gold-=price; p.inventory.append({"kind":"armor","name":n,"rank":r,"defense":de,"hp_bonus":hp,"mana_bonus":ma,"crit_resistance":cr,"price":price,"required_level":1}); print("Purchased",n)
        elif c=="3":
            for i,(n,k,a,price) in enumerate(POTIONS,1): print(f"{i}. {n} - {price}g")
            s=input("Number (0 cancel): ").strip()
            if s=="0": continue
            if not s.isdigit() or not 1<=int(s)<=len(POTIONS): print("Invalid."); continue
            n,k,a,price=POTIONS[int(s)-1]
            if p.gold<price: print("Not enough gold."); continue
            p.gold-=price; p.potions[n]=p.potions.get(n,0)+1; print("Purchased",n)
        elif c=="4": inventory(p)
        else: print("Choose a valid option.")

def loot(p,e):
    p.gold+=e["gold"]; print(f"You found {e['gold']} gold.")
    if random.random() < (.85 if e["boss"] else .4):
        if random.random()<.45:
            n=random.choice(POTIONS)[0]; p.potions[n]=p.potions.get(n,0)+1; print("Loot potion:",n)
        else:
            rarity=random.choices(list(RARITIES),weights=[50,25,15,6,3,.9,.1])[0]
            opts=[w for w in WEAPONS if w[1]==rarity and w[4]<=p.level]
            if opts:
                n,r,d,price,req=random.choice(opts); it={"kind":"weapon","name":n,"rank":r,"damage":d,"crit_bonus":RARITIES[r][1],"price":price,"required_level":req}
                p.inventory.append(it); p.weapons.append(n)
                if r not in ("Common","Uncommon"): p.rare_items.append(n)
                print(f"Loot: {r} {n}")
    if e["boss"]:
        opts=[w for w in WEAPONS if w[1] in ("Rare","Super Rare","Epic","Mythical","Legendary") and w[4]<=p.level]
        if opts:
            n,r,d,price,req=random.choice(opts); p.inventory.append({"kind":"weapon","name":n,"rank":r,"damage":d,"crit_bonus":RARITIES[r][1],"price":price,"required_level":req})
            p.weapons.append(n); p.rare_items.append(n); print("Guaranteed boss reward:",r,n)

def battle(p,e):
    print(f"\n{'BOSS' if e['boss'] else 'Enemy'}: {e['name']} | HP {e['hp']}")
    defending=False; stunned=False
    while p.hp>0 and e["hp"]>0:
        print(f"\n{p.name} HP {p.hp}/{p.max_hp} Mana {p.mana}/{p.max_mana} | {e['name']} HP {e['hp']}/{e['max_hp']}")
        print("1 Attack  2 Skills  3 Heal  4 Potion  5 Defend  6 Inventory  7 Stats  8 Run")
        c=input("Your turn: ").strip()
        if c not in list("12345678"): print("Enter 1-8."); continue
        enemy_turn=True
        if c=="1":
            buffs=p.__dict__.get("buffs", {})
            dmg=max(1,p.attack+p.weapon["damage"]+buffs.get("attack",0)-e["defense"])
            if random.random()<min(.85,p.crit+p.weapon.get("crit_bonus",0)+buffs.get("crit",0)): dmg=int(dmg*1.8); print("CRITICAL HIT!")
            e["hp"]-=dmg; print(f"You dealt {dmg} damage.")
        elif c=="2":
            key=next(k for k,v in CLASSES.items() if v["name"]==p.player_class); skills=CLASSES[key]["skills"]
            for i,(n,cost,power) in enumerate(skills,1): print(f"{i}. {n} (mana {cost})")
            s=input("Skill number (0 cancel): ").strip()
            if s=="0": enemy_turn=False
            elif not s.isdigit() or not 1<=int(s)<=len(skills): print("Invalid skill."); enemy_turn=False
            else:
                n,cost,power=skills[int(s)-1]
                if p.mana<cost: print("Not enough mana."); enemy_turn=False
                else:
                    p.mana-=cost
                    if n in ("Rage","Smoke Bomb"):
                        p.__dict__.setdefault("buffs",{})["attack" if n=="Rage" else "evade"]=12 if n=="Rage" else 1
                        p.buffs["attack_turns" if n=="Rage" else "evade_turns"]=3 if n=="Rage" else 1
                        print(n,"activated.")
                    else:
                        buffs=p.__dict__.get("buffs", {})
                        dmg=max(1,int((p.attack+p.weapon["damage"]+buffs.get("attack",0))*power-e["defense"]))
                        if n=="Instant Kill" and random.random()<.08: dmg=e["hp"]; print("INSTANT KILL!")
                        if n=="Shield Bash": stunned=True
                        e["hp"]-=dmg; print(f"{n} dealt {dmg} damage.")
        elif c=="3":
            h=min(35+p.level*2,p.max_hp-p.hp); p.hp+=h; print("Recovered",h,"HP.")
        elif c=="4": enemy_turn=not (potion_menu(p) is False)
        elif c=="5": defending=True; print("Next incoming attack reduced by 50%.")
        elif c=="6": inventory(p); enemy_turn=False
        elif c=="7": p.stats(); enemy_turn=False
        elif c=="8":
            if e["boss"]: print("You cannot run from a boss."); enemy_turn=False
            elif random.random()<.65: print("Escaped."); return "run"
            else: print("Escape failed.")
        if e["hp"]<=0: break
        if enemy_turn:
            e["turn"]+=1
            if e["boss"] and e["hp"] < e["max_hp"] * 0.55 and random.random() < 0.12:
                heal = min(int(e["max_hp"] * 0.08), e["max_hp"] - e["hp"])
                e["hp"] += heal
                print(f"{e['name']} uses dark healing and restores {heal} HP!")
            elif stunned: print("Enemy stunned and loses its turn."); stunned=False
            elif p.__dict__.get("buffs",{}).get("evade"): print("You evaded the attack."); p.buffs.pop("evade",None)
            else:
                buffs=p.__dict__.get("buffs", {})
                dmg=max(1,e["attack"]-(p.defense+(p.armor["defense"] if p.armor else 0)+buffs.get("defense",0)))
                if defending: dmg=max(1,dmg//2)
                if e["boss"] and e["turn"]%3==0: dmg=int(dmg*1.7); print("BOSS SPECIAL ATTACK!")
                if random.random()<.08: dmg=int(dmg*1.5); print("Enemy critical hit!")
                p.hp-=dmg; print(f"{e['name']} dealt {dmg} damage.")
            defending=False
            buffs=p.__dict__.get("buffs", {})
            for key in ("attack", "defense", "crit", "evade"):
                turns_key=key+"_turns"
                if turns_key in buffs:
                    buffs[turns_key]-=1
                    if buffs[turns_key]<=0:
                        buffs.pop(turns_key,None); buffs.pop(key,None)
    if p.hp<=0: print("You have fallen in battle."); return "dead"
    print("Victory!",e["name"],"defeated."); p.enemies+=not e["boss"]
    if e["boss"]: p.bosses.append(e["name"])
    p.gain_exp(e["exp"]); loot(p,e); return "win"


import json, os, time
SAVE="eldoria_save.json"

def save(p):
    try:
        with open(SAVE,"w",encoding="utf-8") as f: json.dump(p.to_dict(),f,indent=2)
        print("Game saved.")
    except (OSError,TypeError) as e: print("Could not save:",e)

def load():
    if not os.path.exists(SAVE): print("No save file found."); return None
    try:
        with open(SAVE,encoding="utf-8") as f: p=Player.from_dict(json.load(f))
        print("Welcome back,",p.name); return p
    except (OSError,ValueError,KeyError,TypeError,StopIteration) as e: print("Could not load save:",e); return None

def new_player():
    name=input("Enter player name: ").strip()
    while not name: print("Name cannot be empty."); name=input("Enter player name: ").strip()
    print("Choose class:")
    for k,v in CLASSES.items(): print(f"{k}. {v['name']} (HP {v['hp']}, Mana {v['mana']}, Attack {v['attack']}, Defense {v['defense']})")
    while True:
        k=input("Class (1-4): ").strip()
        if k in CLASSES: return Player(name,k)
        print("Please choose 1, 2, 3, or 4.")

def instructions():
    print("""
LEGENDS OF THE FORGOTTEN REALM
Create a hero, explore, fight enemies, earn EXP and gold, collect gear,
buy potions, and defeat bosses every 10 levels. Combat actions:
1 Attack, 2 Skills, 3 Heal, 4 Potion, 5 Defend, 6 Inventory,
7 Stats, 8 Run (not allowed against bosses). Defend halves the next hit.
Use the shop to buy equipment. Save from the exploration menu.
The final goal is Level 100 and the Ancient Demon King.
""")

def victory(p,started):
    seconds=int(time.time()-started)
    print("\n=== ELDORIA SAVED: VICTORY ===")
    print(f"Player: {p.name} | Final level: {p.level} | Gold: {p.gold}")
    print(f"Bosses: {len(p.bosses)} | Enemies: {p.enemies} | Weapons collected: {len(set(p.weapons))}")
    print(f"Rare items found: {len(set(p.rare_items))} | Play time: {seconds//60}m {seconds%60}s")
    print("Final score:",p.level*100+p.gold+p.enemies*20+len(p.bosses)*500)

def play(p):
    started=time.time()
    while True:
        print(f"\n=== {REGIONS[p.region]} | Level {p.level} ===")
        print("1 Explore/fight  2 Shop  3 Inventory  4 Stats  5 Use potion  6 Save  7 Main menu")
        c=input("Choose: ").strip()
        if c=="1":
            # Boss at every tenth level; defeat it before moving beyond that level.
            cap=((p.level+9)//10)*10
            if p.level%10==0 and cap in BOSSES and BOSSES[cap] not in p.bosses: e=enemy_for(cap,True)
            elif p.level>=100 and BOSSES[100] not in p.bosses: e=enemy_for(100,True)
            else: e=enemy_for(p.level,False)
            result=battle(p,e)
            if result=="dead":
                print("\nGAME OVER\n1 Retry with a new hero  2 Load save  3 Exit")
                c=input("Choose: ").strip()
                if c=="1": return "new"
                if c=="2":
                    loaded=load()
                    if loaded: return play(loaded)
                return "menu"
            if result=="win" and e["boss"]:
                p.region=min(len(REGIONS)-1,p.region+1); print("Region unlocked:",REGIONS[p.region])
                if e["name"]==BOSSES[100]: victory(p,started); input("Press Enter..."); return "menu"
        elif c=="2": shop(p)
        elif c=="3": inventory(p)
        elif c=="4": p.stats()
        elif c=="5": potion_menu(p)
        elif c=="6": save(p)
        elif c=="7":
            if input("Save before leaving? (y/n): ").strip().lower() in ("y","yes"): save(p)
            return "menu"
        else: print("Please choose 1-7.")

def main():
    while True:
        print("\n====================================\n LEGENDS OF THE FORGOTTEN REALM\n====================================\n1 New Game\n2 Continue\n3 Instructions\n4 Exit")
        c=input("Choose: ").strip()
        if c=="1":
            result=play(new_player())
            if result=="new": continue
        elif c=="2":
            p=load()
            if p: play(p)
        elif c=="3": instructions()
        elif c=="4": print("Farewell, hero. May Eldoria remember your courage!"); break
        else: print("Please enter 1-4.")

main()
