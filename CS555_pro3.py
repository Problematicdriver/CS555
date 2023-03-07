from prettytable import PrettyTable

# 存储所有的个人信息
info_list = [
    {
        "INDI": "@I1@",
        "NAME": "Facai /Xiao/",
        "GIVN": "Facai",
        "SURN": "Xiao",
        "_MARNM": "Xiao",
        "SEX": "M",
        "BIRT": "1 JAN 1999",
        "MARR": "2 JAN 1999",
        "FAMC": "@F1@"
    },
    {
        "INDI": "@I2@",
        "NAME": "Hao /Xiao/",
        "GIVN": "Hao",
        "SURN": "Xiao",
        "_MARNM": "Xiao",
        "SEX": "M",
        "BIRT": "1 FEB 1965",
        "MARR": "3 JAN 1969",
        "FAMC": "@F2@",
        "FAMS": "@F1@"
    },
    {
        "INDI": "@I3@",
        "NAME": "Lailai /Xu/",
        "GIVN": "Lailai",
        "SURN": "Xu",
        "_MARNM": "Xu",
        "SEX": "F",
        "BIRT": "1 JAN 1971",
        "MARR": "12 FEB 1979",
        "FAMC": "@F3@",
        "FAMS": "@F1@"
    }
]

# 按照类别分开信息
indi_list = []
famc_list = []
fams_list = []
for info in info_list:
    if "INDI" in info:
        indi_list.append(info)
    elif "FAMC" in info:
        famc_list.append(info)
    elif "FAMS" in info:
        fams_list.append(info)

# 打印个人信息表格
indi_table = PrettyTable()
indi_table.field_names = ["ID", "Name", "Sex", "Birth", "FamC", "FamS"]
for indi in indi_list:
    indi_table.add_row([
        indi["INDI"],
        indi["NAME"],
        indi["SEX"],
        indi["BIRT"],
        indi["FAMC"] if "FAMC" in indi else "",
        indi["FAMS"] if "FAMS" in indi else ""
    ])
print("Individuals:")
print(indi_table)

# 打印家庭信息表格
fam_table = PrettyTable()
fam_table.field_names = ["ID", "FamC", "FamS"]
for fam in famc_list + fams_list:
    fam_table.add_row([
        fam["INDI"] if "FAMC" in fam else fam["FAMS"],
        fam["FAMC"] if "FAMC" in fam else "",
        fam["FAMS"] if "FAMS" in fam else ""
    ])
print("Families:")
print(fam_table)

# Check Birthday
from datetime import datetime
for key in ['BIRT', 'DEAT', 'DIV', 'MARR']:
    for info in info_list:
        date = info.get(key)
        if not date:
            continue
        date_time = datetime.strptime(date, "%d %b %Y")
        if datetime.now() < date_time:
            print(f'error: {key} of {info["NAME"]} is in the future.')

# Check Marriage Date
for info in info_list:
    birth_date = datetime.strptime(info.get('BIRT'), "%d %b %Y")
    marr_date = datetime.strptime(info.get('MARR'), "%d %b %Y")
    if birth_date > marr_date:
        print(f'error: marriage of {info["NAME"]} is earlier than birthday.')



