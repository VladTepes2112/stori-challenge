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
