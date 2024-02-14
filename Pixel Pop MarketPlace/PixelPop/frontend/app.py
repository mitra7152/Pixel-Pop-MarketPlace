from flask import Flask, render_template, request, redirect
import mysql.connector
from mysqlx import IntegrityError

app = Flask(__name__,template_folder='template')

# Connect to your MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="milo",
    database="sql_users"
)

mydb1 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="milo",
    database="sql_Inventory"
)

mydb2 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="milo",
    database="sql_RetailStore"
)

mydb3 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="milo",
    database="delivery_assignment"
)


@app.route('/')
def index():
    # Display the name of the retail store and a login button
    return render_template('index2.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the username, password, and type entered by the user
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['type']
        # Check the user's credentials against the database
        cursor = mydb.cursor()
        if user_type == 'admin':
            query = "SELECT * FROM admin WHERE user_id = %s AND password = %s"
            values = (username, password)
            cursor.execute(query, values)
            admin = cursor.fetchone()
            # print(admin)
            if admin:
                # Admin has successfully logged in                
                return redirect('/admin')
            else:
                # Incorrect username or password
                return render_template('login.html', error='Invalid credentials')
        else:
            query = "SELECT * FROM user WHERE user_id = %s AND password = %s AND type = %s"
            values = (username, password, user_type)
            cursor.execute(query, values)
            user = cursor.fetchone()
            if user:
                # User has successfully logged in
                # Check the type of user and redirect to the appropriate page
                if user_type == 'customer':
                    return redirect('/customer')
                elif user_type == 'supplier':
                    return redirect('/supplier')
                elif user_type == 'delivery executive':
                    return redirect('/delivery')
            else:
                # Incorrect username, password, or user type
                return render_template('login - Copy.html', error='Invalid credentials')
    else:
        # Display the login form
        return render_template('login - Copy.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Display the admin page
    cursor = mydb1.cursor()
    
    if request.method == 'POST':
        if 'int' in request.form:
            return redirect('/inventory')
        
        if 'cust' in request.form:
            return redirect('/customer_adm')
        
        if 'back' in request.form:
            return redirect('/login')
    return render_template('admin.html')


@app.route('/customer_adm',methods=['GET','POST'])
#customer page on the admin log in
def customer_adm():
    cursor = mydb.cursor()
    query = "select customer_id, customer_name,customer_email from customer"
    if  request.method == 'POST':
        if 'netRevenue' in request.form:
            return redirect('/netrevenue')        
        if 'profit' in request.form:
            return redirect('/profitt')        
        if 'back' in request.form:
            return redirect('/admin')
        if 'search_button' in request.form:
            search_result = request.form['search']
            query = "SELECT customer_id, customer_name,customer_email FROM customer WHERE customer_name LIKE %s"
            values = (f'%{search_result}%',)
            cursor.execute(query, values)
            final = cursor.fetchall()
            # print(final)
            return render_template('customer_admin.html', cursor=final)
        if 'clearFilters' in request.form:
            cursor.execute(query)
            return render_template('customer_admin.html', cursor=cursor)
    else:              
        cursor.execute(query)
        return render_template('customer_admin.html',cursor = cursor)

@app.route('/profitt', methods=['GET', 'POST'])
#Profit earned from orders and total revenue 
def profitt():
    cursor = mydb.cursor()
    query = '''SELECT uo.user_order_id,SUM(
  uo.product_quantity * p.Price) 
  AS Total_Revenue,SUM(
  uo.product_quantity * (p.Price - (p.Price * 0.2)))
  AS Total_Profit
FROM sql_RetailStore.user_order uo
JOIN sql_Inventory.Product p ON uo.Product_ID = p.Product_ID
GROUP BY uo.user_order_id;'''
    if 'goback' in request.form:
        return redirect('/customer_adm')
    cursor.execute(query)
    return render_template('profit.html',cursor=cursor)

@app.route('/netrevenue', methods=['GET', 'POST'])
#Revenue earned by each customer
def netrevenue():
    cursor = mydb2.cursor()
    query = '''SELECT customer_id, SUM(total_cost) as total_revenue
FROM sql_RetailStore.user_order
INNER JOIN sql_RetailStore.placed_order ON sql_RetailStore.user_order.user_order_id = sql_RetailStore.placed_order.user_order_id
INNER JOIN sql_RetailStore.bill_details ON sql_RetailStore.placed_order.bill_ID = sql_RetailStore.bill_details.bill_id
GROUP BY customer_id;'''
    if 'goback' in request.form:
        return redirect('/customer_adm')
    cursor.execute(query)
    return render_template('netrevenue.html',cursor=cursor)


@app.route('/inventory', methods=['GET', 'POST'])
#inventory on admin page category and back only works
def inventory():
    if request.method == 'POST':
        if 'category' in request.form:
            return redirect('/category')
        if 'back' in request.form:
            return redirect('/admin')
        if 'products' in request.form:
            return redirect('/product_adm')
    else:
        return render_template('inventory.html')

@app.route('/product_adm',methods = ['GET','POST'])
def product():
    cursor = mydb1.cursor()
    query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price,Quantity FROM product"
    if request.method == 'POST':
        if 'filter' in request.form:
            category_id = request.form['product']
            # price = request.form['price']
            query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price,Quantity FROM product where Product_ID = %s"
            values = (category_id,)
            cursor.execute(query,values)
            return render_template('products2.html', cursor=cursor)
        if 'search_button' in request.form:
            search_result = request.form['search']
            query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price,Quantity FROM product WHERE Product_Name LIKE %s"
            values = (f'%{search_result}%',)
            cursor.execute(query, values)
            final = cursor.fetchall()
            # print(final)
            return render_template('products2.html', cursor=final)
        if 'clearFilters' in request.form:
            cursor.execute(query)
            return render_template('products2.html', cursor=cursor)
        if 'back' in request.form:
            return redirect('/inventory')
    else:
        cursor.execute(query)
        return render_template('products2.html', cursor=cursor)
    
@app.route('/category',methods=['GET','POST'])
#category manage in inventory
def category():
    cursor = mydb1.cursor()
    query = "select * from Category"
    if request.method == 'POST':
        if 'go_back' in request.form:
            return redirect('/inventory')
        if 'earning' in request.form:
            return redirect('/earning')
    else:        
        cursor.execute(query)
        return render_template('category_admin.html',cursor = cursor)
    
@app.route('/earning', methods =['GET','POST'])
#earnings fromc ategory
def earning():
    cursor = mydb1.cursor()
    query = '''SELECT sql_Inventory.Category.Category_Name, SUM(total_cost) as total_revenue
FROM sql_RetailStore.user_order
INNER JOIN sql_Inventory.Product ON sql_RetailStore.user_order.Product_ID = sql_Inventory.Product.Product_ID
INNER JOIN sql_Inventory.Category ON sql_Inventory.Product.Category_ID = sql_Inventory.Category.Category_ID
INNER JOIN sql_RetailStore.placed_order ON sql_RetailStore.user_order.user_order_id = sql_RetailStore.placed_order.user_order_id
INNER JOIN sql_RetailStore.bill_details ON sql_RetailStore.placed_order.bill_ID = sql_RetailStore.bill_details.bill_id
GROUP BY sql_Inventory.Category.Category_Name;'''
    if request.method == 'POST':
        if 'goback' in request.form:
            return redirect('/category')
    else:
        cursor.execute(query)
        return render_template('earnings.html',cursor=cursor)

@app.route('/customer',methods = ['GET','POST'])
def customer():
    # Display the customer page
    cursor = mydb1.cursor()
    query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price FROM product"
    if request.method == 'POST':
        if 'filter' in request.form:
            category_id = request.form['category']
            price = request.form['price']
            query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price FROM product where Category_ID = %s and Price>%s"
            values = (category_id,price)
            cursor.execute(query,values)
            final = cursor.fetchall()
            return render_template('products.html', cursor=final)
        if 'search_button' in request.form:
            search_result = request.form['search']
            query = "SELECT Product_id,Category_ID, Product_Name, Product_Description, Price FROM product WHERE Product_Name LIKE %s"
            values = (f'%{search_result}%',)
            cursor.execute(query, values)
            final = cursor.fetchall()
            # print(final)
            return render_template('products.html', cursor=final)
        if 'clearFilters' in request.form:
            cursor.execute(query)
            return render_template('products.html', cursor=cursor)
        if 'top10' in request.form:
            return redirect('/top10')
        if 'logout' in request.form:
            return redirect('/login')
        if 'viewCart' in request.form:
            return redirect('/cart')
    else:
        cursor.execute(query)
        return render_template('products.html', cursor=cursor)


@app.route('/cart',methods=['GET','POST'])
def cart():
    cursor = mydb2.cursor()
    query = "select customer_ID,Product_ID,Product_quantity,total_cost from cart_details where customer_ID = 'aa'"
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect('/customer')
        if 'payment' in request.form:
            return redirect('/payment')
    else:
        cursor.execute(query)
        return render_template('cart.html',cursor = cursor)

@app.route('/payment',methods=['GET','POST'])
def payment():
    cursor = mydb2.cursor()
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect('/cart')
        if 'submit' in request.form:   
            name = request.form['card_name']
            card_no = request.form['card_number']
            cvv = request.form['cvv']
            ed = request.form['expiry_date']    
            query = "INSERT INTO payment (payment_id,card_name, card_number, cvv, expiry_date) VALUES ('8a2F5J9E4',%s, %s, %s, %s)"
            values = (name,card_no,cvv,ed) 
            try:
                cursor.execute(query, values)
                mydb2.commit()
                return render_template('payment.html',error = "Entered succesfully")
            except mysql.connector.Error as e:
                return render_template('payment.html',error = str(e))
    else:
        return render_template('payment.html')
            

@app.route('/supplier', methods=['GET', 'POST'])
def supplier():
    # Display the customer page
    cursor = mydb1.cursor()
    query = "SELECT Product_id, Category_ID, Product_Name, Product_Description, Price FROM product"
    if request.method == 'POST':
        if 'filter' in request.form:
            category_id = request.form['category']
            price = request.form['price']
            query = "SELECT Product_id, Category_ID, Product_Name, Product_Description, Price FROM product WHERE Category_ID = %s AND Price > %s"
            values = (category_id, price)
            cursor.execute(query, values)
            final = cursor.fetchall()
            return render_template('products1.html', cursor=final)
        if 'search_button' in request.form:
            search_result = request.form['search']
            query = "SELECT Product_id, Category_ID, Product_Name, Product_Description, Price FROM product WHERE Product_Name LIKE %s"
            values = (f'%{search_result}%',)
            cursor.execute(query, values)
            final = cursor.fetchall()
            return render_template('products1.html', cursor=final)
        if 'clearFilters' in request.form:
            cursor.execute(query)
            final = cursor.fetchall()
            return render_template('products1.html', cursor=final)
        if 'logout' in request.form:
            return redirect('/login')
        if 'add' in request.form:
            p_id = request.form.get('add')
            quantity = request.form['quantity']
            query1 = "UPDATE sql_inventory.product SET quantity = %s WHERE Product_id = %s;"
            values = (quantity, p_id)
            try:
                cursor.execute(query1, values)
                mydb1.commit()
                cursor.execute(query)
                final = cursor.fetchall()
                return render_template('products1.html', cursor=final)
            except mysql.connector.Error as e:
                cursor.execute(query)
                final = cursor.fetchall()
                return render_template('products1.html', cursor=final,error = str(e))
    else:
        cursor.execute(query)
        final = cursor.fetchall()
        return render_template('products1.html', cursor=final)

    

@app.route('/customer_admin')
def customer_admin():
    # Display the supplier page
    return render_template('customer_admin.html')
@app.route('/delivery')
def delivery():
    # Display the delivery executive page
    return render_template('delivery.html')

@app.route('/top10',methods=['GET','POST'])
def top10():
    if request.method == 'POST':
        return redirect('/customer')
    else:
        cursor = mydb1.cursor()
        query = '''SELECT Product_Name, SUM(product_quantity) as total_quantity_sold
    FROM sql_RetailStore.user_order
    INNER JOIN sql_Inventory.Product ON sql_RetailStore.user_order.Product_ID = sql_Inventory.Product.Product_ID
    GROUP BY Product_Name
    ORDER BY total_quantity_sold DESC
    LIMIT 10;'''
        cursor.execute(query)
        return render_template('top10.html',cursor=cursor)

if __name__ == '__main__':
    app.run(debug=True)
