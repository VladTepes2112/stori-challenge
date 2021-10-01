import json
import boto3

def lambda_handler(event, context):
    for i in event["Records"]:
        action = i["eventName"]
        ip = i["requestParameters"]["sourceIPAddress"]
        bucket_name = i["s3"]["bucket"]["name"]
        object = i["s3"]["object"]["key"]

    client = boto3.client("ses")
    subject = str(action) + "Event from " + bucket_name
    body = f"""
        <br>
        This email is to notify you regarding {action} event.
        The object {object} is deleted. (second mail)
        Source IP: {ip} """

    message = {"Subject": {"Data": subject}, "Body":{"Html": {"Data": body}}}

    response = client.send_email(Source = "victor.carrillo.2112@gmail.com",
        Destination = {"ToAddresses":["vicvlad2112@hotmail.com"]}, Message = message)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
