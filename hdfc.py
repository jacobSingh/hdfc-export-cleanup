import sys
import csv
import re
import logging

l = logging.getLogger()

filename = sys.argv[1]
csv_fp = open(filename)

def transfer(row):
    if not re.match('IMPS|NEFT', row["Merchant"]):
        return
    merchant = row["Merchant"]
    if re.match('IMPS', merchant):
        matches = re.match("[^-]+-[^-]+-([^-]+)-[^-]+-[^-]+-([^-]+)", merchant)
        if not matches:
            l.warning("Error parsing merchant {}".format(merchant))
            return
        name = matches.group(1)
        memo = matches.group(2)
    else:
        matches = re.match(
            "[^-]+-[^-]+-([^-]+)-([^-]+)-[^-]+", merchant)
        if not matches:
            l.warning("Error parsing merchant {}".format(merchant))
            return
        name = matches.group(1)
        memo = matches.group(2)
    row["Merchant"] = name
    row["Memo"] = memo

def chq(row):
    if not re.match('CHQ', row["Merchant"]):
        return

    merchant = row["Merchant"]
    matches = re.match("[^-]+-[^-]+-[^-]+-([^-]+)", merchant)
    if not matches:
        l.warning("Error parsing merchant for chq{}".format(merchant))
        return
    row["Merchant"] = matches.group(1)
    row["Memo"] = "Check"

def clean_pos(row):
    matches = re.match('POS [^ ]+ (.+)', row["Merchant"])
    if not matches:
        return
    row["Merchant"] = matches.group(1)

def match_cash(row):
    matches = re.match('NWD', row["Merchant"])
    if not matches:
        return
    row["Merchant"] = "CASH"

def remove_random(row):
    row["Merchant"].replace("POS DEBIT", "")
    
    
filters = [
    transfer,
    clean_pos,
    remove_random,
    match_cash,
    chq
]

with open(filename) as csvfile:
    writer = csv.DictWriter(sys.stdout, ["Date", "Merchant", "Memo", "Amount"])
    reader = csv.DictReader(csvfile, delimiter=',')
    l.setLevel(logging.ERROR)
    writer.writeheader()
    for row in reader:
        for f in filters:
            f(row)
        writer.writerow(row)


