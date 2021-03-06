import boto3
def send_email(body):
    client = boto3.client("ses")
    subject = "New transactions proccessed"

    message = {"Subject": {"Data": subject}, "Body":{"Html": {"Data": body}}}

    response = client.send_email(Source = "vicvlad2112@hotmail.com",
        Destination = {"ToAddresses":["victor.carrillo.2112@gmail.com"]}, Message = message)

def get_s3_lines(event):
    i = event["Records"][0]
    bucket_name = i["s3"]["bucket"]["name"]
    object = i["s3"]["object"]["key"]
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket=bucket_name, Key=object)
    file = data['Body']
    file = data['Body'].read().decode().split("\r\n")
    return{"file": file, "file_name": object}
