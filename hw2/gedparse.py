import pprint

l0_2_tags = ["INDI", "FAM"]
l0_3_tags = ["HEAD", "TRLR", "NOTE"]
l1_ind_tags = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "CHIL"]
l1_fam_tags = ["MARR", "HUSB", "WIFE"]
date_tags = ["BIRT", "DIV", "MARR"]
curr_top_level = "NONE"
curr_2nd_level = "NONE"

ppl_idx = {
        "NAME": 0,
        "SEX": 1,
        "BIRT": 2,
        "DEAT": 3,
        "FAMC": 4,
        "FAMS": 5,
        "CHIL": 6,
        }

fml_idx = {
        "MARR": 0,
        "DIVOR": 1,
        "HUSB": 2,
        "HUSBNAME": 3,
        "WIFE": 4,
        "WIFENAME": 5,
        "CHIL": 6
        }

people = {}
families = {}

def parseLine(line):
    global curr_top_level
    global curr_2nd_level
    valid = "N"
    tokens = line.split()
    print("--> {str}".format(str = line.strip()))
    if len(tokens) == 0:
        return
    if tokens[0] == "0":
        # 0 <id> <tag> or 0 <tag> <arguments that may be ignored>
        if tokens[1] in l0_3_tags:
            valid = "Y"
            curr_top_level = "NONE"
        elif tokens[2] in l0_2_tags:
            valid = "Y"
            curr_top_level = tokens[2]
        else: return
        if len(tokens) < 3:
            print("<-- 0|{tag}|{v}".format(tag = tokens[1], v = valid))
        elif len(tokens) == 3:
            if curr_top_level == "INDI":
                people[tokens[1]] = ["N/A"] * len(ppl_idx)
            elif curr_top_level == "FAM":
                families[tokens[1]] = ["N/A"] * len(fml_idx)
            print("<-- 0|{id}|{v}|{tag}".format(id = tokens[1], tag = tokens[2], v = valid))
        elif len(tokens) > 3:
            print("<-- 0|{tag}|{v}|{args}".format(tag = tokens[1], v = valid, args = ' '.join(tokens[3:])))
        curr_top_level += " " + tokens[1]
    elif tokens[0] == "1":
        # 1 <tag> <arguments>
        top_level_tags = curr_top_level.split()
        ID = top_level_tags[1]
        if tokens[1] in l1_ind_tags and top_level_tags[0] == "INDI":
            valid = "Y"
            people[ID][ppl_idx[tokens[1]]] = ' '.join(tokens[2:])
        elif tokens[1] in l1_fam_tags and top_level_tags[0] == "FAM":
            valid = "Y"
            if tokens[1] == "CHIL":
                families[ID][fml_idx[tokens[1]]].append(' '.join(tokens[2:]))
            else:
                families[ID][fml_idx[tokens[1]]] = ' '.join(tokens[2:])
        if tokens[1] in date_tags:
            curr_2nd_level = tokens[1]
        if len(tokens) < 3:
            print("<-- 1|{tag}|{v}".format(tag = tokens[1], v = valid))
        else:
            print("<-- 1|{tag}|{v}|{args}".format(id = tokens[1], tag = tokens[1], v = valid, args = ' '.join(tokens[2:])))
    elif tokens[0] == "2":
        # 2 <tag> <arguments>
        top_level_tags = curr_top_level.split()
        ID = top_level_tags[1]
        print(curr_2nd_level)
        if tokens[1] == "DATE" and curr_2nd_level in date_tags:
            valid = "Y"
            if top_level_tags[0] == "INDI":
                people[ID][ppl_idx[curr_2nd_level]] = ' '.join(tokens[2:])
            elif top_level_tags[0] == "FAM":
                families[ID][fml_idx[curr_2nd_level]] = ' '.join(tokens[2:])
        print("<-- 2|{tag}|{v}|{args}".format(tag = tokens[1], v = valid, args = ' '.join(tokens[2:])))
        curr_2nd_level = "NONE"


def main():
    file = open('Jiayi.ged', 'r')
    Lines = file.readlines()
    for line in Lines:
        parseLine(line)
    pp = pprint.PrettyPrinter(indent=4) 
    pp.pprint(people)
    pp.pprint(families)

main()
