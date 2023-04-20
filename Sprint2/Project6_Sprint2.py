from datetime import datetime
from dateutil.relativedelta import relativedelta
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
         

#US09:Birth before death of parents
for family_id, family in families.items():
    mom_death_date = individuals[family['wife_id']]['deathdate']
    dad_death_date = individuals[family['husband_id']]['deathdate']
    child_birth_dates = [individuals[id]['birthdate'] for id in family['children']]

    for date in child_birth_dates:
        if mom_death_date:
            if date > mom_death_date:
                print(f"error: child {individuals[child_id]['name']} was born after mom's death date in family {family_id}. #US09")
        
        if dad_death_date:
            if date > dad_death_date + relativedelta(months=9):
                print(f"error: child {individuals[child_id]['name']} was born more than 9 months after dad's death date in family {family_id}. #US09")

#US10:Marriage after 14
for family_id, family in families.items():
    wife_id = family['wife_id']
    husband_id = family['husband_id']
    wife_birth_date = individuals[wife_id]['birthdate']
    husband_birth_date = individuals[husband_id]['birthdate']
    marriage_date = family['marriagedate']
    
    x = marriage_date - relativedelta(years=14)
    if x < wife_birth_date:
        print(f"error: {individuals[wife_id]['name']} was married before 14 yo in family {family_id}. #US10")
    if x < husband_birth_date:
        print(f"error: {individuals[husband_id]['name']} was married before 14 yo in family {family_id}. #US10")

#US11 No bigamy
for family_id, family in families.items():
    husband_id = family['husband_id']
    wife_id = family['wife_id']
    marriage_date = family['marriagedate']
    divorce_date = family['divorcedate']
    for family_id2, family2 in families.items():
        if family_id == family_id2:
            continue
        husband_id2 = family2['husband_id']
        wife_id2 = family2['wife_id']
        marriage_date2 = family2['marriagedate']
        divorce_date2 = family2['divorcedate']
        if husband_id == husband_id2 or wife_id == wife_id2:
            if divorce_date is None or divorce_date2 is None:
                print(f"error: {individuals[husband_id]['name']} and {individuals[husband_id2]['name']} are married to the same person. #US11")
            elif divorce_date > marriage_date2 or divorce_date2 > marriage_date:
                print(f"error: {individuals[husband_id]['name']} and {individuals[husband_id2]['name']} are married to the same person. #US11")

# US12 Parents not too old
for family_id, family in families.items():
    mom_birth_date = individuals[family['wife_id']]['birthdate']
    dad_birth_date = individuals[family['husband_id']]['birthdate']
    child_birth_dates = [individuals[id]['birthdate'] for id in family['children']]

    mom_limit = mom_birth_date + relativedelta(years = 60)
    dad_limit = dad_birth_date + relativedelta(years = 80)

    for date in child_birth_dates:
        if date > mom_limit:
            print(f"error: child {individuals[child_id]['name']} was born after mom's 60 in family {family_id}. #US12")
        
        if date > dad_limit:
            print(f"error: child {individuals[child_id]['name']} was born after dad's 80 in family {family_id}. #US12")

#US13    Siblings spacing	Children should be born at least 8 months apart or more
for family_id, family in families.items():
    children = family.get("children", [])
    birthdates = [individuals[child]["birthdate"] for child in children if individuals[child]["birthdate"]]
    birthdates.sort()
    for i in range(len(birthdates) - 1):
        if (birthdates[i + 1] - birthdates[i]).days < 240:
            print(f"Error: {family_id} siblings are born less than 8 months apart. #US13")

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

# US16 Male last names
for family_id, family in families.items():
    dad_name = individuals[family['husband_id']]['name']
    children = [individuals[id] for id in family['children']]
    sons = list(filter(lambda x: (x['gender'] == 'M'), children))
    son_names = list(map(lambda x: (x['name']), sons))
    for name in son_names:
        if (dad_name.split('/')[1] != name.split('/')[1]):
            print(f"error: son {name} has different last name than his dad {dad_name}. #US16")

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

# US21	Correct gender for role: Husband in family should be male and wife in family should be female.
for family_id, family in families.items():
    husband_id = family["husband_id"]
    wife_id = family["wife_id"]
    a = individuals[husband_id]["gender"]
    b = individuals[wife_id]["gender"]
    if a != "M":
        print(f"error:Husband {husband_id} in {family_id} should be male, not be female . #US21")
    if b != "F":
        print(f"error:Wife {wife_id} in {family_id} should be female , not be male . #US21")

# US22	Unique IDs:	All individual IDs should be unique and all family IDs should be unique.
family_id = []
for family_id1, f in families.items():
    family_id.append(family_id1)
for i1 in range(len(family_id)):
    for j1 in range(i1+1, len(family_id)):
        if i1 == j1:
            print(f"error: All family IDs should be unique. But{i1} and {j1} are same. #US22")
individuals_id = []
for individuals_id1, i in individuals.items():
    individuals_id.append(individuals_id1)
for i2 in range(len(individuals_id)):
    for j2 in range(i2 + 1, len(individuals_id)):
        if i2 == j2:
            print(f"error: All individual IDs should be unique. But{i2} and {j2} are same. #US22")
print("No error: All individual IDs and all family IDs are unique in this GEDCOM file. #US22")

# US23	Unique name and birth date:	No more than one individual with the same name and birth date should appear in a GEDCOM file.
for individuals_id, individual in individuals.items():
    name = individual["name"]
    birthdate = individual["birthdate"]
    for individuals_id1, individual1 in individuals.items():
        name1 = individual1["name"]
        birthdate1 = individual1["birthdate"]
        if name == name1 and birthdate == birthdate1:
            print(f"error: No more than one individual with the same name and birth date should appear in a GEDCOM file. But {individuals_id} and {individuals_id1} are same. #US23")

# US25    Unique first names in families:	No more than one child with the same name and birth date should appear in a family.
for family_id, family in families.items():
    children = family.get("children", [])
    for i in range(len(children)):
        for j in range(i + 1, len(children)):
            child1_id = children[i]
            child2_id = children[j]
            name1 = individuals[child1_id]["name"]
            name2 = individuals[child2_id]["name"]
            birthdate1 = individuals[child1_id]["birthdate"]
            birthdate2 = individuals[child2_id]["birthdate"]
            if name1 == name2 and birthdate1 == birthdate2:
                print(f"error: No more than one child with the same name and birth date should appear in a family. But {child1_id} and {child2_id} are same. #US25")

# US29	List deceased:	List all deceased individuals in a GEDCOM file.
# US30	List living married: List all living married people in a GEDCOM file.
deceased = []
living = []
married = []
living_married = []
for individuals_id, individual in individuals.items():
    a = individual["alive"]
    if a is False:
        deceased.append(individuals_id)
    else:
        living.append(individuals_id)
print("#29: All deceased individuals in a GEDCOM file: " + str(deceased) +" . #29")
for family_id, family in families.items():
    married.append(family["husband_id"])
    married.append(family["wife_id"])
for i in living:
    if i in married:
        living_married.append(i)
print("#30: List all living married people in a GEDCOM file : " + str(living_married) +" . #30")        


# Spring 4:
# US31	List living single：List all living people over 30 who have never been married in a GEDCOM file.
married = []
single = []
for family_id, family in families.items():
    married.append(family["husband_id"])
    married.append(family["wife_id"])
for individuals_id, individual in individuals.items():
    age = individual["age"]
    if age > 30 and individuals_id not in married:
        single.append(individuals_id)
print("#31: List living single(over 30) in a GEDCOM file: " + str(single) +" . #31")

# US32	List multiple births：List all multiple births in a GEDCOM file.
from collections import Counter
for family_id, family in families.items():
    children = family["children"]
    birthdates = [individuals[child]["birthdate"] for child in children if individuals[child]["birthdate"]]
    duplicates = [k for k, v in Counter(birthdates).items() if v > 1]
    multiple = []
    for i in children:
        birthdate = individuals[i]["birthdate"]
        if birthdate in duplicates:
            multiple.append(i)
    if multiple:
        print("#32: List living single(over 30) in a GEDCOM file: " + str(multiple) +" . #32")

# US35	List recent births：List all people in a GEDCOM file who were born in the last 30 days.
born_30days = []
for individuals_id, individual in individuals.items():
    birthdate = individual["birthdate"]
    now = datetime.now().date()
    days = (now - birthdate).days
    if days <= 30:
        born_30days.append(individuals_id)
print("#35:List all people in a GEDCOM file who were born in the last 30 days: " + str(born_30days) +" . #35")

# US36	List recent deaths：List all people in a GEDCOM file who died in the last 30 days.
died_30days = []
for individuals_id, individual in individuals.items():
    deathdate = individual["deathdate"]
    if deathdate:
        now = datetime.now().date()
        days = (now - deathdate).days
        if days <= 30:
            died_30days.append(individuals_id)
print("#36:List all people in a GEDCOM file who died in the last 30 days: " + str(died_30days) +" . #36")
