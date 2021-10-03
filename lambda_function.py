import json
from src import transaction_processor

def lambda_handler(event, context):
    from src import aws_service
    print("*** Started xxxx lambda handler ***")
    lines = aws_service.get_s3_lines(event)
    file_name = lines["file_name"]
    print("File name:", file_name)
    data = transaction_processor.get_transactions(lines["file"], file_name)
    if(valida_transactions(data)):
        aws_service.send_email(transaction_processor.get_html_summary(data))
    else:
        aws_service.send_email(data)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(lines)
    }

def valida_transactions(transactions):
    return type(transactions) is dict

def main():
    local_doc = open("test1.csv")
    data = transaction_processor.get_transactions(local_doc.readlines(), "victor.carrillo.2112@hotmail.com.csv")
    local_doc.close()
    if(valida_transactions(data)):
        result = transaction_processor.get_html_summary(data)
        with open('test1-result.html', 'w') as f:
            f.write(result)

if __name__ == '__main__':
    main()
