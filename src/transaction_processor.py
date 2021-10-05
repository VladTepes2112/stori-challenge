from dateutil import parser
from src.db_manager import DBmanager
import re
import random

def get_transactions(lines):
    try:
        if(len(lines) < 2):
            print("No records found in the file")

        new_transactions = {}
        db = DBmanager()
        email = None
        transactions_sumary = {"total": 0.0, "retirement":{"total": 0.0, "n":0}, "deposit":{"total": 0.0, "n":0}, "months":{} }

        # Add transactions in new file to summary
        for line in lines[1:] :
            if(not line):
                continue
            if (not email):
                temp_mail = get_email_if_exists(line)
                if(temp_mail):
                    email = temp_mail
                    continue
            transaction = line.replace("\n", "").split(",")

            amount = float(transaction[2])
            date = parser.parse(transaction[1])
            transaction_id = transaction[0]
            new_transactions[str(transaction_id)] = {"date": date.strftime("%Y/%m/%d"), "transaction": amount}
            key_month = date.strftime("%B %Y")
            add_to_transactions_summary(transactions_sumary, amount, key_month)

        print("Getting old transactions")
        old_trans = get_from_database(db, email)
        try:
            for trans in old_trans:
                # trans in aurora = [{'longValue': 0}, {'stringValue': '2021-07-15'}, {'doubleValue': 60.5}]
                trans_id = trans[0]
                if(type(trans_id) is dict):
                    trans_id = str(trans_id["longValue"])
                    key_month = parser.parse(trans[1]["stringValue"]).strftime("%B %Y")
                    trans_amount = trans[2]["doubleValue"]
                else:
                    trans_id = str(trans_id)
                    trans_amount = trans[2]
                    key_month = trans[1].strftime("%B %Y")

                #If the transaction came from the database we don't to attempt to save it again
                if(trans_id in new_transactions):
                    new_transactions.pop(trans_id)
                    continue

                add_to_transactions_summary(transactions_sumary, trans_amount, key_month)

        except Exception as e:
            print(e)

        save_to_database(db, new_transactions, email)
        print("All lines proccessed")
        return transactions_sumary
    except Exception as e:
        return e

def add_to_transactions_summary(transactions_sumary, amount, key_month):
    transactions_sumary["total"] += amount
    if(key_month not in transactions_sumary["months"]):
        transactions_sumary["months"][key_month] = 0
    transactions_sumary["months"][key_month] += 1
    if (amount < 0):
        transactions_sumary["retirement"]["total"] += amount
        transactions_sumary["retirement"]["n"] += 1
    else:
        transactions_sumary["deposit"]["total"] += amount
        transactions_sumary["deposit"]["n"] += 1

def save_to_database(db, transactions, email):
    if(not db.connection_successful()):
        print("No transaction will be saved to database")
        return
    else:
        email = email if email else "vicvlad2112@hotmail.com"
        result = db.execute_query(f'select account_id from account where email = "{email}"')
        db.execute_query("START TRANSACTION;")

        if (len(result) == 0):
            db.execute_query(f'insert into account(email) values("{email}")')
            result = db.execute_query("SELECT LAST_INSERT_ID()")

        # Temporal fix to have polimorfism aurora-rds dbs (should refactor logic-wise in further iterations)
        account_id = result[0][0] if (type(result[0][0]) is int) else result[0][0]['longValue']

        for key in transactions:
            transaction = transactions[key]
            result = db.execute_query(f"""INSERT INTO transaction (transaction_id, account_id, date, transaction)
                VALUES({int(key)},{account_id}, \"{transaction['date']}\", {transaction["transaction"]})""")
            if(type(result) is str):
                print("saves discarded check and fix the file and try again")
                db.execute_query("ROLLBACK;")
                db.return_connection()
                return
        db.execute_query("COMMIT;")
        print("Transactions saved to database")
    db.return_connection()

def get_from_database(db, email):
    if(not db.connection_successful()):
        print("No grabbed from database")
        return
    else:
        email = email if email else "vicvlad2112@hotmail.com"
        result = db.execute_query(f'SELECT t.transaction_id, t.date, t.transaction FROM account a NATURAL JOIN transaction t WHERE a.email="{email}"')
        return result

def get_email_if_exists(line):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email=str(line.replace("\n", ""))
    if(re.fullmatch(regex, email)):
        return email

def get_html_summary(transactions):
    cards = "".join([f"""<li>
        <h2><img src='https://picsum.photos/200?random={round(random.random()*1000)%25}' class="card__thumb" alt="" />Total transactions in {i}: <strong>{transactions['months'][i]}</strong> </h2>
      </li>""" for i in transactions["months"]])
    return """<style>
  /* demo shizzle only */
  :root {
    --surface-color: #fff;
    --curve: 40;
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Noto Sans JP', sans-serif;
    background-color: #7cd8e2;
  }

  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 4rem 5vw;
    padding: 0;
    list-style-type: none;
  }

  .card {
    position: relative;
    display: block;
    height: 50%;
    border-radius: calc(var(--curve) * 1px);
    overflow: hidden;
    text-decoration: none;
  }

  .card__image {
    width: 100%;
    height: auto;
  }

  .card__overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1;
    border-radius: calc(var(--curve) * 1px);
    background-color: var(--surface-color);
    transform: translateY(100%);
    transition: .2s ease-in-out;
  }

  .card:hover .card__overlay {
    transform: translateY(0);
  }

  .card__header {
    position: relative;
    display: flex;
    align-items: center;
    gap: 2em;
    padding: 2em;
    border-radius: calc(var(--curve) * 1px) 0 0 0;
    background-color: var(--surface-color);
    transform: translateY(-100%);
    transition: .2s ease-in-out;
  }

  .card__arc {
    width: 80px;
    height: 80px;
    position: absolute;
    bottom: 100%;
    right: 0;
    z-index: 1;
  }

  .card__arc path {
    fill: var(--surface-color);
    d: path("M 40 80 c 22 0 40 -22 40 -40 v 40 Z");
  }

  .card:hover .card__header {
    transform: translateY(0);
  }

  .card__thumb {
    flex-shrink: 0;
    width: 50px;
    height: 50px;
    border-radius: 50%;
  }

  .card__title {
    font-size: 1em;
    margin: 0 0 .3em;
    color: #6A515E;
  }

  .card__tagline {
    display: block;
    margin: 1em 0;
    font-family: "MockFlowFont";
    font-size: .8em;
    color: #D7BDCA;
  }

  .card__status {
    font-size: .8em;
    color: black;
  }

  .card__description {
    padding: 0 2em 2em;
    margin: 0;
    color: #D7BDCA;
    font-family: "MockFlowFont";
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    overflow: hidden;
  }
  .main_content{
    height: 65%;
    width: 90%;
    background-color:#ecfffe;
    margin-top:3% !important;
    margin: auto;
    color: black;
    border-radius: 25px;
    text-align:center;
    font-family: "Lucida Console";
  }
  h1{
    padding-top:2%;
  }
  li{
    height:60%;
  }
  table{
    width: 90%;
    font-size: xx-large;
  }
  td{
  padding: 42px;
  }
</style>""" + f"""
<div class="main_content" >
  <h1>Stori challenge - by V&iacute;ctor Carrillo <img src="https://media-exp1.licdn.com/dms/image/C4E0BAQHtxnxSv1F2HQ/company-logo_200_200/0/1562253639430?e=2159024400&v=beta&t=OTPUGauJAaVkkW2Uc1pZS9Qj_AHMCC2nbqt2ttvR6uE" class="card__thumb" alt="" /> </h1>
    <p><strong>Transactions summary from file</strong><br>
    This message has been sent automatically trough a lambda function</p>
    <table align="center"><tbody>
    <tr><td>The total balance of the account is: <strong>{round(transactions["total"], 2)}</strong></td>   <td class="right-td">All time average debit amount: <strong>{round(transactions["retirement"]["total"] / transactions["retirement"]["n"], 2) if transactions["retirement"]["n"] > 0 else 0}</strong></td></tr>
    <tr><td></td> <td class="right-td">All time average credit amount: <strong>{round(transactions["deposit"]["total"] / transactions["deposit"]["n"], 2) if transactions["deposit"]["n"] > 0 else 0} </strong></td></tr>
    </tbody></table>
</div>
<ul class="cards"> {cards} </ul>
    """
    # months = list(transactions["months"].keys())
    # sof="""<style>body{background-color: #007784;color: white;font-family: "Lucida Console";font-size: larger;}.body{margin: 0 auto;align: center;}h1{color: #b3f198;font-family: "Lucida Console";}table{border:0;font-size: large;width: 100%; padding:10px}td{padding: 5px;padding-left: 10px;} .right-td{float:right;}</style><div class="body"><h1 style="margin:30px">Stori challenge - by V&iacute;ctor Carrillo</h1>"""
    # body=f"""<p><strong>Transactions summary from file</strong></p><table><tbody>
    #     <tr><td>Total balance is {transactions["total"]}</td>   <td class="right-td">Average debit amount: {round(transactions["retirement"]["total"] / transactions["retirement"]["n"], 2) if transactions["retirement"]["n"] > 0 else 0}</td></tr>
    #     <tr><td>Number of transactions in {months[0]}: {transactions["months"][months[0]]}</td>     <td class="right-td">Average credit amount: {round(transactions["deposit"]["total"] / transactions["deposit"]["n"], 2) if transactions["deposit"]["n"] > 0 else 0}</td></tr>
    #     """
    # eof="</tbody></table></div>"
    # html_info = sof + body
    # html_lines = [f"<tr><td>Number of transactions in {m}: {transactions['months'][m]}</td></tr>" for m in months[1:]]
    # html_lines.insert(0, html_info)
    # html_lines.append(eof)
    # return "".join(html_lines)
