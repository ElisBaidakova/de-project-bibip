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

create table raw_data.sales_2nf(
id SERIAL primary key,
brand varchar not null,
auto_name varchar not null,
color varchar not null,
gas_type char(3),
price numeric(9, 2) not null,
date date not null,
customer_name varchar not null,
phone varchar not null,
discount char(2),
origin_country varchar
);

alter table raw_data.sales_2nf alter column gas_type type varchar;

insert into raw_data.sales_2nf(
brand, auto_name, color, gas_type, price, date, customer_name, phone, discount, origin_country)
select
SPLIT_PART(auto, ' ', 1),
LTRIM(
    RTRIM(auto, ', qwertyuiopasdfghjklzxcvbnm'), 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    ),
SPLIT_PART(auto, ', ', -1),
gasoline_consumption,
price,
date,
person_name,
phone,
discount,
brand_origin
from raw_data.sales;

create schema car_shop;

create table car_shop.brands(
brand_id SERIAL primary key,  /*первичный ключ с автоинкрементом*/
brand_name varchar unique     /*название бренда может состоять из букв или цифр и может быть разной длины*/
);
create table car_shop.auto_names    /*первичный ключ с автоинкрементом*/
name varchar unique not null    /*название автомобиля может состоять из букв или цифр и может быть разной длины*/
);
create table car_shop.colors(
color_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
color varchar unique    /*название цвета может состоять из букв и может быть разной длины*/
);

create table car_shop.gasoline_consumption_types(
gct_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
gct_type varchar unique    /*здесь логично указать char(2), но при копировании данных возникает ошибка с длиной строки*/
);
create table car_shop.countries(
country_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
country varchar unique    /*название страны может состоять из букв и может быть разной длины*/
);
create table car_shop.customers(
customer_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
customer_name varchar not null,    /*имя и фамилия могут состоять из букв и могут быть разной длины*/
phone varchar not null    /*номер телефона может состоять из цифр, пробелов, дефисов, скобок и может быть разной длины*/
);
insert into car_shop.brands(brand_name)
select distinct brand
from raw_data.sales_2nf;

insert into car_shop.auto_names(name)
select distinct auto_name
from raw_data.sales_2nf;

insert into car_shop.colors(color)
select distinct color
from raw_data.sales_2nf;

insert into car_shop.gasoline_consumption_types(gct_type)
select distinct gas_type
from raw_data.sales_2nf;

insert into car_shop.countries(country)
select distinct origin_country
from raw_data.sales_2nf;

insert into car_shop.customers(customer_name, phone)
select distinct customer_name, phone
from raw_data.sales_2nf;

create table car_shop.autos(
auto_id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
brand_id smallint not null references car_shop.brands,    /*все поля этой таблицы ссылаются*/
name_id smallint not null references car_shop.auto_names,    /*на первичные ключи других таблиц,*/
color_id smallint not null references car_shop.colors,    /*поэтому тип полей - малое целое число*/
gct_id smallint references car_shop.gasoline_consumption_types,
country_id smallint references car_shop.countries,
price numeric(9, 2) not null    /*цена должна быть максимально точным числом не более семи знаков до запятой и не более двух знаков после*/
);

create table car_shop.auto_and_color(    /*таблица для связи разных цветов и разных автомобилей*/
auto_id int,    /*тип поля id - целое число*/
color_id int,    /*тип поля id - целое число*/
foreign key (auto_id) references car_shop.autos(auto_id),
foreign key (color_id) references car_shop.colors(color_id),
primary key (auto_id, color_id)
);

create table car_shop.auto_sales(
id SERIAL primary key,    /*первичный ключ с автоинкрементом*/
auto_id smallint not null references car_shop.autos,    /*тип поля id - малое целое число*/
date date not null,    /*в этом поле хранится дата, поэтому тип данных - дата*/
customer_id smallint not null references car_shop.customers,    /*тип поля id - малое целое число*/
discount char(2)    /*процент скидки может быть только однозначным или двузначным числом или 0*/
);

insert into car_shop.autos(brand_id, name_id,color_id, gct_id, country_id, price)
select brand_id, name_id,color_id, gct_id, country_id, price
from raw_data.sales_2nf
join car_shop.brands on sales_2nf.brand = brands.brand_name
join car_shop.auto_names on sales_2nf.auto_name = auto_names.name
join car_shop.colors on sales_2nf.color = colors.color
join car_shop.gasoline_consumption_types on sales_2nf.gas_type = gasoline_consumption_types.gct_type
join car_shop.countries on sales_2nf.origin_country = countries.country;

insert into car_shop.auto_sales(auto_id, date, customer_id, discount)
select auto_id, date, customer_id, discount
from raw_data.sales_2nf
join car_shop.autos on autos.price = sales_2nf.price
join car_shop.customers on sales_2nf.customer_name = customers.customer_name;

  /*задание 1*/
select count(
  case 
	when gct_type is null then 1
  end
) / count(*) * 100 as nulls_percentage_gasoline_consumption
from car_shop.autos
join car_shop.gasoline_consumption_types using (gct_id);

  /*задание 2*/
select brand_name, extract(year from date) as year,
    ROUND(AVG(price), 2)
from car_shop.brands
join car_shop.autos using (brand_id)
join car_shop.auto_sales using (auto_id)
group by brand_name, year
order by brand_name;

  /*задание 3*/
select extract(month from date) as month, extract(year from date) as year,
ROUND(AVG(price), 2) as average_price
from car_shop.auto_sales
join car_shop.autos using (auto_id)
where extract(year from date) = 2022
group by extract(month from date), extract(year from date)
order by month;

  /*задание 4*/
select customer_name,
STRING_AGG(CONCAT_WS(' ', brand_name, name), ', ') as cars
from car_shop.customers
join car_shop.auto_sales using(customer_id)
join car_shop.autos using(auto_id)
join car_shop.brands using(brand_id)
join car_shop.auto_names using(name_id)
group by customer_name;

  /*задание 5*/
select country,
  MAX(price / (1 - cast(discount as INTEGER)/ 100)) as price_max,
  MIN(price / (1 - cast(discount as INTEGER) / 100)) as price_min
from car_shop.countries
join car_shop.autos using(country_id)
join car_shop.auto_sales using(auto_id)
where country != 'null'
group by country;

  /*задание 6*/
select count(*) as persons_from_usa_count
from car_shop.customers
where phone like '+1%';