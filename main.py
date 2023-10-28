import csv
import requests
import pandas as pd
from re import match
from urllib.parse import quote

def reference(url, id, alt = None):
    print(str(id) + "/" + str(len(names) - 1))
    pd.read_html(requests.get(url).content)[0].to_csv("temp.csv")
    with open('temp.csv', mode='r') as file:
        data = []
        csvFile = csv.reader(file)

        for line in csvFile:
            data.append(line)

        data = data[1:-6]
        has = False
        for dat in data:
            if dat[4] in ["Single Family Home", "Single Family - more than one house per parcel", "Vacant Residential - lot & acreage less than 5 acres"]: 
                has = True
                if dat[2] not in names_n:
                    names_n.append(dat[2])

        if has == False and alt != None:
            reference(alt, id)

def list_peeps(url, id):
    print(str(id) + "/" + str(len(names_n) - 1))
    pd.read_html(requests.get(url).content)[2].to_csv("temp.csv")
    with open('temp.csv', mode='r') as file:
        csvFile = csv.reader(file)
        data = []
        for line in csvFile:
            data.append(line)

        datx = data[2][2].split("  ")[1:]
        
        if datx[0] == "Site Address (First Building)":
            return

        names = datx[0].replace(", EST", "").replace("EST", "").replace("C/O", "").split(' ')[2:]

        index = 0
        for n in names:
            if match('[0-9]+', n) or n in ["PO"]:
                break
            index += 1

        mail_add = ' '.join(names[index:-2])
        mail_state = names[-2]
        mail_zip = names[-1]

        name = []
        temp = []
        for idx, n in enumerate(names[:index]):
            if n.endswith(','):
                if idx != 0:
                    name.append(temp)
                temp = [n]
            elif idx == len(names[:index]) - 1:
                if len(temp) < 2:
                    temp.append(n)
                name.append(temp)
            elif len(temp) < 2:
                temp.append(n)

        usename = []
        if len(name) <= 2: usename = name[0]
        else: usename = name[-1]

        site_add = datx[1]
        site_zip = ""

        if datx[1] == mail_add or site_add.endswith("(Unincorporated)"):
            site_add = mail_add
            site_zip = mail_zip
        else:
            site_zip = "?"

        row = [usename[1], usename[0].removesuffix(','), mail_add, mail_state, mail_zip, site_add, " ", "FL", site_zip, " "]
        if row not in rows:
            rows.append(row)

names = []
with open('SearchResults.csv', mode='r') as file:
    csvFile = csv.reader(file)

    for line in csvFile:
        if line[0] not in names:
            names.append(line[0])
names = names[1:]

names_n = []
for idx, name in enumerate(names):
    a = quote(name, safe='').replace(',', '').replace('.', '').upper().split("%20")
    a[0] = a[0] + "%2C"
    print(names[idx])
    if len(a) <= 2 or a[2] in ["SR", "JR", "III"]:
        reference("https://www.pcpao.org/query_name.php?Text1=" + '+'.join(a) + "&nR=25", idx)
    else:
        m = a[:3]
        print(m)
        m[2] = m[-1][0]
        reference("https://www.pcpao.org/query_name.php?Text1=" + '+'.join(m) + "&nR=25", idx, "https://www.pcpao.org/query_name.php?Text1=" + '+'.join(m[:2]))

fields = ["First Name", "Last Name", "Mail Address", "Mail State", "Mail Zip", "Property Address", "Property Address 2", "Property State", "Property Zip", "NOTES"]  
rows = []
for idy, name in enumerate(names_n):
    id_split = name.split('-')
    idx = id_split[2] + id_split[1] + id_split[0] + id_split[3] + id_split[4] + id_split[5]
    list_peeps("https://www.pcpao.org/general.php?strap=" + str(idx), idy)

with open("result.csv", "w", newline='', encoding='utf-8') as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows) 
