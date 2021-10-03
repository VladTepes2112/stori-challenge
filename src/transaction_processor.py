from dateutil import parser
import mysql.connector
from mysql.connector import Error
import base64
import re

def get_transactions(lines, file_name):
    print("Lines:", lines)
    try:
        if(len(lines) < 2):
            raise Exception("No records found")
        proccessed_transaction = {"total": 0.0, "retirement":{"total": 0.0, "n":0}, "deposit":{"total": 0.0, "n":0}, "months":{}}
        transactions = []
        for line in lines[1:] :
            print("line:", line)
            if(not line):
                continue
            transaction = line.replace("\n", "").split(",")
            # INSERT INTO transaction (transaction_id, account_id, date, transaction) VALUES(1,1, "2021/10/02", 13.5);
            amount = float(transaction[2])
            date = parser.parse(transaction[1])
            transaction_id = int(transaction[0])
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
        print("All lines proccessed")
        save_to_database(transactions, get_email_if_exists(file_name))
        return proccessed_transaction
    except Exception as e:
        return e

def save_to_database(transactions, email):
    print("Saving to database")
    connection = get_connection()
    if(not connection):
        print("Can't connect to database, summary will be generated as would, but should not be considered proccessed.")
        return
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            # Check if the user exists in the database:
            email = email if email else "vicvlad2112@hotmail.com"
            cursor.execute(f'select account_id from account where email = "{email}"')
            result = cursor.fetchone()
            print("email:", email)
            if (result):
                account_id = result[0]
            else:
                cursor.execute(f'insert into account(email) values("{email}")')
                result = cursor.lastrowid
                account_id = result
            # return
            print("account_id:", account_id)
            for transaction in transactions:
                try:
                    insert_transaction = f"""INSERT INTO transaction (transaction_id, account_id, date, transaction)
                        VALUES({transaction["transaction_id"]},{account_id}, "{transaction["date"]}", {transaction["transaction"]})"""
                    cursor.execute(insert_transaction)
                except Error as b:
                    if("Duplicate entry" in str(b)):
                        print(f'Transaction {transaction["transaction_id"]} already exists for {email}.')
                    else:
                        raise Error(e)
            cursor.close()
            connection.commit()
            print("changes saved to database")
        else:
            print("Can't connect to database")
    except Error as e:
        print("Error while connecting to MySQL", e)
        if (connection):
            connection.rollback()
    finally:
        return_connection(connection)

def get_connection():
    try:
        print("Connecting to database")
        return mysql.connector.connect(host='database-1-instance-1.cq2chuy4das5.us-east-2.rds.amazonaws.com',
                                             database='Stori_challenge',
                                             user='admin',
                                             password=base64.b64decode(b'c3RvcmlfY2hhbGxlbmdlX2RiX3Bhc3N3b3Jk').decode("utf-8"))

        # return mysql.connector.connect(host='localhost',
        #                                      database='Stori_challenge',
        #                                      user='root',
        #                                      password='root')

    except Error as e:
        print("Error while connecting to MySQL")

def return_connection(connection):
    if (connection and connection.is_connected()):
        connection.close()
        print("MySQL connection is closed")

def get_email_if_exists(file_name):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email=file_name.replace(".csv", "")
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
