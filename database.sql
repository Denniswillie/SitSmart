drop table if exists Booking;
drop table if exists SitSmartUser;
drop table if exists TableStats;
drop table if exists StudyTable;
drop table if exists Location;
drop event if exists setAverageTableStats;

create table Location (
    locationId int not null AUTO_INCREMENT,
    name varchar(50),
    PRIMARY KEY (locationId)
);

create table SitSmartUser (
    sitSmartUserId int not null AUTO_INCREMENT,
    email varchar(255) not null,
    PRIMARY KEY (sitSmartUserId)
);

create table StudyTable (
    studyTableId int not null AUTO_INCREMENT,
    studyTableName varchar(30) not null,
    locationId int not null,
    piMacAddress varchar(60) not null,
    avg_temperature float,
    avg_sound float,
    avg_co2 float,
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
    sitSmartUserId int not null,
    PRIMARY KEY (bookingId),
    FOREIGN KEY (studyTableId) REFERENCES StudyTable(studyTableId),
    FOREIGN KEY (sitSmartUserId) REFERENCES SitSmartUser(sitSmartUserId)
);

alter table Booking modify bookingPasswordHash varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SET GLOBAL event_scheduler = ON;
CREATE EVENT setAverageTableStats
ON SCHEDULE EVERY 1 DAY
STARTS '2021-11-25 00:00:00'
DO
update studyTable s join (
    select
        studyTableId,
        avg(temperatureLevel) as avg_temperature,
        avg(soundLevel) as avg_sound,
        avg(co2Level) as avg_co2
    from tableStats where DATEDIFF(NOW() , recordedTime) <= 7 group by studyTableId
) x on s.studyTableId = x.studyTableId
set s.avg_temperature = x.avg_temperature, s.avg_co2 = x.avg_co2, s.avg_sound = x.avg_sound;