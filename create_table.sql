CREATE TABLE Campaigns (
  ID SERIAL PRIMARY KEY,
  startdate DATE,
  enddate DATE,
  firstfood INT,
  lastfood INT,
  user_tg_id INT
);

INSERT INTO Campaigns (StartDate, Enddate, Firstfood, Lastfood) VALUES ('2024-12-01', '2024-12-31', '1', '2');

CREATE TABLE Users (
  ID SERIAL PRIMARY KEY,
  name VARCHAR(255),
  password VARCHAR(255),
  tg_id INT
);

INSERT INTO Users (name, password, tg_id) VALUES ('John Doe', 'somepass', '001');

CREATE TABLE People (
  ID INT PRIMARY KEY,
  campaign_ID INT,
  FIO VARCHAR(255),
  foodpreferences VARCHAR(255),
  FOREIGN KEY (campaign_ID) REFERENCES Campaigns(ID)
);

CREATE TABLE Product (
  ID INT PRIMARY KEY,
  PRODUCT VARCHAR(255)
);

CREATE TABLE Menu (
  ID INT PRIMARY KEY,
  feedType VARCHAR(255),
  feedName VARCHAR(255),
  productName VARCHAR(255),
  quantity INT,
  units VARCHAR(255),
  foodpreferences VARCHAR(255),
  ID_PRODUCT INT,
  FOREIGN KEY (ID_PRODUCT) REFERENCES Product(ID)
);

CREATE TABLE Admins (
  ID SERIAL PRIMARY KEY,
  username VARCHAR(255),
  password VARCHAR(255)
);