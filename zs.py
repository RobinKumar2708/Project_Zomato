import streamlit as st
import pandas as pd
import pymysql

# Function to establish database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Umaneethi@123", 
        database="zomato_deliveries"
    )

# Dictionary of queries
queries = {
    "Find the top 5 customers who placed the most orders.": """
        SELECT c.customer_id, c.name, COUNT(o.order_id) AS total_orders 
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id 
        GROUP BY c.customer_id, c.name 
        ORDER BY total_orders DESC 
        LIMIT 5;
    """,
    "Find the most popular cuisine type among premium customers.": """
        SELECT preferred_cuisine, COUNT(*) AS count 
        FROM Customers 
        WHERE is_premium = 1 
        GROUP BY preferred_cuisine 
        ORDER BY count DESC 
        LIMIT 1;
    """,
    "Find the top 3 highest-rated restaurants.": """
        SELECT name, rating 
        FROM Restaurants 
        ORDER BY rating DESC 
        LIMIT 3;
    """,
    "Find the top 5 customers who have spent the most money.": """
        SELECT c.customer_id, c.name, SUM(o.total_amount) AS total_spent
        FROM Orders o
        JOIN Customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 5;
    """,
    "Find the number of orders per payment mode.": """
        SELECT payment_mode, COUNT(*) AS total_orders 
        FROM Orders 
        GROUP BY payment_mode;
    """,
    "Identify customers who have not placed any orders.": """
        SELECT c.customer_id, c.name 
        FROM Customers c 
        LEFT JOIN Orders o ON c.customer_id = o.customer_id 
        WHERE o.order_id IS NULL;
    """,
    "Find the most common delivery status.": """
        SELECT delivery_status, COUNT(*) AS count 
        FROM Deliveries 
        GROUP BY delivery_status 
        ORDER BY count DESC 
        LIMIT 1;
    """,
    "Find the top 3 most frequent customers (by order count).": """
        SELECT c.customer_id, c.name, COUNT(o.order_id) AS total_orders
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_orders DESC
        LIMIT 3;
    """,
    "Identify the busiest delivery person.": """
        SELECT d.delivery_person_id, d.name, COUNT(*) AS total_deliveries 
        FROM Deliveries del
        JOIN DeliveryPersons d ON del.delivery_person_id = d.delivery_person_id
        GROUP BY d.delivery_person_id, d.name 
        ORDER BY total_deliveries DESC 
        LIMIT 1;
    """,
    "Find the restaurant with the best average feedback rating.": """
        SELECT r.name, AVG(o.feedback_rating) AS avg_rating
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        GROUP BY r.name
        ORDER BY avg_rating DESC
        LIMIT 1;
    """,
    "Find the highest-rated delivery person.": """
        SELECT name, average_rating 
        FROM DeliveryPersons 
        ORDER BY average_rating DESC 
        LIMIT 1;
    """,
    "Identify the average discount applied per order.": """
        SELECT AVG(discount_applied) AS avg_discount 
        FROM Orders;
    """,
    "Find the total revenue generated by each payment mode.": """
        SELECT payment_mode, SUM(total_amount) AS total_revenue
        FROM Orders
        GROUP BY payment_mode
        ORDER BY total_revenue DESC;
    """,
    "Find the delivery person who has delivered the most orders.": """
        SELECT d.delivery_person_id, d.name, COUNT(del.delivery_id) AS total_deliveries
        FROM Deliveries del
        JOIN DeliveryPersons d ON del.delivery_person_id = d.delivery_person_id
        GROUP BY d.delivery_person_id, d.name
        ORDER BY total_deliveries DESC
        LIMIT 1;
    """,
    "Identify customers who have placed orders at more than 3 different restaurants.": """
        SELECT c.customer_id, c.name, COUNT(DISTINCT o.restaurant_id) AS unique_restaurants 
        FROM Orders o
        JOIN Customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name 
        HAVING unique_restaurants > 3;
    """,
    "Find the busiest time period (hour) for order placements.": """
        SELECT HOUR(order_date) AS order_hour, COUNT(*) AS order_count 
        FROM Orders 
        GROUP BY order_hour 
        ORDER BY order_count DESC 
        LIMIT 1;
    """,
    "Find customers who have given an average rating above 4.5.": """
        SELECT c.name, AVG(o.feedback_rating) AS avg_rating 
        FROM Orders o
        JOIN Customers c ON o.customer_id = c.customer_id
        GROUP BY c.name 
        HAVING avg_rating > 4.5;
    """,
    "Calculate total revenue per restaurant.": """
        SELECT r.name, SUM(o.total_amount) AS total_revenue 
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        GROUP BY r.name 
        ORDER BY total_revenue DESC;
    """,
    "Find the restaurant with the highest repeat customer rate.": """
        SELECT r.name, 
               COUNT(o.customer_id) AS total_orders, 
               COUNT(DISTINCT o.customer_id) AS unique_customers,
               (COUNT(o.customer_id) / COUNT(DISTINCT o.customer_id)) AS repeat_rate
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        GROUP BY r.name
        ORDER BY repeat_rate DESC
        LIMIT 1;
    """
}

# Function to execute query
def execute_query(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            return pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        else:
            st.warning("No data found.")
            return pd.DataFrame()  # Return empty DataFrame if no data
    except pymysql.MySQLError as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

# Streamlit Layout
st.set_page_config(layout="wide", page_title="Zomato Deliveries Dashboard")
st.title("🍔 Zomato Deliveries Dashboard 🍕")

# Sidebar with query selection
selected_query = st.sidebar.radio("🔍 Choose a Query:", list(queries.keys()))

# Dashboard Metrics
col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Orders", "12,450")
col2.metric("⏳ Avg. Delivery Time", "28 min")
col3.metric("⭐ Customer Rating", "4.5")

# Automatically execute and display selected query
query = queries[selected_query]
df = execute_query(query)
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🔍 Selected Query:")
    st.write(f"**{selected_query}**")

with col2:
    if not df.empty:
        # Display data as a table
        st.dataframe(df)
        if "total_orders" in df.columns or "total_revenue" in df.columns:
            st.bar_chart(df.set_index(df.columns[0]))  # Bar chart for numerical data
    else:
        st.warning("No data to display.")
