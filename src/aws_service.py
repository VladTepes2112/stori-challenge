import boto3
def send_email(body):
    client = boto3.client("ses")
    subject = "New transactions proccessed"

    message = {"Subject": {"Data": subject}, "Body":{"Html": {"Data": body}}}

    response = client.send_email(Source = "victor.carrillo.2112@gmail.com",
        Destination = {"ToAddresses":["vicvlad2112@hotmail.com"]}, Message = message)

def get_s3_lines(event):
    print("*** s3 lines")
    i = event["Records"][0]
    bucket_name = i["s3"]["bucket"]["name"]
    object = i["s3"]["object"]["key"]
    print("object", object)
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket=bucket_name, Key=object)
    file = data['Body']

    file = data['Body'].read().decode().split("\r\n")
    print(file)
    file.append(object)
    print(object)
    return file
