from dateutil import parser
from src.db_manager import DBmanager
import re

def get_transactions(lines):
    try:
        if(len(lines) < 2):
            raise Exception("No records found")
        proccessed_transaction = {"total": 0.0, "retirement":{"total": 0.0, "n":0}, "deposit":{"total": 0.0, "n":0}, "months":{}}
        transactions = []
        email = None
        for line in lines[1:] :
            if(not line):
                continue
            if (not email):
                temp_mail = get_email_if_exists(line)
                if(temp_mail):
                    email = temp_mail
                    continue
            transaction = line.replace("\n", "").split(",")
            # INSERT INTO transaction (transaction_id, account_id, date, transaction) VALUES(1,1, "2021/10/02", 13.5);
            amount = float(transaction[2])
            date = parser.parse(transaction[1])
            transaction_id = transaction[0]
            transactions.append({"transaction_id": transaction_id, "date": date.strftime("%Y/%m/%d"), "transaction": amount})

            proccessed_transaction["total"] += amount
            if (amount < 0):
                proccessed_transaction["retirement"]["total"] += amount
                proccessed_transaction["retirement"]["n"] += 1
            else:
                proccessed_transaction["deposit"]["total"] += amount
                proccessed_transaction["deposit"]["n"] += 1


            key_month = date.strftime("%B %Y")
            if(key_month not in proccessed_transaction["months"]):
                proccessed_transaction["months"][key_month] = 0
            proccessed_transaction["months"][key_month] += 1
        save_to_database(transactions, email)
        print("All lines proccessed")
        return proccessed_transaction
    except Exception as e:
        return e

def save_to_database(transactions, email):
    db = DBmanager()
    if(not db.connection_successful()):
        print("Can't connect to database.")
        return
    else:
        email = email if email else "vicvlad2112@hotmail.com"
        print(email)
        result = db.execute_query(f'select account_id from account where email = "{email}"')
        db.execute_query("START TRANSACTION;")

        if (len(result) == 0):
            db.execute_query(f'insert into account(email) values("{email}")')
            result = db.execute_query("SELECT LAST_INSERT_ID()")

        # Temporal fix to have polimorfism aurora-rds dbs (should refactor logic-wise in further iterations)
        account_id = result[0][0] if (type(result[0][0]) is int) else result[0][0]['longValue']

        for transaction in transactions:
            result = db.execute_query(f"""INSERT INTO transaction (transaction_id, account_id, date, transaction)
                VALUES({transaction["transaction_id"]},{account_id}, \"{transaction['date']}\", {transaction["transaction"]})""")
            if(type(result) is str):
                print("saves discarded check and fix the file and try again")
                db.execute_query("ROLLBACK;")
                db.return_connection()
                return
        db.execute_query("COMMIT;")
        print("changes saved to database")
    db.return_connection()

def get_email_if_exists(line):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email=str(line.replace("\n", ""))
    if(re.fullmatch(regex, email)):
        return email

def get_html_summary(transactions):
    months = list(transactions["months"].keys())
    sof="""<style>body{background-color: #007784;color: white;font-family: "Lucida Console";font-size: larger;}.body{margin: 0 auto;align: center;}h1{color: #b3f198;font-family: "Lucida Console";}table{border:0;font-size: large;width: 100%; padding:10px}td{padding: 5px;padding-left: 10px;} .right-td{float:right;}</style><div class="body"><h1 style="margin:30px">Stori challenge - by V&iacute;ctor Carrillo</h1>"""
    body=f"""<p><strong>Transactions summary from file</strong></p><table><tbody>
        <tr><td>Total balance is {transactions["total"]}</td>   <td class="right-td">Average debit amount: {round(transactions["retirement"]["total"] / transactions["retirement"]["n"], 2) if transactions["retirement"]["n"] > 0 else 0}</td></tr>
        <tr><td>Number of transactions in {months[0]}: {transactions["months"][months[0]]}</td>     <td class="right-td">Average credit amount: {round(transactions["deposit"]["total"] / transactions["deposit"]["n"], 2) if transactions["deposit"]["n"] > 0 else 0}</td></tr>
        """
    eof="</tbody></table></div>"
    html_info = sof + body
    html_lines = [f"<tr><td>Number of transactions in {m}: {transactions['months'][m]}</td></tr>" for m in months[1:]]
    html_lines.insert(0, html_info)
    html_lines.append(eof)
    return "".join(html_lines)
