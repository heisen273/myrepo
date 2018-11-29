CREATE DATABASE IF NOT EXISTS act;


CREATE TABLE IF NOT EXISTS act.tmp_keywords (
   keyword VARCHAR(4000) NOT NULL,
   link VARCHAR(2083) NOT NULL,
   original TEXT NOT NULL,
   score INT NOT NULL,
   process_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS act.keywords (
   keyword VARCHAR(4000) NOT NULL,
   link VARCHAR(2083) NOT NULL,
   original TEXT NOT NULL,
   translation TEXT NOT NULL,
   desktop_screenshot TEXT NOT NULL,
   mobile_screenshot TEXT NOT NULL,
   score INT NOT NULL,
   process_date DATE NOT NULL
);


