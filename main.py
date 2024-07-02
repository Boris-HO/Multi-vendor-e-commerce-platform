import mysql.connector
import pandas as pd

def make_connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Pass1234",
        auth_plugin='mysql_native_password',
        database="mydb"
    )
    mycursor = mydb.cursor()
    return mydb, mycursor

def close_connection(db, cursor):
    cursor.close()
    db.close()

def cursor_to_df(cursor):
    data = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    return df

def prompt_format_1_2(prompt):
    para_list = [x.strip() for x in prompt.split(',')]
    if len(para_list) == 3:
        return para_list
    elif len(para_list) == 2:
        para_list.append('')  # give an empty address
    return para_list

def sql_execution(db, cursor, sqls):
    try:
        for sql in sqls:
            cursor.execute(sql)
        print("Successfully executed.")
    except Exception as e:
        print(f"Error: {e}")
        print("Please check if the inputs are valid.")
        db.rollback()

class PromptFormat:
    def prompt_format_1_2(self, prompt):
        para_list = [x.strip() for x in prompt.split(',')]
        if len(para_list) == 3:
            return para_list
        elif len(para_list) == 2:
            para_list.append('')  # give an empty address
        return para_list
    def prompt_format_2_1(self, prompt):
        if prompt == "":
            return ""
        return prompt
    def prompt_format_2_2(self, prompt1, prompt2):
        values = [x.strip() for x in prompt1.split(', ')]
        ProductID = values[0]
        ProductName = values[1]
        Description = values[2]
        UnitPrice = values[3]
        VendorID = values[4]

        tags = [x.strip() for x in prompt2.split(', ')]
        insert_statements = []
        insert_statement1 = f'insert into ProductInfo values ({ProductID}, "{ProductName}", "{Description}", {UnitPrice}, {VendorID});'
        insert_statements.append(insert_statement1)

        for tag in tags:
            insert_statement = f'insert into Products values ({ProductID}, "{tag}");'
            insert_statements.append(insert_statement)

        return insert_statements

    def prompt_format_3_1(self, prompt):
        return self.prompt_format_2_1(prompt)
    
    def prompt_format_3_2(self, prompt):
        if prompt == "":
            return "IS NOT NULL"
        return " = " + prompt
    
    def prompt_format_4_1(self, prompt):
        para_list = [x.strip() for x in prompt.split(',')]
        return para_list
    
while True:
    try:
        print("Here are the functionalities:\n1. Vendor Administration\n2. Product Catalog Management\n3. Product Discovery\n4. Product Purchase\n5. Order Modification")
        choice = int(input("Please choose one functionality (1 to 5): "))
        if choice == 1:
            choice = float(input("Please choose one functionality:\n1.1 Display a list of all vendors\n1.2 Insert new vendor(s)\n"))
            if choice == 1.1:
                mydb, mycursor = make_connection()
                sql = """                        
                      select *
                      from Vendors inner join BusinessInfo on Vendors.BusinessName = BusinessInfo.BusinessName
                      order by VendorID;
                      """
                mycursor.execute(sql)
                df = cursor_to_df(mycursor)
                print(df)
                close_connection(mydb, mycursor)
            elif choice == 1.2:
                prompt_format = PromptFormat()
                prompt = input("Please input the VendorID, BusinessName, Address (optional) in the following format A, B, C: ")
                para_list = prompt_format.prompt_format_1_2(prompt)
                mydb, mycursor = make_connection()
                sql_1 = 'insert into BusinessInfo values ("{}", null, "{}");'.format(para_list[1], para_list[2])
                sql_2 = 'insert into Vendors values ({}, "{}");'.format(para_list[0], para_list[1])
                sql_execution(db=mydb, cursor=mycursor, sqls=[sql_1, sql_2])
                mydb.commit()
                close_connection(mydb, mycursor)
        elif choice == 2:
            choice = float(input("Please choose one functionality:\n2.1 Browse all products offered by a specific vendor\n2.2 Insert a new product to vendor's catalog\n"))
            if choice == 2.1:
                prompt_format = PromptFormat()
                prompt_1 = input("Please input the business name (leave it empty if all vendors are chosen): ")
                prompt_1 = prompt_format.prompt_format_2_1(prompt_1)
                prompt_2 = int(input("Please input how many product(s) you want to show: "))
                mydb, mycursor = make_connection()
                sql = """
                      select v.BusinessName, pi.Name, p.tags, pi.description, pi.unitprice
                      from Products p, ProductInfo pi, Vendors v
                      where p.ProductID = pi.ProductID and pi.VendorID = v.VendorID and v.BusinessName like '%""" + prompt_1 + "%' order by v.BusinessName, pi.Name, p.tags;" 
                mycursor.execute(sql)
                df = cursor_to_df(mycursor)
                df_aggregated = df.groupby(['BusinessName', "Name", "description", "unitprice"])['tags'].apply(list).reset_index()
                print(df_aggregated[0: prompt_2])
                close_connection(mydb, mycursor)
            elif choice == 2.2:
                prompt_format = PromptFormat()
                prompt1 = input("Please input the ProductID, ProductName, Description, UnitPrice, and VendorID: ")
                prompt2 = input("Please input 1 to 3 tag(s): ")
                sqls = prompt_format.prompt_format_2_2(prompt1, prompt2)
                print(sqls)
                mydb, mycursor = make_connection()
                sql_execution(db=mydb, cursor=mycursor, sqls=sqls)
                mydb.commit()
                close_connection(mydb, mycursor)
        elif choice == 3:
            choice = float(input("Please choose one functionality:\n3.1 Product Discovery by Tags\n3.2 Product Purchase Record Inspection by CustomerID\n"))
            if choice == 3.1:

                prompt_format = PromptFormat()
                prompt = input("Please input one tag (leave it empty for all tags): ")
                prompt = prompt_format.prompt_format_3_1(prompt)
                sql = """
                select Name, Tags, Description, UnitPrice
                from Products inner join ProductInfo on Products.ProductID = ProductInfo.ProductID
                where Tags like '%""" + prompt + "%' or Name like '%" + prompt + "%' order by Name, Tags;"
                mydb, mycursor = make_connection()
                mycursor.execute(sql)
                df = cursor_to_df(mycursor)
                print(df)
                close_connection(mydb, mycursor)

            elif choice == 3.2:
                prompt_format = PromptFormat()
                prompt = input("Please input one CustomerID (leave it empty for all customers): ")
                prompt = prompt_format.prompt_format_3_2(prompt)
                sql = """
                      with invoice as
                      (select c.CustomerID, o.OrderID, o.PaymentMethod, t.ProductID, t.Quantity, o.DeliveryStatus, o.PaymentTime
                      from Customers c left join Orders o on c.CustomerID = o.CustomerID left join Transactions t on o.OrderID = t.OrderID
                      where c.CustomerID {}),
                      product_service as
                      (select pi.ProductID, pi.Name, pi.Description, pi.UnitPrice, v.VendorID, t.OrderID
                       from ProductInfo pi, Vendors v, Transactions t
                       where pi.VendorID = v.VendorID and pi.ProductID = t.ProductID
                      )
                      select i.CustomerID, i.OrderID, i.PaymentMethod, i.Quantity, i.DeliveryStatus, i.PaymentTime, ps.Name, ps.UnitPrice
                      from invoice i left join product_service ps on i.OrderID = ps.OrderID and i.ProductID = ps.ProductID
                      order by i.CustomerID, i.OrderID, i.PaymentTime DESC;
                      """.format(prompt)
                mydb, mycursor = make_connection()
                mycursor.execute(sql)
                df = cursor_to_df(mycursor)
                print(df)
                close_connection(mydb, mycursor)
        elif choice == 4:
            prompt_format = PromptFormat()
            cust = input("Please input your customer id: ")
            first_Record=True
            mydb, mycursor = make_connection()
            global order_Seq;
            global order_Placed;
            global payMethod;
            order_Placed=False
                    
            while True:
                tags = input("Please input one tag (leave it empty for all tags): ")
                
                sql = """
                      select ProductInfo.Productid, Name
                      , GROUP_CONCAT(Products.Tags SEPARATOR ', ') as Tag_Concat
                      , Description, UnitPrice
                      from Products inner join ProductInfo on Products.ProductID = ProductInfo.ProductID
                      where Tags like '%""" + tags + "%' " +"or name like '%" +tags+ "%' group by ProductInfo.Productid, Name, Description, UnitPrice order by Name ;"
                    # print(sql)
                
                mycursor.execute(sql)
                df = cursor_to_df(mycursor)
                print(df)
                
                prompt = input("Please input product id, quantity or exit() to end order: ")
                para_list = prompt_format.prompt_format_4_1(prompt)
                if("exit()"==para_list[0]):
                    break
                else:
                    sql_2 = 'INSERT ORDERS (CustomerID) VALUES ("{}");'.format(cust)
                    sql_3 = 'SELECT LAST_INSERT_ID();'
                    #print(sql_2)
                    if(first_Record):
                        mydb, mycursor = make_connection()
                        mycursor.execute(sql_2)
                        mycursor.execute(sql_3)
                        myresult = mycursor.fetchone() 
                        order_Seq = myresult[0]
                        sql_4 = 'INSERT Transactions (OrderID,ProductID,Quantity) VALUES ("{}", "{}", "{}");'.format(order_Seq, para_list[0], para_list[1])
                        
                        #print(sql_4)
                        mycursor.execute(sql_4)
                        first_Record=False
                        order_Placed=True
                    else:
                        sql_4 = 'INSERT Transactions (OrderID,ProductID,Quantity) VALUES ("{}", "{}", "{}");'.format(order_Seq, para_list[0], para_list[1])
                        #print(sql_4)
                        mycursor.execute(sql_4)
            if(order_Placed):            
                print("Please input Payment method: \n1. Apple Pay, \n2. Visa, \n3: Master \n4: Paypal\n")            
                payment = input("Please choose one Payment method (1 to 4): ")
                
                if "1"==payment:
                    payMethod="Apple Pay"
                elif "2"==payment:
                    payMethod="Visa"
                elif "3"==payment:
                    payMethod="Master"
                elif "4"==payment:
                    payMethod="Paypal"
                sql_5 = "Update Orders Set PaymentMethod=%s, DeliveryStatus='Paid', PaymentTime=now() where OrderID=%s"
                
                val_5 = (payMethod, order_Seq)
                mycursor.execute(sql_5, val_5)
            
            mydb.commit()
            close_connection(mydb, mycursor)
        elif choice == 5:
            prompt_format = PromptFormat()
            cust = input("Please input your customer id: ")
            sql = """
            select CustomerID, OrderID , PaymentMethod , DeliveryStatus , PaymentTime  
            from orders ord 
            where CustomerID = """ + cust + " order by PaymentTime desc;"
            # print(sql)
            mydb, mycursor = make_connection()
            mycursor.execute(sql)
            df = cursor_to_df(mycursor)
            print(df)
            
            choice = float(input("Please choose one functionality:\n5.1 Cancel Order:\n5.2 modify order: "))
            if choice == 5.1:
   
                prompt_format = PromptFormat()
                prompt = input("Please input the Order ID for cancel: ")
                sql = """
                delete from orders where orderid= """ + prompt + ";"
                print(sql)
                mydb, mycursor = make_connection()
                mycursor.execute(sql)
                mydb.commit()
                close_connection(mydb, mycursor)
          
            elif choice == 5.2:
                prompt_format = PromptFormat()
                orderId = input("Please input one order ID: ")
                sql_1 = """
                      select t.transactionID,t.OrderID,t.ProductID,p.Name, t.Quantity 
                      from transactions t
                      ,productinfo p 
                      where t.ProductID =p.ProductID
                      and t.OrderID = """ + orderId + " order by t.transactionID;"
                # print(sql)
                mydb, mycursor = make_connection()
                mycursor.execute(sql_1)
                df = cursor_to_df(mycursor)
                print(df)
                prompt_format = PromptFormat()
                prompt = input("Please input the transaction ID for remove: ")
                sql_2 = """
                      select count(*)
                      from transactions t
                      ,productinfo p 
                      where t.ProductID =p.ProductID
                      and t.OrderID = """ + orderId + ";"
                mycursor.execute(sql_2)
                myresult = mycursor.fetchone() 
                print(myresult[0]) 
        
                sql_3 = """
                      delete from transactions t
                      where t.transactionID = """ + prompt + " ;"
                sql_4 = """
                delete from orders where orderid= """ + orderId + ";"
                if(myresult[0]==1):
                    sqls = [sql_3, sql_4]
                    mydb, mycursor = make_connection()
                    sql_execution(db=mydb, cursor=mycursor, sqls=sqls)
                    mydb.commit()
                elif (myresult[0]>1):
                    mydb, mycursor = make_connection()
                    mycursor.execute(sql_3)
                    mydb.commit()
                close_connection(mydb, mycursor)
    except ValueError:
        print("Please input a number.")
        continue
