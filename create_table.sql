CREATE TABLE Campaign (
  ID SERIAL PRIMARY KEY,
  Startdate DATE,
  Enddate DATE,
  Firstfood VARCHAR(255),
  Lastfood VARCHAR(255)
);

INSERT INTO Campaign (StartDate, Enddate, Firstfood, Lastfood) VALUES ('2024-12-01', '2024-12-31', '1', '2');

CREATE TABLE People (
  ID INT PRIMARY KEY,
  campaign_ID INT,
  FIO VARCHAR(255),
  foodpreferences VARCHAR(255),
  FOREIGN KEY (campaign_ID) REFERENCES Campaign(ID)
);

CREATE TABLE Product (
  ID INT PRIMARY KEY,
  PRODUCT VARCHAR(255)
);

CREATE TABLE Menu (
  ID INT PRIMARY KEY,
  FeedType VARCHAR(255),
  FeedName VARCHAR(255),
  ProductName VARCHAR(255),
  quantity INT,
  units VARCHAR(255),
  foodpreferences VARCHAR(255),
  ID_PRODUCT INT,
  FOREIGN KEY (ID_PRODUCT) REFERENCES Product(ID)
);
