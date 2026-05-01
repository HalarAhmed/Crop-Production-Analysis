-- 1. Crop Table (Dimension)
CREATE TABLE Crop (
    crop_id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL
);

-- 2. Year Table (Time Dimension)
CREATE TABLE Year (
    year_id SERIAL PRIMARY KEY,
    fiscal_year VARCHAR(20) NOT NULL
);

-- 3. Production Data Table (Fact Table)
CREATE TABLE ProductionData (
    prod_id SERIAL PRIMARY KEY,
    crop_id INT REFERENCES Crop(crop_id),
    year_id INT REFERENCES Year(year_id),
    area NUMERIC,
    production NUMERIC,
    yield NUMERIC
);

-- 4. Weather Data Table
CREATE TABLE WeatherData (
    weather_id SERIAL PRIMARY KEY,
    year_id INT REFERENCES Year(year_id),
    rainfall NUMERIC,
    avg_temperature NUMERIC
);



INSERT INTO Crop (crop_id, crop_name) VALUES (1, 'Mash');
INSERT INTO Crop (crop_id, crop_name) VALUES (2, 'Onion');
INSERT INTO Crop (crop_id, crop_name) VALUES (3, 'Rice');
INSERT INTO Crop (crop_id, crop_name) VALUES (4, 'Sugar Cane');
INSERT INTO Crop (crop_id, crop_name) VALUES (5, 'Wheat');


INSERT INTO Year (year_id, fiscal_year) VALUES (1, '1980-81');
INSERT INTO Year (year_id, fiscal_year) VALUES (2, '1981-82');
INSERT INTO Year (year_id, fiscal_year) VALUES (3, '1982-83');
INSERT INTO Year (year_id, fiscal_year) VALUES (4, '1983-84');
INSERT INTO Year (year_id, fiscal_year) VALUES (5, '1984-85');
INSERT INTO Year (year_id, fiscal_year) VALUES (6, '1985-86');
INSERT INTO Year (year_id, fiscal_year) VALUES (7, '1986-87');
INSERT INTO Year (year_id, fiscal_year) VALUES (8, '1987-88');
INSERT INTO Year (year_id, fiscal_year) VALUES (9, '1988-89');
INSERT INTO Year (year_id, fiscal_year) VALUES (10, '1989-90');
INSERT INTO Year (year_id, fiscal_year) VALUES (11, '1990-91');
INSERT INTO Year (year_id, fiscal_year) VALUES (12, '1991-92');
INSERT INTO Year (year_id, fiscal_year) VALUES (13, '1992-93');
INSERT INTO Year (year_id, fiscal_year) VALUES (14, '1993-94');
INSERT INTO Year (year_id, fiscal_year) VALUES (15, '1994-95');
INSERT INTO Year (year_id, fiscal_year) VALUES (16, '1995-96');
INSERT INTO Year (year_id, fiscal_year) VALUES (17, '1996-97');
INSERT INTO Year (year_id, fiscal_year) VALUES (18, '1997-98');
INSERT INTO Year (year_id, fiscal_year) VALUES (19, '1998-99');
INSERT INTO Year (year_id, fiscal_year) VALUES (20, '1999-00');
INSERT INTO Year (year_id, fiscal_year) VALUES (21, '2000-01');
INSERT INTO Year (year_id, fiscal_year) VALUES (22, '2001-02');
INSERT INTO Year (year_id, fiscal_year) VALUES (23, '2002-03');
INSERT INTO Year (year_id, fiscal_year) VALUES (24, '2003-04');
INSERT INTO Year (year_id, fiscal_year) VALUES (25, '2004-05');
INSERT INTO Year (year_id, fiscal_year) VALUES (26, '2005-06');
INSERT INTO Year (year_id, fiscal_year) VALUES (27, '2006-07');
INSERT INTO Year (year_id, fiscal_year) VALUES (28, '2007-08');
INSERT INTO Year (year_id, fiscal_year) VALUES (29, '2008-09');
INSERT INTO Year (year_id, fiscal_year) VALUES (30, '2009-10');
INSERT INTO Year (year_id, fiscal_year) VALUES (31, '2010-11');
INSERT INTO Year (year_id, fiscal_year) VALUES (32, '2011-12');
INSERT INTO Year (year_id, fiscal_year) VALUES (33, '2012-13');
INSERT INTO Year (year_id, fiscal_year) VALUES (34, '2013-14');
INSERT INTO Year (year_id, fiscal_year) VALUES (35, '2014-15');
INSERT INTO Year (year_id, fiscal_year) VALUES (36, '2015-16');
INSERT INTO Year (year_id, fiscal_year) VALUES (37, '2016-17');
INSERT INTO Year (year_id, fiscal_year) VALUES (38, '2017-18');
INSERT INTO Year (year_id, fiscal_year) VALUES (39, '2018-19');
INSERT INTO Year (year_id, fiscal_year) VALUES (40, '2019-20');
INSERT INTO Year (year_id, fiscal_year) VALUES (41, '2020-21');
INSERT INTO Year (year_id, fiscal_year) VALUES (42, '2021-22');
INSERT INTO Year (year_id, fiscal_year) VALUES (43, '2022-23');
INSERT INTO Year (year_id, fiscal_year) VALUES (44, '2023-24');
INSERT INTO Year (year_id, fiscal_year) VALUES (45, '2024-25');
select * from ProductionData;


CREATE OR REPLACE VIEW ml_ready_data AS
SELECT 
    c.crop_name,
    y.fiscal_year,
    p.area,
    p.production,
    p.yield,
    w.rainfall,
    w.avg_temperature
FROM ProductionData p





JOIN Crop c ON p.crop_id = c.crop_id
JOIN Year y ON p.year_id = y.year_id
JOIN WeatherData w ON y.year_id = w.year_id;



