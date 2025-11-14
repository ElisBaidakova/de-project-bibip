create schema raw_data;

create table raw_data.sales(
id integer not NULL,
auto varchar,
gasoline_consumption varchar,
price numeric,
date date,
person_name varchar,
phone varchar,
discount smallint,
brand_origin varchar
);
/*заполняем таблицу при помощи интерфейса dbeaver*/

create table raw_data.sales_2nf_new(
id SERIAL primary key,
brand varchar not null,
auto_name varchar not null,
color varchar not null,
gas_type numeric(4, 1),
price numeric(9, 2) not null,
date date not null,
customer_name varchar not null,
phone varchar not null,
discount char(2),
origin_country varchar
);

ALTER TABLE raw_data.sales_2nf_new
ALTER COLUMN gas_type TYPE varchar;

insert into raw_data.sales_2nf_new(
brand, auto_name, color, gas_type, price, date, customer_name, phone, discount, origin_country)
select
SPLIT_PART(auto, ' ', 1),
REGEXP_SUBSTR(auto, '(?<= )[^,]+'),
SPLIT_PART(auto, ', ', -1),
gasoline_consumption,
price,
date,
person_name,
phone,
discount,
brand_origin
from raw_data.sales;

ALTER TABLE raw_data.sales_2nf_new
ALTER COLUMN gas_type TYPE numeric(4,1)
USING NULLIF(TRIM(gas_type), 'null')::numeric(4,1);

create schema car_shop;

create table car_shop.countries(
country_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
country varchar unique    /*название страны может состоять из букв и может быть разной длины*/
);
create table car_shop.auto_brands(
brand_id SERIAL primary key,  /*первичный ключ с автоинкрементом*/
brand_name varchar unique,     /*название бренда может состоять из букв или цифр и может быть разной длины*/
country_id smallint references car_shop.countries
);
create table car_shop.auto_names(
name_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
auto_name varchar unique not null,    /*название автомобиля может состоять из букв или цифр и может быть разной длины*/
brand_id smallint not null references car_shop.auto_brands,
gas_type numeric(4, 1)  /*выбрано методом исключения: тип integer не подходит для дробных чисел. В этом значении не более одного знака после запятой*/
);
create table car_shop.colors(
color_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
color varchar unique    /*название цвета может состоять из букв и может быть разной длины*/
);
create table car_shop.customers(
customer_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
customer_name varchar not null,    /*имя и фамилия могут состоять из букв и могут быть разной длины*/
phone varchar not null    /*номер телефона может состоять из цифр, пробелов, дефисов, скобок и может быть разной длины*/
);

insert into car_shop.countries(country)
select distinct origin_country
from raw_data.sales_2nf_new;

insert into car_shop.auto_brands(brand_name, country_id)
select distinct brand, country_id
from raw_data.sales_2nf_new
join car_shop.countries on sales_2nf_new.origin_country = countries.country;

alter table car_shop.auto_names alter column brand_id drop not null;

insert into car_shop.auto_names(auto_name, gas_type, brand_id)
select distinct auto_name, gas_type, brand_id
from raw_data.sales_2nf_new
join car_shop.auto_brands on sales_2nf_new.brand = auto_brands.brand_name;

insert into car_shop.colors(color)
select distinct color
from raw_data.sales_2nf;

insert into car_shop.customers(customer_name, phone)
select distinct customer_name, phone
from raw_data.sales_2nf;

create table car_shop.car_and_color(    /*таблица для связи многие ко многим цветов и автомобилей*/
name_id int,    /*тип поля id - целое число*/
color_id int,    /*тип поля id - целое число*/
foreign key (name_id) references car_shop.auto_names(name_id),
foreign key (color_id) references car_shop.colors(color_id),
primary key (name_id, color_id)
);

create table car_shop.auto_sales_new(
id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
brand_id smallint not null references car_shop.auto_brands,    /*тип поля id - малое целое число*/
name_id smallint not null references car_shop.auto_names,    /*тип поля id - малое целое число*/
color_id smallint not null references car_shop.colors,    /*тип поля id - малое целое число*/
price numeric(9, 2) not null,    /*цена содержит не более семи знаков до запятой и не более двух знаков после запятой*/
date_of_sale date not null,    /*в этом поле хранится дата, поэтому тип данных - дата*/
customer_id smallint not null references car_shop.customers,    /*тип поля id - малое целое число*/
discount char(2)    /*процент скидки может быть только однозначным или двузначным числом или 0*/
);

insert into car_shop.auto_sales_new(brand_id, name_id, color_id, price, date_of_sale, customer_id, discount)
select auto_brands.brand_id, auto_names.name_id, color_id, price, date, customer_id, discount
from raw_data.sales_2nf_new
join car_shop.auto_brands on auto_brands.brand_name = sales_2nf_new.brand
join car_shop.auto_names on auto_names.auto_name = sales_2nf_new.auto_name
join car_shop.colors on colors.color = sales_2nf_new.color
join car_shop.customers on sales_2nf_new.customer_name = customers.customer_name;

  /*задание 1*/
select count(
  case 
	when gas_type is null then 1
  end
) / count(*) * 100 as nulls_percentage_gasoline_consumption
from car_shop.auto_names;

  /*задание 2*/
select brand_name, extract(year from date_of_sale) as year,
    ROUND(AVG(price), 2)
from car_shop.auto_brands
join car_shop.auto_sales_new on auto_sales_new.brand_id = auto_brands.brand_id
group by brand_name, year
order by brand_name;

  /*задание 3*/
select extract(month from date_of_sale) as month, extract(year from date_of_sale) as year,
ROUND(AVG(price), 2) as average_price
from car_shop.auto_sales_new
where extract(year from date_of_sale) = 2022
group by extract(month from date_of_sale), extract(year from date_of_sale)
order by month;

  /*задание 4*/
select customer_name,
STRING_AGG(CONCAT_WS(' ', brand_name, auto_name), ', ') as cars
from car_shop.customers
join car_shop.auto_sales_new using(customer_id)
join car_shop.auto_brands using(brand_id)
join car_shop.auto_names using(name_id)
group by customer_name;

  /*задание 5*/
select country,
  MAX(price / (1 - cast(discount as FLOAT)/ 100)) as price_max,
  MIN(price / (1 - cast(discount as FLOAT) / 100)) as price_min
from car_shop.countries
join car_shop.auto_brands using(country_id)
join car_shop.auto_sales_new using(brand_id)
where country != 'null'
group by country;

  /*задание 6*/
select count(*) as persons_from_usa_count
from car_shop.customers
where phone like '+1%';