
from prettytable import PrettyTable

supported_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR",
                  "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

# create empty lists for individuals and families
individuals = {}
families = {}

with open('marriage.ged') as file:
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
            individuals[current_individual_id] = {"name": "", "gender": ""}
        elif tag == "NAME" and level == "1":
            current_individual_name = arguments
            individuals[current_individual_id]["name"] = current_individual_name
        elif tag == "SEX" and level == "1":
            individuals[current_individual_id]["gender"] = arguments
        elif tag == "FAMC" and level == "1":
            if "child" not in individuals[current_individual_id]:
                individuals[current_individual_id]["child"] = []
            individuals[current_individual_id]["child"].append(arguments.strip("@"))
        elif tag == "FAMS" and level == "1":
            individuals[current_individual_id]["spouse"] = arguments.strip("@")

        elif tag == "FAM" and level == "0":
            current_family_id = arguments.strip("@")
            families[current_family_id] = {"husband_id": "", "husband_name": "", "wife_id": "", "wife_name": "", "children": []}
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
individual_table.field_names = ["ID", "Name", "Gender", "Spouse_ID", "Children"]
for individual_id in sorted(individuals.keys(), key=lambda x: x[2:]):
    name = individuals[individual_id]["name"]
    gender = individuals[individual_id]["gender"]
    spouse_id = individuals[individual_id].get("spouse", "")
    children = individuals[individual_id].get("child", [])
    individual_table.add_row([individual_id, name, gender, spouse_id, children])

# create a PrettyTable for families and print it
families_table = PrettyTable()
families_table.field_names = ["ID", "Husband_ID", "Husband_Name", "Wife_ID", "Wife_Name", "Children"]
for families_id in sorted(families.keys(), key=lambda x: x[2:]):
    husband_id = families[families_id]["husband_id"]
    husband_name = families[families_id]["husband_name"]
    wife_id = families[families_id]["wife_id"]
    wife_name = families[families_id]["wife_name"]
    children = families[families_id]["children"]
    families_table.add_row([families_id, husband_id, husband_name, wife_id, wife_name, children])

print(individual_table)
print(families_table)
