import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import uuid

# Database
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

# Modern Dark Theme with Gold Accents
st.markdown("""
<style>
    .main {background-color: #0a0a0a; color: #ffffff;}
    h1 {color: #ffcc00; font-size: 2.5rem; text-align: center;}
    .stTabs [data-baseweb="tab"] {background-color: #1f1f1f; border-radius: 12px;}
    .stButton>button {background-color: #ffcc00; color: black; font-weight: bold; border-radius: 10px;}
    .success {color: #00ff9d;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="PonyBoys Detailing", layout="centered", page_icon="🚗")

st.title("🚗 PonyBoys Detailing")
st.markdown("**Premium Mobile Car Detailing • Fontana, CA**")

tab1, tab2, tab3 = st.tabs(["👥 Customers", "📅 Schedule Appointment", "📆 Today's Schedule"])

with tab1:
    st.subheader("Add New Customer")
    with st.form("new_customer", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        email = col2.text_input("Email")
        col3, col4 = st.columns(2)
        year = col3.text_input("Vehicle Year")
        make = col4.text_input("Make")
        model = st.text_input("Model")
        birthday = st.date_input("Birthday", value=date(1995,1,1))
        
        if st.form_submit_button("Save Customer") and name:
            cid = str(uuid.uuid4())
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", 
                     (cid, name, year, make, model, email, str(birthday)))
            conn.commit()
            st.success(f"✅ {name} saved successfully!")

    st.subheader("All Customers")
    df = pd.read_sql("SELECT name as Name, vehicle_year||' '||vehicle_make||' '||vehicle_model as Vehicle, email as Email FROM customers", conn)
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Schedule New Appointment")
    customers = pd.read_sql("SELECT id, name FROM customers", conn)
    customer_list = ["New Customer"] + customers['name'].tolist()
    
    with st.form("new_appointment", clear_on_submit=True):
        selected = st.selectbox("Select Customer", customer_list)
        if selected == "New Customer":
            cust_name = st.text_input("Customer Name")
            vehicle = st.text_input("Vehicle (Year Make Model)")
        else:
            cust_name = selected
            vehicle = ""
        
        col1, col2 = st.columns(2)
        app_date = col1.date_input("Date", value=date.today())
        app_time = col2.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
        
        service = st.selectbox("Service Package", [
            "Signature Wash & Interior",
            "Full Premium Detail",
            "Ceramic Coating Package",
            "Cybertruck Full Restoration"
        ])
        notes = st.text_area("Notes / Special Requests")
        
        if st.form_submit_button("Confirm Booking"):
            app_id = str(uuid.uuid4())
            if selected == "New Customer":
                cid = str(uuid.uuid4())
                c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", (cid, cust_name, "", "", vehicle, "", ""))
            else:
                cid = customers[customers['name'] == cust_name]['id'].iloc[0]
            
            c.execute("INSERT INTO appointments VALUES (?,?,?,?,?,?,?)", 
                     (app_id, cid, str(app_date), str(app_time), service, notes, "Scheduled"))
            conn.commit()
            st.success(f"✅ Booking confirmed for {cust_name}!")

with tab3:
    st.subheader(f"📅 Today's Schedule — {date.today().strftime('%B %d, %Y')}")
    today = pd.read_sql("""
        SELECT a.app_time as Time, c.name as Customer, a.service_type as Service 
        FROM appointments a 
        JOIN customers c ON a.customer_id = c.id 
        WHERE a.app_date = ?
        ORDER BY a.app_time
    """, conn, params=(str(date.today()),))
    
    if not today.empty:
        st.dataframe(today, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments scheduled for today.")

st.caption("PonyBoys Detailing • Premium Mobile Service")
