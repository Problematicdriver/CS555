import sys

from datetime import datetime
from prettytable import PrettyTable

supported_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR",
                  "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

# create empty lists for individuals and families
individuals = {}
families = {}

filename = sys.argv[1]

print(filename)

with open(filename) as file:
    for line in file:
        line = line.strip()
        parts = line.split(" ")
        level = parts[0]
        tag = parts[1] if len(parts) > 1 else ""
        arguments = " ".join(parts[2:]) if len(parts) > 2 else ""
        if arguments in supported_tags:
            temp = tag
            tag = arguments
            arguments = temp

        if tag == "INDI" and level == "0":
            current_individual_id = arguments.strip("@")
            individuals[current_individual_id] = {"name": "", "gender": "", "birthdate": None, "age": None,
                                                  "alive": True, "deathdate": None}
        elif tag == "NAME" and level == "1":
            current_individual_name = arguments
            individuals[current_individual_id]["name"] = current_individual_name
        elif tag == "SEX" and level == "1":
            individuals[current_individual_id]["gender"] = arguments
        elif tag == "BIRT" and level == "1":
            current_date_tag = "birthdate"#birthdate, deathdate, alive, age
        elif tag == "DEAT" and level == "1":
            current_date_tag = "deathdate"
            individuals[current_individual_id]["alive"] = False
        elif tag == "MARR" and level == "1":
            current_date_tag = "marriagedate"
        elif tag == "DIV" and level == "1":
            current_date_tag = "divorcedate" 
        elif tag == "DATE" and level == "2" and current_date_tag:
            date_value = datetime.strptime(arguments, "%d %b %Y").date()
            print(date_value)
            individuals[current_individual_id][current_date_tag] = date_value
            if current_date_tag == "deathdate":
                birthdate = individuals[current_individual_id]["birthdate"]
                if birthdate:
                    individuals[current_individual_id]["age"] = (date_value - birthdate).days // 365
            elif current_date_tag == "marriagedate":
                families[current_family_id]["marriagedate"] = date_value
            elif current_date_tag == "divorcedate":
                families[current_family_id]["divorcedate"] = date_value
            else:
                now = datetime.now().date()
                birthdate = individuals[current_individual_id]["birthdate"]
                if birthdate:
                    individuals[current_individual_id]["age"] = (now - birthdate).days // 365

        elif tag == "FAMC" and level == "1":
            if "child" not in individuals[current_individual_id]:
                individuals[current_individual_id]["child"] = []
            individuals[current_individual_id]["child"].append(arguments.strip("@"))
        elif tag == "FAMS" and level == "1":
            individuals[current_individual_id]["spouse"] = arguments.strip("@")

        elif tag == "FAM" and level == "0":
            current_family_id = arguments.strip("@")
            families[current_family_id] = {"husband_id": "", "husband_name": "", "wife_id": "", "wife_name": "",
                                           "children": [], "marriage": "", "divorcedate": ""}
        elif tag == "HUSB" and level == "1":
            current_family_husband_name = individuals[arguments.strip("@")]["name"]
            families[current_family_id]["husband_id"] = arguments.strip("@")
            families[current_family_id]["husband_name"] = current_family_husband_name
        elif tag == "WIFE" and level == "1":
            current_family_wife_name = individuals[arguments.strip("@")]["name"]
            families[current_family_id]["wife_id"] = arguments.strip("@")
            families[current_family_id]["wife_name"] = current_family_wife_name
        elif tag == "CHIL" and level == "1":
            families[current_family_id]["children"].append(arguments.strip("@"))
        
# create a PrettyTable for individuals and print it
individual_table = PrettyTable()
individual_table.field_names = ["ID", "Name", "Gender", "Birthdate", "Deathdate", "Alive", "Age", "Spouse_ID", "Children"]
for individual_id in sorted(individuals.keys(), key=lambda x: x[2:]):
    name = individuals[individual_id]["name"]
    gender = individuals[individual_id]["gender"]
    birthdate = individuals[individual_id]["birthdate"]
    deathdate = individuals[individual_id]["deathdate"]
    alive = individuals[individual_id]["alive"]
    age = individuals[individual_id]["age"]
    spouse_id = individuals[individual_id].get("spouse", "")
    children = individuals[individual_id].get("child", [])
    individual_table.add_row([individual_id, name, gender, birthdate, deathdate, alive, age, spouse_id, children])

# create a PrettyTable for families and print it
families_table = PrettyTable()
families_table.field_names = ["ID", "Husband_ID", "Husband_Name", "Wife_ID", "Wife_Name", "Children", "Marriage", "Divorce"]
for families_id in sorted(families.keys(), key=lambda x: x[2:]):
    husband_id = families[families_id]["husband_id"]
    husband_name = families[families_id]["husband_name"]
    wife_id = families[families_id]["wife_id"]
    wife_name = families[families_id]["wife_name"]
    children = families[families_id]["children"]
    marriage_date = families[families_id].get("marriagedate")
    divorce_date = families[families_id].get("divorcedate")
    families_table.add_row([families_id, husband_id, husband_name, wife_id, wife_name, children, marriage_date, divorce_date])
print(individual_table)
print(families_table)

# US01	Dates before current date
# print(individuals.values())

for key in ['birthdate', 'deathdate', 'divorcedate', 'marriagedate']:
    for info in individuals.values():
        date = info.get(key)
        if not date:
            continue
        if datetime.now().date() < date:
            print(f'error: {key} of {info["name"]} is in the future.')

# US02	Birth before marriage
for info in individuals.values():
    birth_date = info.get('birthdate')
    marr_date = info.get('marriagedate')
    if not birth_date or not marr_date:
        continue        
    if birth_date > marr_date:
        print(f'error: marriage of {info["name"]} is earlier than birthday.')

# US03	Birth before death
for ind_id, info in individuals.items():
    birth_date = info.get('birthdate')
    death_date = info.get('deathdate')
    if not birth_date or not death_date:
        continue
    if birth_date > death_date:
        print(f'error: death of {info["name"]} ({death_date}) is earlier than birthday ({birth_date}). #US03')

# US04	Marriage before divorce
for family_id, family in families.items():
    marr_date = family.get('marriagedate')
    div_date = family.get('divorcedate')
    if not marr_date or not div_date:
        continue
    if marr_date > div_date:
        print(f'error: divorce ({div_date}) of family {family_id} is earlier than marriage ({marr_date}). #US04')

# US05 Marriage should occur before death of either spouse
for family_id, family in families.items():
    marriage_date = family['marriagedate']
    husband_death_date = individuals[family['husband_id']]['deathdate']
    wife_death_date = individuals[family['wife_id']]['deathdate']
    if husband_death_date is not None and wife_death_date is not None \
            and marriage_date > husband_death_date and marriage_date > wife_death_date:
                print(f"error: marriage date of family {family_id} occurred after the death dates of both husband and wife.")
    else:
        print(f"error: marriage date of family {family_id} occurred before the death dates of either husband or wife.")


# US06 Divorce can only occur before death of both spouses
for family_id, family in families.items():
    divorce_date = family['divorcedate']
    husband_death_date = individuals[family['husband_id']]['deathdate']
    wife_death_date = individuals[family['wife_id']]['deathdate']
    if husband_death_date is not None and wife_death_date is not None \
            and divorce_date > husband_death_date and divorce_date > wife_death_date:
                print(f"error: divorce date of family {family_id} occurred after the death dates of both husband and wife.")
    else:
        print(f"error: divorce date of family {family_id} occurred before the death dates of either husband or wife.")

        

#US07:Less then 150 years old.
for individual_id, individual in individuals.items():
    if individual['age'] >= 150:
        print(f"error: child {child_id} was born before parents' marriage date in family {family_id}")
    else:
        continue

#US08:Birth before marriage of parents.
for family_id, family in families.items():
    marriage_date = family['marriagedate']
    divorce_date = family['divorcedate']
    for child_id in family['children']:
        child_birth_date = individuals[child_id]['birthdate']
        if child_birth_date < marriage_date:
            print(f"error: child {individuals[child_id]['name']} was born before parents' marriage date in family {family_id}")
        if divorce_date and (child_birth_date - divorce_date).days > 270:
            print(f"error: child {individuals[child_id]['name']} was born more than 9 months after parents' divorce date in family {family_id}")


