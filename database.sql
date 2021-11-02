drop table if exists Booking;
drop table if exists TableStats;
drop table if exists StudyTable;
drop table if exists Location;

create table Location (
    locationId int not null AUTO_INCREMENT,
    name varchar(50),
    PRIMARY KEY (locationId)
);

create table StudyTable (
    studyTableId int not null AUTO_INCREMENT,
    studyTableName varchar(30) not null,
    locationId int not null,
    piMacAddress varchar(60) not null,
    averageTemperatureLevel float,
    averageSoundLevel float,
    averageCo2Level float,
    PRIMARY KEY (studyTableId, locationId),
    FOREIGN KEY (locationId) REFERENCES Location(locationId),
    CONSTRAINT UC_StudyTable UNIQUE (studyTableName, locationId)
);

create table TableStats (
    tableStatsId int not null AUTO_INCREMENT,
    studyTableId int not null,
    recordedTime DATETIME,
    temperatureLevel float,
    soundLevel float,
    co2Level float,
    PRIMARY KEY (tableStatsId),
    FOREIGN KEY (studyTableId) REFERENCES StudyTable(studyTableId)
);

create table Booking (
    bookingId int not null AUTO_INCREMENT,
    bookingPasswordHash varchar(128) NOT NULL,
    salt varchar(40) not null,
    studyTableId int not null,
    startTime DATETIME,
    endTime DATETIME,
    PRIMARY KEY (bookingId),
    FOREIGN KEY (studyTableId) REFERENCES StudyTable(studyTableId)
);

alter table Booking modify bookingPasswordHash varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;