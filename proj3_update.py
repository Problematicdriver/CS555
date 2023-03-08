import sys

from datetime import datetime, timedelta

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
                                           "children": [], "marriage": "", "divorce": ""}
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








#US07:Less then 150 years old.
for individual_id, individual in individuals.items():
    if individual['age'] >= 150:
        print(f"{individual_id} has an age greater than or equal to 150 years old.")
    else:
        print(f"{individual_id} has an age less than 150 years old.")

#US08:Birth before marriage of parents.
for family_id, family in families.items():
    marriage_date = family['marriagedate']
    divorce_date = family['divorcedate']
    for child_id in family['children']:
        child_birth_date = individuals[child_id]['birthdate']
        if child_birth_date < marriage_date:
            print(f"Error: Child {child_id} was born before parents' marriage date in family {family_id}")
        if divorce_date and (child_birth_date - divorce_date).days > 270:
            print(f"Error: Child {child_id} was born more than 9 months after parents' divorce date in family {family_id}")


