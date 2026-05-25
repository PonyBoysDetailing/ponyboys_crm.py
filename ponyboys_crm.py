import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import uuid

conn = sqlite3.connect('/tmp/ponyboys_detailing.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY, name TEXT, vehicle_year TEXT, 
    vehicle_make TEXT, vehicle_model TEXT, email TEXT, birthday TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY, customer_id TEXT, app_date TEXT, 
    app_time TEXT, service_type TEXT, notes TEXT, status TEXT DEFAULT 'Scheduled'
)''')
conn.commit()

st.set_page_config(page_title="PonyBoys Detailing", layout="centered")
st.title("🚗 PonyBoys Detailing CRM")
st.markdown("**Mobile Detailing • Fontana, CA**")

tab1, tab2, tab3 = st.tabs(["📇 Customers", "📅 Book Appointment", "📆 Today's Schedule"])

with tab1:
    st.subheader("Add New Customer")
    with st.form("new_customer", clear_on_submit=True):
        name = st.text_input("Full Name *")
        col1, col2 = st.columns(2)
        year = col1.text_input("Vehicle Year")
        make = col2.text_input("Make")
        model = st.text_input("Model")
        email = st.text_input("Email")
        birthday = st.date_input("Birthday", value=date(1995,1,1))
        
        if st.form_submit_button("Save Customer") and name:
            cid = str(uuid.uuid4())
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", 
                     (cid, name, year, make, model, email, str(birthday)))
            conn.commit()
            st.success(f"✅ {name} saved!")

    st.subheader("All Customers")
    df = pd.read_sql("SELECT name, vehicle_year || ' ' || vehicle_make || ' ' || vehicle_model as Vehicle, email FROM customers", conn)
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Schedule New Appointment")
    customers = pd.read_sql("SELECT id, name FROM customers", conn)
    customer_list = ["New Customer"] + customers['name'].tolist()
    
    with st.form("new_appointment", clear_on_submit=True):
        selected = st.selectbox("Select Customer", customer_list)
        if selected == "New Customer":
            cust_name = st.text_input("Customer Name")
            vehicle = st.text_input("Vehicle Info")
        else:
            cust_name = selected
            vehicle = ""
        
        app_date = st.date_input("Date", value=date.today())
        app_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
        service = st.selectbox("Service", ["Basic Wash", "Full Detail", "Premium Detail + Ceramic", "Cybertruck Detail"])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Schedule"):
            app_id = str(uuid.uuid4())
            if selected == "New Customer":
                cid = str(uuid.uuid4())
                c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", (cid, cust_name, "", "", vehicle, "", ""))
            else:
                cid = customers[customers['name'] == cust_name]['id'].iloc[0]
            
            c.execute("INSERT INTO appointments VALUES (?,?,?,?,?,?,?)", 
                     (app_id, cid, str(app_date), str(app_time), service, notes, "Scheduled"))
            conn.commit()
            st.success("✅ Appointment Scheduled!")

with tab3:
    st.subheader(f"Today — {date.today()}")
    today = pd.read_sql("""
        SELECT a.app_time as Time, c.name as Customer, a.service_type as Service 
        FROM appointments a JOIN customers c ON a.customer_id = c.id 
        WHERE a.app_date = ?
    """, conn, params=(str(date.today()),))
    st.dataframe(today, use_container_width=True, hide_index=True)

st.caption("PonyBoys Detailing CRM")
