DROP DATABASE IF EXISTS mydb;
CREATE DATABASE mydb;
USE mydb;

/* Here are the relations after normalization */
/* For the adoption between ON UPDATE / DELETE NO ACTION and CASCADE, choose NO ACTION if deletion and update is very infrequent */

create table BusinessInfo (

    BusinessName varchar(50),
    CustomerFeedbackScore numeric(3, 1),
    Address varchar(150),
    constraint BusinessInfo_PK primary key (BusinessName)
    
);

create table Vendors (

    VendorID integer,
    BusinessName varchar(50) NOT NULL,
    constraint Vendors_PK primary key (VendorID),
    constraint Vendors_CK UNIQUE (BusinessName), # BusinessName as a candidate key
    constraint Vendors_FK foreign key (BusinessName) references BusinessInfo (BusinessName) ON UPDATE NO ACTION ON DELETE NO ACTION

);

create table ProductInfo (

    ProductID integer,
    Name varchar(70),
    Description varchar(500),
    UnitPrice numeric(7, 2),
    VendorID integer NOT NULL, /* ensure each Product is sold by a Vendor */
    constraint ProductInfo_PK primary key(ProductID),
    constraint ProductInfo_FK foreign key(VendorID) references Vendors(VendorID) ON UPDATE NO ACTION ON DELETE NO ACTION
    
);

create table Products (

    ProductID integer NOT NULL, # ensure each product containing a tag is a valid product in ProductInfo
    Tags varchar(25),
    constraint Products_PK primary key (ProductID, Tags),
	constraint Product_FK foreign key (ProductID) references ProductInfo (ProductID) ON UPDATE NO ACTION ON DELETE CASCADE
    
);

create table Customers (

    CustomerID integer,
    ShippingAddress varchar(150),
    ContactNumber varchar(15), /* storing the region number => varchar(15) */
    constraint Customers_PK primary key(CustomerID)
    
);

create table Orders (

    OrderID integer AUTO_INCREMENT,
    PaymentMethod varchar(10),
	DeliveryStatus varchar(10),
    PaymentTime datetime,
    CustomerID integer NOT NULL, /* ensure each order is purchased by a Customer */
    constraint Orders_PK primary key(OrderID),
    constraint Orders_FK foreign key(CustomerID) references Customers(CustomerID) ON UPDATE NO ACTION ON DELETE NO ACTION
    
);

create table Transactions (

    transactionID BIGINT AUTO_INCREMENT, # ensure the range of transactionID is big enough to handle the number of transactions
    OrderID integer NOT NULL, # ensure each transaction is from an order
    ProductID integer, # ensure each transaction containing a product purchased
	Quantity integer,
    constraint Transactions_PK primary key (transactionID),
	constraint Transactions_FK_1 foreign key (OrderID) references Orders (OrderID) ON UPDATE NO ACTION ON DELETE CASCADE,
	constraint Transactions_FK_2 foreign key (ProductID) references ProductInfo (ProductID) ON UPDATE NO ACTION ON DELETE NO ACTION

);

insert into BusinessInfo values ("MyDress", 7.0, "Room 301, Harmony Plaza, Sunset Road, Beijing, China");
insert into BusinessInfo values ("TechTrend Innovations", 8.1, "Flat 5A, Silver Tower, Main Street, Techno Park, New York City, United States");
insert into BusinessInfo values ("HomeVibe Essentials", 8.3, "Building B10, Green Heights Residences, Skyline Avenue, London, England");

insert into Vendors values (1, "MyDress");
insert into Vendors values (2, "TechTrend Innovations");
insert into Vendors values (3, "HomeVibe Essentials");

insert into ProductInfo values (1, "Slim Fit Denim Jeans", "Stay stylish and comfortable with these slim fit denim jeans. Made from high-quality, stretchable denim fabric, these jeans are perfect for a casual day out or a night on the town. Pair them with your favorite top for a trendy look that never goes out of style.", 770, 1);
insert into ProductInfo values (2, "Leather Crossbody Bag", "Carry your essentials in style with this chic leather crossbody bag. With multiple compartments and an adjustable strap, this bag is perfect for everyday use or for a night out. The sleek design and durable material make it a must-have accessory for any fashionista.", 799, 1);
insert into ProductInfo values (3, "Wireless Bluetooth Earbuds", "Enjoy the freedom of wireless listening with these Bluetooth earbuds. With crystal-clear sound quality and a comfortable fit, these earbuds are perfect for on-the-go music enthusiasts. The long battery life ensures uninterrupted music playback, making them ideal for workouts or daily commute.", 499, 2);
insert into ProductInfo values (4, "Smart Home Security Camera", "Keep your home safe and secure with this smart home security camera. Equipped with motion detection, night vision, and two-way audio, this camera allows you to monitor your home from anywhere using your smartphone. Stay connected and protect your loved ones with this advanced security solution.", 3000, 2);
insert into ProductInfo values (5, "Modern Sectional Sofa", "Elevate your living room with this modern sectional sofa. Featuring a sleek design, plush cushions, and durable upholstery, this sofa offers both style and comfort. Perfect for lounging or entertaining guests, it is a versatile addition to any contemporary home.", 5888, 3);
insert into ProductInfo values (6, "Stainless Steel French Door Refrigerator", "Keep your food fresh and organized with this stainless steel French door refrigerator. With spacious shelves, adjustable temperature settings, and energy-efficient design, this refrigerator offers convenience and functionality. The elegant stainless steel finish adds a touch of sophistication to your kitchen.", 6000, 2);
insert into ProductInfo values (7, "Smartwatch with Fitness Tracker", "Stay active and connected with this smartwatch featuring a built-in fitness tracker. Monitor your daily steps, heart rate, and sleep patterns while receiving notifications for calls and messages. With a sleek design and long-lasting battery life, this smartwatch is a must-have for health-conscious individuals.", 1000, 2);
insert into ProductInfo values (8, "Portable Bluetooth Speaker", "Enjoy your favorite music anywhere with this portable Bluetooth speaker. With high-quality sound, compact design, and long battery life, this speaker is perfect for picnics, gatherings, or outdoor adventures. Pair it with your smartphone or tablet for a wireless listening experience.", 300, 2);

insert into Products values (1, "Jeans");
insert into Products values (1, "Sleek");
insert into Products values (1, "Contemporary");
insert into Products values (2, "Bags");
insert into Products values (2, "Hands-free");
insert into Products values (3, "Earbuds");
insert into Products values (3, "Wireless");
insert into Products values (4, "Wireless");
insert into Products values (4, "High-Tech");
insert into Products values (5, "Furniture");
insert into Products values (5, "Comfortable");
insert into Products values (6, "Electronics");
insert into Products values (6, "Spacious");
insert into Products values (7, "Watch");
insert into Products values (7, "Multi-functional");
insert into Products values (8, "Wireless");
insert into Products values (8, "Multi-functional");

insert into Customers values (1, "Room 210, 5th Floor, Lakeshore Towers, Chicago, United States", "312-6627890");
insert into Customers values (2, "Room 505, 2nd Floor, Downtown Plaza, Houston, United States", "713-7894567");
insert into Customers values (3, "Room 301, 3rd Floor, Peachtree Center, Atlanta, United States", "404-1235678");
insert into Customers values (4, "Room 1502, 15th Floor, Oceanfront Residences, Miami, United States", "786-4568901");
insert into Customers values (5, "Room 410, 4th Floor, Riverfront Tower, Portland, United States", "503-7892345");

insert into Orders values (1, "Apple Pay", "Shipping", "2024-03-17 01:15:13", 1);
insert into Orders values (2, "Visa", "Arrived", "2024-03-16 15:00:01", 1);
insert into Orders values (3, "Master", "Paid", "2024-03-18 00:00:13", 2);
insert into Orders values (4, "Paypal", "Received", "2024-02-18 23:05:59", 3);


insert into Transactions values (1, 1, 1, 1);
insert into Transactions values (2, 1, 5, 2);
insert into Transactions values (3, 2, 1, 1);
insert into Transactions values (4, 2, 6, 1);
insert into Transactions values (5, 3, 2, 4);
insert into Transactions values (6, 3, 8, 1);
insert into Transactions values (7, 4, 3, 1);





