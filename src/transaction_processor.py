from dateutil import parser

def get_transactions(lines):
    try:
        if(len(lines) < 2):
            raise Exception("No records found")
        transactions = {"total": 0.0, "retirement":{"total": 0.0, "n":0}, "deposit":{"total": 0.0, "n":0}, "months":{}}
        for line in lines[1:] :
            if(not line):
                continue
            transaction = line.replace("\n", "").split(",")
            amount = float(transaction[2])
            transactions["total"] += amount
            if (amount < 0):
                transactions["retirement"]["total"] += amount
                transactions["retirement"]["n"] += 1
            else:
                transactions["deposit"]["total"] += amount
                transactions["deposit"]["n"] += 1

            date = parser.parse(transaction[1])
            key_month = date.strftime("%B %Y")
            if(key_month not in transactions["months"]):
                transactions["months"][key_month] = 0
            transactions["months"][key_month] += 1
        return transactions
    except Exception as e:
        return e


def get_html_summary(transactions):
    months = list(transactions["months"].keys())
    html_info = f"""Total balance is: {transactions["total"]} \t\t\t\t Average credit amount: {round(transactions["retirement"]["total"] / transactions["retirement"]["n"], 2) if transactions["retirement"]["n"] > 0 else 0}
Number of transactions in {months[0]}: {transactions["months"][months[0]]}   \t\t Average debit amount: {round(transactions["deposit"]["total"] / transactions["deposit"]["n"], 2) if transactions["deposit"]["n"] > 0 else 0}
"""
    html_lines = [f"Number of transactions in {m}: {transactions['months'][m]}\n" for m in months[1:]]
    html_lines.insert(0, html_info)
    return "".join(html_lines)
