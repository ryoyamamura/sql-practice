create table customer 
(
    customer_id text primary key,
    customer_name text,
    gender_cd text,
    gender text,
    birth_day date,
    age int,
    postal_cd text,
    address text,
    application_store_cd text,
    application_date text,
    status_cd text
);

create table receipt
(
    sales_ymd int,
    sales_epoch int,
    store_cd text,
    receipt_no int,
    receipt_sub_no int,
    customer_id text,
    product_cd text,
    quantity int,
    amount int,
    PRIMARY KEY (sales_ymd, store_cd, receipt_no, receipt_sub_no)
);

create table store
(
    store_cd text primary key,
    store_name text,
    prefecture_cd text,
    prefecture text,
    address text,
    address_kana text,
    tel_no text,
    longitude real,
    latitude real,
    floor_area real
);

