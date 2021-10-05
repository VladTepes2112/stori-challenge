# Stori challenge - by Víctor Carrillo
## 10/04/2021

>For this challenge, you must create an idempotent serverless function, e.g. AWS Lambda, that
>processes a file. The function should be triggered when a file is placed in an object storage location,
>e.g. AWS S3, bucket). The file will contain a list of debit and credit transactions on an account. Your
>function should process the file and send summary information to a user in the form of an email.


## Features

- Proccess a csv file to get transactions summary.
- Save all transactions in a database.
- Ready to set up in a aws environment using lambda function, aurora mysql database, s3 bucket.
- Sends a mail with the complete transactions summary of an account.
- Export html file with the same if being executed in local.

All this code can be deployed to either aws or a local machine and will work the same, can be set up with an aurora db if hosted in a lambda function or use a local or rds database if executed locally (both already set up in my personal account).
I'm ready to show any of these functionality (that's for you stori people).

## Tech

This project can use certain tools to work properly:

- [Python 3.8] - All code is written in python 3.8 but has been tested with python 3.7 too.
- [mysql database] - Code is ready to connect to any mysql database in local.
- [Aurora mysql] - Code was setup to connect to an aws aurora mysql database
- [AWS lambda] - Project is being deployed to a lambda function in my aws account with each merge to main.
- [S3 Bucket] - Code is getting a file through a creation event from an s3 bucket if in lambda function. If local it will read test1.csv file.

## Installation

Dillinger requires python 3.7 to run.
Of course you need to clone the repository:
```sh
git clone https://github.com/VladTepes2112/stori-challenge.git
```
The only dependency needed in local is mysql-connector-python so just install that and you are ready to go.
```sh
pip install mysql-connector-python
```

To run the code just call the lambda_function.py

```sh
python lambda_function.py
```

if you want to have a local database to save the transactions run the queries in database.sql file
Or you can also uncomment the db_manager.py and ask me to start the RDS database.

For an aws there are some more aws configs needed but code is ready for it.
