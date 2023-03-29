from datetime import datetime
from prettytable import PrettyTable

supported_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR",
                  "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

# create empty lists for individuals and families
individuals = {}
families = {}


with open('Project4.ged') as file:
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
            current_date_tag = "birthdate"  # birthdate, deathdate, alive, age
        elif tag == "DEAT" and level == "1":
            current_date_tag = "deathdate"
            individuals[current_individual_id]["alive"] = False
        elif tag == "MARR" and level == "1":
            current_date_tag = "marriagedate"
        elif tag == "DIV" and level == "1":
            current_date_tag = "divorcedate"
        elif tag == "DATE" and level == "2" and current_date_tag:
            date_value = datetime.strptime(arguments, "%d %b %Y").date()
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
                                           "children": [], "marriage": None, "divorcedate":  None}
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

for fam_id, family in families.items():
    wife = family["wife_id"]
    husband = family["husband_id"]
    individuals[wife]["marriagedate"] = family["marriagedate"]
    individuals[husband]["marriagedate"] = family["marriagedate"]

# create a PrettyTable for individuals and print it
individual_table = PrettyTable()
individual_table.field_names = ["ID", "Name", "Gender", "Birthdate", "Deathdate", "Alive", "Age", "Spouse_ID",
                                "Children"]
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
families_table.field_names = ["ID", "Husband_ID", "Husband_Name", "Wife_ID", "Wife_Name", "Children", "Marriage",
                              "Divorce"]
for families_id in sorted(families.keys(), key=lambda x: x[2:]):
    husband_id = families[families_id]["husband_id"]
    husband_name = families[families_id]["husband_name"]
    wife_id = families[families_id]["wife_id"]
    wife_name = families[families_id]["wife_name"]
    children = families[families_id]["children"]
    marriage_date = families[families_id].get("marriagedate")
    divorce_date = families[families_id].get("divorcedate")
    families_table.add_row(
        [families_id, husband_id, husband_name, wife_id, wife_name, children, marriage_date, divorce_date])
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
            print(f'error: {key} of {info["name"]} is in the future. #US01')

# US02	Birth before marriage
for ind_id, info in individuals.items():
    birth_date = info.get('birthdate')
    marr_date = info.get('marriagedate')
    if not birth_date or not marr_date:
        continue
    if birth_date > marr_date:
        print(f'error: marriage of {info["name"]} is earlier than birthday. #US02')

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
        print(
            f"error: marriage date of family {family_id} occurred after the death dates of both husband and wife. #US05")
    else:
        continue


# US06 Divorce can only occur before death of both spouses
for family_id, family in families.items():
        divorce_date = family['divorcedate']
        husband_death_date = individuals[family['husband_id']]['deathdate']
        wife_death_date = individuals[family['wife_id']]['deathdate']
        if divorce_date is not None:
            if husband_death_date is not None and divorce_date > husband_death_date:
                    print(f"error: divorcedate date of family {family_id} occurred after the death dates of  husband. #US06")
            elif wife_death_date is not None and divorce_date > wife_death_date:
                    print(f"error: divorcedate date of family {family_id} occurred after the death dates of  wife. #US06")



# US07:Less than 150 years old.
for individual_id, individual in individuals.items():
    if individual['age'] >= 150:
        print(f"Error: {individual_id} has an age greater than or equal to 150 years old. #US07")
    else:
        continue

# US08:Birth before marriage of parents.
for family_id, family in families.items():
    marriage_date = family['marriagedate']
    divorce_date = family['divorcedate']
    for child_id in family['children']:
        child_birth_date = individuals[child_id]['birthdate']
        if child_birth_date < marriage_date:
            print(
                f"error: child {individuals[child_id]['name']} was born before parents' marriage date in family {family_id}. #US08")
        if divorce_date and (child_birth_date - divorce_date).days > 270:
            print(
                f"error: child {individuals[child_id]['name']} was born more than 9 months after parents' divorce date in family {family_id}. #US08")
         
        
        
 
#US14 Multiple births <= 5, No more than five siblings should be born at the same time.
for family_id, family in families.items():
    children = family.get("children", [])
    birthdates = [individuals[child]["birthdate"] for child in children if individuals[child]["birthdate"]]
    if len(birthdates) != len(set(birthdates)):
        # there are multiple births
        num_multiple_births = len(birthdates) - len(set(birthdates)) + 1
        if num_multiple_births > 5:
            # check if multiple births exceeds 5
            print(f"Error: {family_id} more than five siblings born at the same time. #US14")

#US15	Fewer than 15 siblings	There should be fewer than 15 siblings in a family
for family_id, family in families.items():
    children = family.get("children", [])
    if len(children) >= 15:
        print(f"Error: {family_id} have {len(children)} childrens, more than 15 siblings. #US15")

# US17 No marriages to descendants.
for family_id, family in families.items():
    husband1_id = family["husband_id"]
    wife1_id = family["wife_id"]
    children = family.get("children", [])
    for i in range(len(children)):
        child_id = children[i]
        for family_id, family in families.items():
            husband2_id = family["husband_id"]
            wife2_id = family["wife_id"]
            if husband1_id == husband2_id and child_id == wife2_id:
                print(f"Error: {husband2_id} or {wife2_id} are descendants, but have married each other. #US17")
            if wife1_id == wife2_id and child_id == husband2_id:
                print(f"Error: {husband2_id} or {wife2_id} are descendants, but have married each other. #US17")


# US18 Siblings should not marry one another.
# iterate through each family
for family_id, family in families.items():
    children = family.get("children", [])

    # iterate through each pair of children
    for i in range(len(children)):
        for j in range(i + 1, len(children)):
            child1_id = children[i]
            child2_id = children[j]

            # check if both children have a common parent
            a = individuals.get(child1_id, {}).get("spouse")
            b = individuals.get(child2_id, {}).get("spouse")
            if a is not None and b is not None and a == b:
                print(f"Error: Siblings {individuals[child1_id]['name']} and {individuals[child2_id]['name']} are siblings, but have married each other. #US18")


