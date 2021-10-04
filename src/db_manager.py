import mysql.connector
from mysql.connector import Error
import base64

class DBmanager:
    """Middle class that will handle db executions to either rds or local mysql through the same interface"""

    def __init__(self):
        self.db_connector = {"executor": None, "finishable": False}
        try:
            self.__stablish_connection()
        except Error as e:
            print(e)

    def execute_query(self, sql):
        query_result = self.db_connector["executor"](sql)

        if(type(query_result) is str):
            if("Duplicate entry" in query_result):
                print('Element already inserted.', sql.split("VALUES")[1])
                query_result = True
            else:
                print("There was an error with your sentence: ", sql)
                print("***", query_result)
        return query_result

    def __execute_nrds_statement(self, sql):
        db_name = "stori_db_vc"
        cluster_arn = "arn:aws:rds:us-east-2:477717552241:cluster:stori-challenge-vc"
        secret_arn = "arn:aws:secretsmanager:us-east-2:477717552241:secret:rds-db-credentials/cluster-2MASYVMN4V2RZSXJEK7U2IQIYA/admin-9g8Wid"
        try:

            result = self.db_connector["client"].execute_statement(
                secretArn=secret_arn,
                database=db_name,
                resourceArn=cluster_arn,
                sql=sql
            )
            print(result)
            if(type(result) is dict and 'records' in result):
                return result['records']
            return result
        except Exception as e:
            return str(e)

    def __execute_local_statement(self, sql):
        connection = self.db_connector["client"]
        try:
            if (connection.is_connected()):
                cursor = self.db_connector["cursor"]
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except Error as e:
            return str(e)

    def __stablish_connection(self):
        print("Stablishing connection")
        try:
            import boto3
            self.db_connector["client"] = boto3.client('rds-data')
            self.db_connector["executor"] = self.__execute_nrds_statement
            print("Connected to boto3")
        except Exception as e:
            print("Running in local db.")
            try:
                # self.db_connector["client"] = mysql.connector.connect(host='database-1-instance-1.cq2chuy4das5.us-east-2.rds.amazonaws.com',
                #                                      database='Stori_challenge',
                #                                      user='admin',
                #                                      password=base64.b64decode(b'c3RvcmlfY2hhbGxlbmdlX2RiX3Bhc3N3b3Jk').decode("utf-8"))
                #
                self.db_connector["client"] = mysql.connector.connect(host='localhost',
                                                      database='stori_db_vc',
                                                      user='root',
                                                      password="root")
                self.db_connector["cursor"] = self.db_connector["client"].cursor()
                self.db_connector["executor"] = self.__execute_local_statement
                self.db_connector["finishable"] = True
            except Exception as e:
                print("Error while connecting to MySQL",e)

    def connection_successful(self):
        return self.db_connector["client"] != None

    def return_connection(self):
        if (self.db_connector["finishable"] and self.db_connector["client"] and self.db_connector["client"].is_connected()):
            self.db_connector["client"].close()
            print("MySQL connection is closed")
