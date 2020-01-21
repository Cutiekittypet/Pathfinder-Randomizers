import json
from os import path,chdir,listdir
import tkinter as tk
from random import randint
from string import capwords

# opens and loads a json file
def readjson(file_name):
    with open(file_name, 'r') as da_file:
        read_file = json.load(da_file)
    return read_file

# randomly grabs an item, weighted so weapon chance = armor chance = misc item chance
def rollItem():
    temp_int = 0
    temp_dict = {}
    for base in typ_tree_active:
        temp_dict[temp_int] = typ_tree_active[base]
        temp_int += 1
    item_list = temp_dict[randint(0, len(temp_dict)-1)]
    precise_item = item_list[randint(0, len(item_list)-1)]
    return precise_item

# randomly grabs a modifier, wastes a roll, or doubles a roll
def rollModifier():
    global rolls
    global current_modifiers
    global magic
    rolls -= 1
    roll = randint(0, 15)
    if roll < 3:
        return
    elif roll > 14:
        rolls += 2
        return
    else:
        mod = {}
        mod = mod_tree_active[randint(0, len(mod_tree_active)-1)]
        while mod['enchant'] > magic:
            mod = mod_tree_active[randint(0, len(mod_tree_active)-1)]
        modifiers.append(mod)
        current_modifiers += mod['enchant']
        return

# roll for and apply material
def applyMaterial(base_item):
    item_mat = mat_tree_active[randint(0, len(mat_tree_active)-1)]
    if base_item['equip_type'] == 'armor':
        if 'resistance' in item_mat:
            for resistance in item_mat['resistance']:
                if 'resistance' in base_item:
                    if resistance in base_item['resistance']:
                        base_item['resistance'][resistance] += item_mat['resistance'][resistance]
                    else:
                        base_item['resistance'][resistance] = item_mat['resistance'][resistance]
                else:
                    base_item['resistance'] = {}
                    base_item['resistance'][resistance] = item_mat['resistance'][resistance]
        if base_item['subtype'] == 'shield':
            base_item['bonus'] += item_mat['shield_mod']
            if base_item['bonus'] < 1:
                base_item['bonus'] = 1
        else:
            if 'prof' not in base_item:
                base_item['prof'] = 0
            base_item['check_penalty'] = item_mat['armor_check']
            base_item['prof'] += item_mat['armor_prof']
            base_item['max_dex'] = item_mat['max_dex'] - base_item['max_dex']
            base_item['spell_failure'] += item_mat['spell_failure']
            base_item['speed_penalty'] -= item_mat['speed_mod']
    if 'damage' in base_item:
        if item_mat['damage_up'] > 0:
            for each in range(item_mat['damage_up']):
                for damage in base_item['damage']:
                    base_item['damage'][damage] = upgradeDice(base_item['damage'][damage])
        elif item_mat['damage_up'] < 0:
            for each in range(-item_mat['damage_up']):
                for damage in base_item['damage']:
                    base_item['damage'][damage] = downgradeDice(base_item['damage'][damage])
    if 'special' not in base_item:
        base_item['special'] = []
    if 'special' in item_mat:
        for spec in item_mat['special']:
            if spec not in base_item['special']:
                base_item['special'].append(spec)
    if 'skill' in item_mat:
        for skill in item_mat['skill']:
            if 'skill' in base_item:
                if skill in base_item['skill']:
                    base_item['skill'][skill] += item_mat['skill'][skill]
                else:
                    base_item['skill'][skill] = item_mat['skill'][skill]
            else:
                base_item['skill'] = {}
                base_item['skill'][skill] = item_mat['skill'][skill]
    base_item['weight'] = round(base_item['weight'] * item_mat['weight_mod'], 4)
    base_item['price'] = round(base_item['price'] * item_mat['price_mod'], 4)
    base_item['name'] = item_mat['name'] + " " + base_item['name']

# damage table downgrade
def downgradeDice(dice):
    die_split = dice.split('d')
    die_split[0] = int(die_split[0])
    if len(die_split) == 1:
        return "1"
    die_split[1] = int(die_split[1])
    if die_split[0] == 1:
        if die_split[1] == 2:
            return "1"
        elif die_split[1] < 5:
            die_split[1] -= 1
        else:
            die_split[1] -= 2
    elif die_split[1] == 10:
        die_split[1] = 8
    else:
        if die_split[1] == 4:
            if die_split[0] % 2 == 0:
                die_split[0] = die_split[0] // 2
                die_split[1] = 8
            else:
                die_split[0] = (die_split[0] // 2) + 1
                die_split[1] = 6
        if die_split[1] == 12:
            die_split[0] = die_split[0] * 2
            die_split[1] = 6
        if die_split[1] == 8:
            if die_split[0] > 8 and die_split[0] % 4 != 0:
                die_split[0] = (die_split[0]//4)*4
            elif die_split[0] > 4 and die_split[0] % 2 != 0:
                die_split[0] -= 1
            else:
                die_split[1] = 6
        elif die_split[1] == 6:
            if die_split[0] > 8:
                if die_split[0] % 4 == 0:
                    die_split[0] = ((die_split[0]//4)-1)*4
                    die_split[1] = 8
                else:
                    die_split[0] = (die_split[0]//4)*4
            elif die_split[0] > 4:
                if die_split[0] % 2 == 0:
                    die_split[0] -= 2
                    die_split[1] = 8
                else:
                    die_split[0] -= 1
            elif die_split[0] == 2:
                die_split[0] = 1
                die_split[1] = 10
            else:
                die_split[0] -= 1
                die_split[1] = 8
    die_split[0] = str(int(die_split[0]))
    die_split[1] = str(int(die_split[1]))
    temp_return = die_split[0] + "d" + die_split[1]
    return temp_return

# damage table upgrade
def upgradeDice(dice):
    die_split = dice.split('d')
    die_split[0] = int(die_split[0])
    if len(die_split) == 1:
        return "1d2"
    die_split[1] = int(die_split[1])
    if die_split[0] == 1:
        if die_split[1] < 4:
            die_split[1] += 1
        elif die_split[1] < 10:
            die_split[1] += 2
        elif die_split[1] == 10:
            die_split[0] = 2
            die_split[1] = 6
        else:
            die_split[0] = 2
            die_split[1] = 8
    elif die_split[1] == 10:
        die_split[0] = die_split[0] * 2
        die_split[1] = 8
    else:
        if die_split[1] == 4:
            if die_split[0] % 2 == 0:
                die_split[0] = die_split[0] // 2
                die_split[1] = 8
            else:
                die_split[0] = (die_split[0] // 2) + 1
                die_split[1] = 6
        if die_split[1] == 12:
            die_split[0] = die_split[0] * 2
            die_split[1] = 6
        if die_split[1] == 6:
            if die_split[0] > 8 and die_split[0] % 4 != 0:
                die_split[0] = ((die_split[0]//4)+1)*4
            elif die_split[0] > 4 and die_split[0] % 2 != 0:
                die_split[0] = die_split[0]+1
            else:
                die_split[1] = 8
        elif die_split[1] == 8:
            if die_split[0] > 7:
                die_split[0] = ((die_split[0]//4)+1)*4
                if die_split[0] % 4 == 0:
                    die_split[1] = 6
            elif die_split[0] > 3:
                die_split[0] = ((die_split[0]//2)+1)*2
                if die_split[0] % 2 == 0:
                    die_split[1] = 6
            else:
                die_split[0] += 1
                die_split[1] = 6
    die_split[0] = str(int(die_split[0]))
    die_split[1] = str(int(die_split[1]))
    temp_return = die_split[0] + "d" + die_split[1]
    return temp_return

# adds dice of different types together
def addDice(die_a, die_b):
    die_split_a = die_a.split('d')
    die_split_b = die_b.split('d')
    die_split_a[0] = int(die_split_a[0])
    if len(die_split_a) < 2:
        die_split_a[1] = 1
    else:
        die_split_a[1] = int(die_split_a[1])
    die_split_b[0] = int(die_split_b[0])
    if len(die_split_a) < 2:
        die_split_b[1] = 1
    else:
        die_split_b[1] = int(die_split_b[1])
    die_count = die_split_a[0] + die_split_b[0]
    die_total = (die_split_a[1] * die_split_a[0]) + (die_split_b[1] * die_split_b[0])
    die_base = die_total / die_count
    if die_base >= 20:
        die_base = 20
    elif die_base >= 12:
        die_base = 12
    elif die_base >= 10:
        die_base = 10
    elif die_base >= 8:
        die_base = 8
    elif die_base >= 6:
        die_base = 6
    elif die_base >= 4:
        die_base = 4
    elif die_base >= 3:
        die_base = 3
    else:
        die_base = 2
    die_count = str(int(die_count))
    die_base = str(int(die_base))
    temp_return = die_count + "d" + die_base
    return temp_return

# calculate price to lowest denominator
def simplifyCoinage(price):
    int_price = int(price * 100)
    if int_price % 1000 == 0:
        return str(int(price / 10)) + " pp"
    elif int_price % 100 == 0:
        return str(int(price)) + " gp"
    elif len(str(int_price)) > 2:
        return str(round(price, 4)) + " gp"
    elif int_price % 10 == 0:
        return str(int(int_price/10)) + " sp"
    else:
        return str(int_price) + " cp"

# add modifier effects to item
def applyModifier(item, modifier):
    if 'damage' in item:
        for mod in modifier['weapon']:
            if mod == 'prof' and item['equip_type'] != 'weapon':
                continue
            if mod in item:
                if mod == 'group':
                    for spec in mod:
                        item[mod].append(spec)
                elif mod == 'damage':
                    for spec in modifier['weapon'][mod]:
                        if spec in item[mod]:
                            item[mod][spec] = addDice(
                                item[mod][spec], modifier['weapon'][mod][spec])
                        else:
                            item[mod][spec] = modifier['weapon'][mod][spec]
                elif mod == 'special':
                    if 'special' not in item:
                        item['special'] = []
                    for spec in modifier['weapon'][mod]:
                        if spec not in item[mod]:
                            item[mod].append(spec)
                elif mod == 'prof':
                    item[mod] += modifier['weapon'][mod]
                else:
                    for spec in modifier['weapon'][mod]:
                        if spec in item[mod]:
                            item[mod][spec] += modifier['weapon'][mod][spec]
                        else:
                            item[mod][spec] = modifier['weapon'][mod][spec]
            else:
                item[mod] = modifier['weapon'][mod]
    for mod in modifier['equipment']:
        if (mod == 'resistance' or mod == 'bonus') and item['equip_type'] != 'armor':
            continue
        if (mod == 'group' or mod == 'armor_size') and item['equip_type'] == 'armor' and item['equip_type'] != 'shield':
            continue
        if mod in item:
            if mod == 'resistance':
                for spec in modifier['equipment'][mod]:
                    if spec in item[mod]:
                        item[mod][spec] += modifier['equipment'][mod][spec]
                    else:
                        item[mod][spec] = modifier['equipment'][mod][spec]
            elif mod == 'group':
                for spec in modifier['equipment'][mod]:
                    if spec not in item[mod]:
                        item[mod].append(spec)
            elif mod == 'armor_size':
                item['size'] += modifier['equipment'][mod]
            elif mod == 'price':
                item[mod] = item[mod] * modifier['equipment'][mod]
            elif mod == 'size' or mod == 'speed_penalty' or mod == 'bonus' or mod == 'prof' or mod == 'weight':
                item[mod] += modifier['equipment'][mod]
            elif mod == 'special':
                if 'special' not in item:
                    item['special'] = []
                for spec in modifier['equipment'][mod]:
                    if spec not in item[mod]:
                        item[mod].append(spec)
            else:
                for spec in modifier['equipment'][mod]:
                    if spec in item[mod]:
                        item[mod][spec] += modifier['equipment'][mod][spec]
                    else:
                        item[mod][spec] = modifier['equipment'][mod][spec]
        else:
            item[mod] = modifier['equipment'][mod]
    return item

def generateItem():
    global mat_tree_active
    global mod_tree_active
    global typ_tree_active
    if (len(mat_tree_active) < 1) or (len(mod_tree_active) < 1) or (len(typ_tree_active) < 1):
        return
    base_item = None
    base_item = rollItem()
    applyMaterial(base_item)
    global magic
    magic = int(spnbox.get())
    global rolls
    global current_modifiers
    global modifiers
    rolls = magic
    current_modifiers = 0
    max_modifiers = magic * magic
    modifiers = []
    while rolls > 0 and current_modifiers < max_modifiers:
        rollModifier()
    item_name = base_item['name']
    item_desc = ""
    item_damage = None
    has_suffix = False
    # apply modifiers
    for mod in modifiers:
        base_item = applyModifier(base_item, mod)
        temp_switch = randint(0, 1)
        if temp_switch:
            item_name = mod['prefix'][randint(0, len(mod['prefix'])-1)] + " " + item_name
        else:
            if has_suffix:
                item_name = item_name + " and " + mod['suffix'][randint(0, len(mod['suffix'])-1)]
            else:
                has_suffix = True
                item_name = item_name + " of " + mod['suffix'][randint(0, len(mod['suffix'])-1)]
        if 'desc' in mod:
            item_desc = item_desc + " " + mod['desc']
    base_item['price'] = round(base_item['price'] * ((current_modifiers * current_modifiers) + 1), 4)
    item_name = capwords(item_name)
    # adjust size to max/min, and upgrade/downgrade damage dice appropriately
    if(base_item['size'] < 5):
        base_item['size'] = max(base_item['size'], 0)
        if 'damage' in base_item:
            for each in range(5-base_item['size']):
                base_item['damage']['physical'] = downgradeDice(
                    base_item['damage']['physical'])
    if(base_item['size'] > 5):
        base_item['size'] = min(base_item['size'], 8)
        if 'damage' in base_item:
            for each in range(base_item['size']-5):
                base_item['damage']['physical'] = upgradeDice(
                    base_item['damage']['physical'])
    nam_lbl.configure(text=item_name)
    item_damage_verbose = ""
    if 'damage' in base_item:
        item_damage = {}
        for damage in base_item['damage']:
            item_damage[damage] = base_item['damage'][damage]
            if 'damage_bonus' in base_item:
                if damage in base_item['damage_bonus']:
                    if base_item['damage_bonus'][damage] < 0:
                        item_damage[damage] += "-"
                    else:
                        item_damage[damage] += "+"
                    item_damage[damage] += str(base_item['damage_bonus'][damage])
        if 'damage_bonus' in base_item:
            for damage in base_item['damage_bonus']:
                if damage not in base_item['damage']:
                    if base_item['damage_bonus'][damage] < 0:
                        item_damage[damage] = "-"
                    else:
                        item_damage[damage] = "+"
                    item_damage[damage] += str(base_item['damage_bonus'][damage])
        for damage in item_damage:
            if damage == 'physical':
                item_damage_verbose += item_damage[damage] + " " + base_item['type'] + ", "
            else:
                item_damage_verbose += item_damage[damage] + " " + damage + ", "
        item_damage_verbose = item_damage_verbose[:-2]
    dam_lbl.configure(text=item_damage_verbose)
    item_resist_verbose = ""
    if base_item['equip_type'] == 'armor':
        if 'resistance' in base_item:
            item_resist = {}
            for resist in base_item['resistance']:
                if base_item['resistance'][resist] >= 0:
                    item_resist[resist] = "+"
                item_resist[resist] = str(base_item['resistance'][resist])
            item_resist_verbose = ""
            for resist in item_resist:
                item_resist_verbose += item_resist[resist] + " " + resist + ", "
            item_resist_verbose = item_resist_verbose[:-2]
            item_resist_verbose = "Resistance: " + item_resist_verbose
    res_lbl.configure(text=item_resist_verbose)
    item_prof = ""
    if base_item['equip_type'] == 'armor':
        if base_item['subtype'] == 'shield':
            if 'category' in base_item:
                if base_item['category'] == 'tower shield':
                    item_prof = "Tower Shield"
            else:
                item_prof = "Shield"
                if 'prof' in base_item:
                    item_prof += "; "
                    if base_item['prof'] <= 0:
                        item_prof += "Simple"
                    elif base_item['prof'] == 1:
                        item_prof += "Simple (modified)"
                    elif base_item['prof'] == 2:
                        item_prof += "Martial"
                    elif base_item['prof'] == 3:
                        item_prof += "Martial (modified)"
                    else:
                        item_prof += "Exotic"
                    for group in base_item['group']:
                        item_prof += " " + group + ","
                    item_prof = item_prof[:-1]
                    item_prof += " (" + base_item['category'] + ")"
        else:
            if base_item['prof'] <= 0:
                item_prof = "Light"
            elif base_item['prof'] == 1:
                item_prof = "Medium (if in suit)"
            elif base_item['prof'] == 3:
                item_prof = "Heavy (if in suit)"
            elif base_item['prof'] > 3:
                item_prof = "Heavy"
            else:
                item_prof = "Medium"
            for group in base_item['group']:
                item_prof += " " + group + ","
            item_prof = item_prof[:-1]
            item_prof += " (" + base_item['subtype'] + ")"
    elif base_item['equip_type'] == 'weapon':
        if base_item['prof'] <= 0:
            item_prof += "Simple"
        elif base_item['prof'] == 1:
            item_prof += "Simple (modified)"
        elif base_item['prof'] == 2:
            item_prof += "Martial"
        elif base_item['prof'] == 3:
            item_prof += "Martial (modified)"
        else:
            item_prof += "Exotic"
        for group in base_item['group']:
            item_prof += " " + group + ","
        item_prof = item_prof[:-1]
        item_prof += " (" + base_item['category'] + ")"
    pro_lbl.configure(text=item_prof)
    item_price = "Cost: " + simplifyCoinage(base_item['price']) + " | Weight: " + str(base_item['weight']) + " lbs"
    pri_lbl.configure(text=item_price)
    item_crit = ""
    if base_item['equip_type'] == 'weapon':
        item_crit = "Critical: " + str(base_item['crit_range'])
        if base_item['crit_range'] != 20:
            item_crit += "-20"
        item_crit += "/x" + str(base_item['crit_mult'])
        if base_item['range'] > 0:
            item_crit += "\nRange: " + str(base_item['range']) + " ft"
    cri_lbl.configure(text=item_crit)
    item_bonus = ""
    if base_item['equip_type'] == 'armor':
        item_bonus = "Armor Bonus: " + str(base_item['bonus']) + " | Max Dex: "
        if base_item['max_dex'] < 0:
            base_item['max_dex'] = 0
        item_bonus += "+" + str(base_item['max_dex']) + "\nCheck Penalty: " + str(base_item['check_penalty']) + " | Spell Failure: " + str(base_item['spell_failure']) + "%"
    bon_lbl.configure(text=item_bonus)
    item_spec = ""
    if 'special' in base_item:
        if len(base_item['special']) != 0:
            for spec in base_item['special']:
                item_spec += spec + ", "
            item_spec = capwords(item_spec[:-2])
    spe_lbl.configure(text=item_spec)
    item_size = "Fitted for " + size_dict[base_item['size']] + " creatures"
    siz_lbl.configure(text=item_size)
    item_skill_verbose = "    "
    if 'skill' in base_item:
        for skill in base_item['skill']:
            if base_item['skill'][skill] >= 0:
                item_skill_verbose += "+"
            item_skill_verbose += str(base_item['skill'][skill]) + " " + skill + ", "
        item_skill_verbose = item_skill_verbose[:-2]
    ski_lbl.configure(text=item_skill_verbose)
    item_desc = base_item['desc'] + "\n" + item_desc
    des_lbl.configure(text=item_desc)

def loadJson():
    global mat_tree_active
    global mod_tree_active
    global typ_tree_active
    global item_type_bool
    mat_tree_active = []
    mod_tree_active = []
    typ_tree_active = {}
    for num in range(len(mat_tree)):
        if mat_bool[num].get() == 1:
            mat_temp = readjson('material/' + mat_tree[num])
            for mat in mat_temp:
                mat_tree_active.append(mat)
    for num in range(len(mod_tree)):
        if mod_bool[num].get() == 1:
            mod_temp = readjson('modifier/' + mod_tree[num])
            for mod in mod_temp:
                mod_tree_active.append(mod)
    for num in range(len(typ_tree)):
        if typ_bool[num].get() == 1:
            typ_temp = readjson('type/' + typ_tree[num])
            for typ in typ_temp:
                if (typ == 'weapons' and item_type_bool[0].get()) or (typ == 'armor' and item_type_bool[1].get()) or (typ == 'piecemeal' and item_type_bool[2].get()) or (typ == 'shield' and item_type_bool[3].get()) or (typ == 'misc' and item_type_bool[4].get()):
                    if typ not in typ_tree_active:
                        typ_tree_active[typ] = []
                    for spec in typ_temp[typ]:
                        if spec not in typ_tree_active[typ]:
                            typ_tree_active[typ].append(spec)

if __name__ == '__main__':
    chdir(path.dirname(__file__))
    mat_tree = listdir('material')
    mod_tree = listdir('modifier')
    typ_tree = listdir('type')
    mat_bool = []
    mod_bool = []
    typ_bool = []
    mat_tree_active = []
    mod_tree_active = []
    typ_tree_active = {}
    magicalness = 0
    size_dict = {
        0: "Fine",
        1: "Diminutive",
        2: "Tiny",
        3: "Small",
        4: "Medium",
        5: "Large",
        6: "Huge",
        7: "Gargantuan",
        8: "Colossal",
    }
    window = tk.Tk()
    item_type_bool = [tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar]
    window.title("Pathfinder Randomizer")
    window.minsize(0,200)
    opt_frm = tk.Frame(window)
    opt_frm.grid(column=0, row=0, sticky="N", rowspan=2)
    mag_lbl = tk.Label(opt_frm, text="Magicalness", bg="black", fg="white", anchor="w")
    mag_lbl.grid(column=0, row=1, sticky="WE")
    spnbox = tk.Spinbox(opt_frm, from_=0, to=255, width=5)
    spnbox.grid(column=0, row=2, sticky="WE")
    opt_chk_frm_col0 = tk.Frame(opt_frm)
    opt_chk_frm_col0.grid(column=0, row=0, sticky="NWE")
    opt_chk_frm_col1 = tk.Frame(opt_frm)
    opt_chk_frm_col1.grid(column=1, row=0, sticky="NWE")
    opt_chk_sel_frm = tk.Frame(opt_chk_frm_col0)
    opt_chk_sel_frm.grid(sticky="WE")
    opt_chk_sel_lbl = tk.Label(opt_chk_sel_frm, text="Item Types", bg="black", fg="white", anchor="w")
    opt_chk_sel_lbl.grid(column=0, row=0, sticky="WE", columnspan=2)
    opt_chk_sel_wpn_lbl = tk.Label(opt_chk_sel_frm, text="Weapon")
    opt_chk_sel_wpn_lbl.grid(column=0, row=1, sticky="W")
    opt_chk_sel_wpn_check = tk.Checkbutton(opt_chk_sel_frm, variable=item_type_bool[0], command=lambda key=0: loadJson())
    opt_chk_sel_wpn_check.grid(column=1, row=1, sticky="E")
    opt_chk_sel_arm_lbl = tk.Label(opt_chk_sel_frm, text="Armor")
    opt_chk_sel_arm_lbl.grid(column=0, row=2, sticky="W")
    opt_chk_sel_arm_check = tk.Checkbutton(opt_chk_sel_frm, variable=item_type_bool[1], command=lambda key=1: loadJson())
    opt_chk_sel_arm_check.grid(column=1, row=2, sticky="E")
    opt_chk_sel_pcm_lbl = tk.Label(opt_chk_sel_frm, text="Piecemeal Armor")
    opt_chk_sel_pcm_lbl.grid(column=0, row=3, sticky="W")
    opt_chk_sel_pcm_check = tk.Checkbutton(opt_chk_sel_frm, variable=item_type_bool[2], command=lambda key=2: loadJson())
    opt_chk_sel_pcm_check.grid(column=1, row=3, sticky="E")
    opt_chk_sel_sld_lbl = tk.Label(opt_chk_sel_frm, text="Shield")
    opt_chk_sel_sld_lbl.grid(column=0, row=4, sticky="W")
    opt_chk_sel_sld_check = tk.Checkbutton(opt_chk_sel_frm, variable=item_type_bool[3], command=lambda key=3: loadJson())
    opt_chk_sel_sld_check.grid(column=1, row=4, sticky="E")
    opt_chk_sel_msc_lbl = tk.Label(opt_chk_sel_frm, text="Miscellaneous")
    opt_chk_sel_msc_lbl.grid(column=0, row=5, sticky="W")
    opt_chk_sel_msc_check = tk.Checkbutton(opt_chk_sel_frm, variable=item_type_bool[4], command=lambda key=4: loadJson())
    opt_chk_sel_msc_check.grid(column=1, row=5, sticky="E")
    opt_chk_mat_frm = tk.Frame(opt_chk_frm_col0)
    opt_chk_mat_frm.grid(sticky="WE")
    opt_chk_mod_frm = tk.Frame(opt_chk_frm_col0)
    opt_chk_mod_frm.grid(sticky="WE")
    opt_chk_typ_frm = tk.Frame(opt_chk_frm_col1)
    opt_chk_typ_frm.grid(column=1, row=0, sticky="WE")
    opt_chk_mat_lbl = tk.Label(opt_chk_mat_frm, text="Material Sources", bg="black", fg="white", anchor="w")
    opt_chk_mat_lbl.grid(column=0, row=0, sticky="WE", columnspan=2)
    opt_chk_mod_lbl = tk.Label(opt_chk_mod_frm, text="Modifier Sources", bg="black", fg="white", anchor="w")
    opt_chk_mod_lbl.grid(column=0, row=0, sticky="WE", columnspan=2)
    opt_chk_typ_lbl = tk.Label(opt_chk_typ_frm, text="Item Sources", bg="black", fg="white", anchor="w")
    opt_chk_typ_lbl.grid(column=0, row=0, sticky="WE", columnspan=2)
    for num in range(len(mat_tree)):
        mat_bool.append(0)
        mat_bool[num] = tk.IntVar()
        temp_lbl = tk.Label(opt_chk_mat_frm, text=capwords(mat_tree[num][:-5]))
        temp_lbl.grid(column=0, row=num+1, sticky="W")
        temp_check = tk.Checkbutton(opt_chk_mat_frm, variable=mat_bool[num], command=lambda key=num: loadJson())
        temp_check.grid(column=1, row=num+1, sticky="E")
    for num in range(len(mod_tree)):
        mod_bool.append(0)
        mod_bool[num] = tk.IntVar()
        temp_lbl = tk.Label(opt_chk_mod_frm, text=capwords(mod_tree[num][:-5]))
        temp_lbl.grid(column=0, row=num+1, sticky="W")
        temp_check = tk.Checkbutton(opt_chk_mod_frm, variable=mod_bool[num], command=lambda key=num: loadJson())
        temp_check.grid(column=1, row=num+1, sticky="E")
    for num in range(len(typ_tree)):
        typ_bool.append(0)
        typ_bool[num] = tk.IntVar()
        temp_lbl = tk.Label(opt_chk_typ_frm, text=capwords(typ_tree[num][:-5]))
        temp_lbl.grid(column=0, row=num+1, sticky="W")
        temp_check = tk.Checkbutton(opt_chk_typ_frm, variable=typ_bool[num], command=lambda key=num: loadJson())
        temp_check.grid(column=1, row=num+1, sticky="E")
    itm_frm = tk.Frame(window)
    itm_frm.grid(column=2, row=0, sticky="NW", rowspan=100)
    nam_lbl = tk.Label(itm_frm, wraplength=300, text="item name", bg="black", fg="white", anchor="w")
    nam_lbl.grid(column=0, row=0, sticky="WE")
    dam_lbl = tk.Label(itm_frm, wraplength=300, text="")
    dam_lbl.grid(column=0, row=1, sticky="W")
    res_lbl = tk.Label(itm_frm, wraplength=300, text="")
    res_lbl.grid(column=0, row=2, sticky="W")
    pro_lbl = tk.Label(itm_frm, wraplength=300, text="")
    pro_lbl.grid(column=0, row=3, sticky="W")
    pri_lbl = tk.Label(itm_frm, wraplength=300, text="")
    pri_lbl.grid(column=0, row=4, sticky="W")
    cri_lbl = tk.Label(itm_frm, wraplength=300, text="", justify="left")
    cri_lbl.grid(column=0, row=5, sticky="W")
    bon_lbl = tk.Label(itm_frm, wraplength=300, text="", justify="left")
    bon_lbl.grid(column=0, row=6, sticky="W")
    spe_lbl = tk.Label(itm_frm, wraplength=300, text="")
    spe_lbl.grid(column=0, row=7, sticky="W")
    siz_lbl = tk.Label(itm_frm, wraplength=300, text="")
    siz_lbl.grid(column=0, row=8, sticky="W")
    ski_lbl = tk.Label(itm_frm, wraplength=300, text="")
    ski_lbl.grid(column=0, row=9, sticky="W")
    des_lbl = tk.Label(itm_frm, wraplength=300, text="", justify="left")
    des_lbl.grid(column=0, row=10, sticky="W")
    btn = tk.Button(opt_frm, text="Roll", command=generateItem)
    btn.grid(column=0, row=3, sticky="WE")
    window.mainloop()
