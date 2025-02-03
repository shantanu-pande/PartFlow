# import streamlit as st



# # Streamlit Interface for User Creation
# st.title("Create New User")
# user_id = st.text_input("User ID")
# name = st.text_input("Name")
# password = st.text_input("Password", type="password")
# role = st.selectbox("Role", ["Manager", "Admin", "User"])

# if st.button("Create User"):
#     if user_id and name and password:
#         result = create_user(user_id, name, password, role)
#         if result.get("success"):
#             st.success(result["message"])
#         else:
#             st.error("Failed to create user!")
#     else:
#         st.error("All fields are required!")



import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import bcrypt
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxnFXCqYbbSfFZjT2wOUe2v9innSydVQC5Ekv7OP2nADWvvgcuyMpSr--luVUNeQGMU3g/exec"

class ComponentManagementSystem:
    def __init__(self):
        self.selected_menu = None
        self.pageIcon ='''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-kanban" viewBox="0 0 16 16"><path d="M13.5 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zm-11-1a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/><path d="M6.5 3a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm-4 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm8 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1z"/></svg>'''
        self.pageTitle = "Component Management System"
        self.hide_decoration_bar_style = '''<style>header {visibility: hidden;}</style>'''
        self.menu_title = "Menu"
        self.admin_menu_options = ["Components List", 'Issue Component', "Return Component", "User Enqury",'Add Component', 'Add User']
        self.admin_menu_icons = ['list-task', 'pencil-square', 'arrow-clockwise', 'person-lines-fill','plus-circle-fill', 'person-plus-fill']
        self.user_menu_options = ["Components List", 'Issue Component', "User Enqury"]
        self.user_menu_icons = ['list-task', 'pencil-square', 'person-lines-fill']
        st.set_page_config(page_title=self.pageTitle, page_icon=self.pageIcon)
        st.markdown(self.hide_decoration_bar_style, unsafe_allow_html=True)

    def run(self):
        if 'logged_in' not in st.session_state or 'role' not in st.session_state:
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            
        if not st.session_state['logged_in'] or st.session_state['role'] == None:
            self.show_login_form()
        else:
            self.after_login_render()

    def show_login_form(self):
        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("User ID")
            password = st.text_input("Password", type="password") 
            
            # Submit button inside form
            if st.form_submit_button("Login"):
                data = self.validate_credentials(username, password)
                if data.get("success"):
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = data.get("role")
                    st.success(f"Login as {data.get('role')}")
                else:
                    st.error("Invalid credentials")


    def after_login_render(self):
        with st.sidebar:
            st.image("logo.png", width=270)
            if st.session_state['role'] == "Admin":
                self.selected_menu = option_menu(
                    menu_title=self.adminmenu_title,
                    options=self.menu_options,
                    icons=self.menu_icons
                )

    def validate_credentials(self, username, password):
        data = {
            "action": "validateCredentials",
            "data": {
                "username": username,
                "password": password
            }
        }
        response = requests.post(WEB_APP_URL, json=data)
        print(response.json())
        return response.json()
    
    def create_user(self, user_id, name, password, role):
        data = {
            "action": "createUser",
            "data": {
                "userId": user_id,
                "name": name,
                "password": password,
                "role": role
            }
        }
        response = requests.post(WEB_APP_URL, json=data)
        return response.json()


if __name__ == '__main__':
    app = ComponentManagementSystem()
    app.run()