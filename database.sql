DROP DATABASE IF EXISTS Stori_challenge;
CREATE database Stori_challenge;
USE Stori_challenge;

CREATE TABLE account(
	   account_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
     email VARCHAR (255) UNIQUE
);

CREATE TABLE transaction(
	 transaction_id int NOT NULL,
	 account_id int NOT NULL,
   date DATE,
   transaction float NOT NULL,
   FOREIGN KEY (account_id) REFERENCES account(account_id),
   PRIMARY KEY (transaction_id, account_id)
);

INSERT INTO account(email) VALUES("vicvlad2112@hotmail.com");
INSERT INTO transaction (transaction_id, account_id, date, transaction) VALUES(1,1, "2021/10/02", 13.5);
SELECT * FROM account;
select * from transaction;
