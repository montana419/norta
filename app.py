import streamlit as st
import pandas as pd
import database as db
import atlas_tools as tools
from cli_parser import parse_user_intent

# --- Page Configuration ---
st.set_page_config(
    page_title="Atlas Agent | Founder Executive Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
db.init_db()

# --- Sidebar Configuration ---
st.sidebar.title("🛡️ Atlas Agent")
st.sidebar.caption("OKX AI Marketplace Skill Edition")

client_name = st.sidebar.text_input("Active Client / Organization", value="Default Client")

st.sidebar.divider()
st.sidebar.markdown("### 📊 Status & Metrics")
tasks_data = db.get_tasks(client_name)
employees_data = db.get_all_employees(client_name)

st.sidebar.metric("Active Tasks", len(tasks_data))
st.sidebar.metric("Registered Personnel", len(employees_data))

st.sidebar.divider()
st.sidebar.info("💡 **OKX Skill Status:** Active\n\nDirectly handles Gemini parsing, SQLite persistence, and executive workflows.")

# --- Main App Header ---
st.title("🤖 Executive AI Assistant Dashboard")
st.caption(f"Connected Context: **{client_name}**")

# --- Tabs Navigation ---
tab_chat, tab_tasks, tab_employees, tab_wellness = st.tabs([
    "💬 AI Command Chat", 
    "📋 Task Board", 
    "👥 Personnel Directory", 
    "🧘 Founder Wellness"
])

# ==========================================
# TAB 1: AI COMMAND CHAT
# ==========================================
with tab_chat:
    st.subheader("Natural Language Action Engine")
    st.write("Talk to Atlas in plain English to execute tasks, register employees, or analyze routines.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input Box
    user_prompt = st.chat_input("E.g., 'Add high priority task to review pitch deck' or 'Register Alex as Developer'")
    
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Atlas is parsing intent with Gemini..."):
                try:
                    plan = parse_user_intent(user_prompt, client_name=client_name)
                    responses = []

                    for action in plan.actions:
                        act_type = action.action

                        if act_type == "add_task":
                            res = db.add_task(client_name, action.title, action.priority)
                            msg = f"✅ **Task Added:** '{action.title}' (Priority: {action.priority})"
                            st.success(msg)
                            responses.append(msg)

                        elif act_type == "register_employee":
                            emp_id = db.register_employee(client_name, action.name, action.role, action.salary)
                            msg = f"👤 **Registered Personnel:** {action.name} ({action.role}) - ID #{emp_id}"
                            st.success(msg)
                            responses.append(msg)

                        elif act_type == "list_tasks":
                            msg = f"📋 Fetched active tasks for `{client_name}`."
                            st.info(msg)
                            responses.append(msg)

                        elif act_type == "general_chat":
                            st.write(action.reply)
                            responses.append(action.reply)

                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": "\n\n".join(responses) if responses else "Action executed successfully."
                    })

                except Exception as e:
                    err_msg = f"⚠️ **Error executing prompt:** {str(e)}"
                    st.error(err_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": err_msg})

# ==========================================
# TAB 2: TASK BOARD
# ==========================================
with tab_tasks:
    st.subheader(f"Task List ({client_name})")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        if tasks_data:
            df_tasks = pd.DataFrame(tasks_data)
            st.dataframe(df_tasks, use_container_width=True)
        else:
            st.info("No tasks recorded for this client yet.")

    with col2:
        st.markdown("#### Quick Add Task")
        with st.form("quick_task_form"):
            t_title = st.text_input("Task Title")
            t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            submitted = st.form_submit_button("Add Task")
            
            if submitted and t_title:
                db.add_task(client_name, t_title, t_priority)
                st.success(f"Added task: {t_title}")
                st.rerun()

# ==========================================
# TAB 3: PERSONNEL DIRECTORY
# ==========================================
with tab_employees:
    st.subheader(f"Personnel & Contractors ({client_name})")

    col_emp1, col_emp2 = st.columns([2, 1])

    with col_emp1:
        if employees_data:
            df_employees = pd.DataFrame(employees_data)
            st.dataframe(df_employees, use_container_width=True)
        else:
            st.info("No personnel registered for this client yet.")

    with col_emp2:
        st.markdown("#### Register Employee")
        with st.form("quick_emp_form"):
            e_name = st.text_input("Full Name")
            e_role = st.text_input("Role / Job Title")
            e_salary = st.number_input("Monthly Compensation ($)", min_value=0.0, value=5000.0)
            emp_submitted = st.form_submit_button("Register Employee")

            if emp_submitted and e_name:
                db.register_employee(client_name, e_name, e_role, e_salary)
                st.success(f"Registered {e_name} successfully.")
                st.rerun()

# ==========================================
# TAB 4: FOUNDER WELLNESS
# ==========================================
with tab_wellness:
    st.subheader("Bio-Hacking & Performance Specialist")
    st.write("Analyze founder metrics to get direct, high-impact advice from Atlas.")

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        sleep = st.slider("Sleep Hours", 0.0, 12.0, 6.5, step=0.5)
    with col_w2:
        work = st.slider("Work Hours", 0.0, 18.0, 10.0, step=0.5)
    with col_w3:
        stress = st.slider("Stress Level (1-10)", 1, 10, 7)

    if st.button("🚀 Generate Performance Optimization Routine"):
        with st.spinner("Calculating performance metrics..."):
            advice = tools.get_health_advice(
                sleep_hours=sleep,
                work_hours=work,
                stress_level=stress,
                client_name=client_name
            )
            st.markdown("### Optimization Plan")
            st.info(advice)