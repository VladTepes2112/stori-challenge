import json
from src import transaction_processor

def lambda_handler(event, context):
    from src import aws_service
    lines = aws_service.get_s3_lines(event)

    data = transaction_processor.get_transactions(lines)
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
    data = transaction_processor.get_transactions(local_doc.readlines())
    local_doc.close()
    if(valida_transactions(data)):
        print(transaction_processor.get_html_summary(data))

if __name__ == '__main__':
    main()
