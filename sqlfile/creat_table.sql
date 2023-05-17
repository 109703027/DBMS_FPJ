CREATE TABLE member (
  memberID char(4) PRIMARY KEY,
  name varchar(20),
  sex char(1),
  birth date,
  phone char(10),
  email varchar(30),
  address varchar(50),
  memberExp date
);

CREATE TABLE course (
  courseID char(4) PRIMARY KEY,
  courseTitle varchar(30),
  cost int,
  dateStart date,
  dateEnd date,
  courseDay char(3),
  courseTime char(9),
  coachID char(4)
);

CREATE TABLE coach (
  coachID char(4) PRIMARY KEY,
  name varchar(20),
  expertise text,
  experience text
);

CREATE TABLE equipment (
  equipmentID char(4) PRIMARY KEY,
  type varchar(30),
  dateBought date,
  cost int,
  usable BOOLEAN,
  coachID char(4),
  memberID char(4),
  dateBorrow DATE,
  timeBorrow char(5)
);

CREATE TABLE commodity (
  commodityID char(4) PRIMARY KEY,
  name varchar(30),
  cost int,
  store int
);

CREATE TABLE record (
  courseID char(4),
  memberID char(4),
  evaluate text
);

CREATE TABLE transactions (
  memberID char(4),
  commodityID char(4)
);
