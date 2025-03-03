
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import bcrypt
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxnFXCqYbbSfFZjT2wOUe2v9innSydVQC5Ekv7OP2nADWvvgcuyMpSr--luVUNeQGMU3g/exec"
# WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzMVuIUkRuYtBoVu8iXy4OUXsa8iPeuccSrTP8bl9Cs/dev"


class ComponentManagementSystem:
    def __init__(self):
        self.selected_menu = None
        self.pageIcon ='''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-kanban" viewBox="0 0 16 16"><path d="M13.5 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zm-11-1a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/><path d="M6.5 3a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm-4 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm8 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1z"/></svg>'''
        self.pageTitle = "Component Management System"
        self.hide_decoration_bar_style = '''<style>header {visibility: hidden;}</style>'''
        self.menu_title = "Menu"
        self.admin_menu_options = ["Components List", 'Issue Component', "Return Component", "User Enquiry",'Add Component', 'Add User']
        self.admin_menu_icons = ['list-task', 'pencil-square', 'arrow-clockwise', 'person-lines-fill','plus-circle-fill', 'person-plus-fill']
        self.user_menu_options = ["Components List", 'Issue Component', "User Enquiry"]
        self.user_menu_icons = ['list-task', 'pencil-square', 'person-lines-fill']
        st.set_page_config(page_title=self.pageTitle, page_icon=self.pageIcon)
        st.markdown(self.hide_decoration_bar_style, unsafe_allow_html=True)

    def run(self):
        if 'logged_in' not in st.session_state or 'role' not in st.session_state:
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            
        if not st.session_state['logged_in'] or st.session_state['role'] == None:
            # show_login_form
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
        else:
            #after_login_render
            with st.sidebar:
                st.image("logo.png", width=280)
                if st.session_state['role'] == "Admin":
                    self.selected_menu = option_menu(
                        menu_title=self.menu_title,
                        options=self.admin_menu_options,
                        icons=self.admin_menu_icons
                    )
                if st.session_state['role'] == "User":
                    self.selected_menu = option_menu(
                        menu_title=self.menu_title,
                        options=self.user_menu_options,
                        icons=self.user_menu_icons
                    )

            if self.selected_menu == "Add User":
                self.add_user_page()
            elif self.selected_menu == "Components List":
                self.components_list_page()
            elif self.selected_menu == "Issue Component":
                self.issue_component_page()
            elif self.selected_menu == "Return Component":
                self.return_component_page()
            elif self.selected_menu == "User Enquiry":
                self.user_enquiry_page()
            elif self.selected_menu == "Add Component":
                self.add_component_page()
     
    def issue_component_page(self):
        pass

    def return_component_page(self):
        pass

    def user_enquiry_page(self):
        pass

    def add_component_page(self):
        pass

    def components_list_page(self):
        st.title("Components List")
        self.component_text_search = st.text_input("Search Component", value="").strip().lower()
        data = self.components_list(self.component_text_search)
        print(data)
        st.code(data)
        # m1 = self.df["component"].str.contains(self.component_text_search)
        # m2 = self.df["image_path"].str.contains(self.component_text_search)
        # df_search = self.df[m1 | m2]

        # N_cards_per_row = 3
        # if self.component_text_search:  
        #     for n_row, row in df_search.reset_index().iterrows():
        #         i = n_row%N_cards_per_row
        #         if i==0:
        #             st.write("---")
        #             cols = st.columns(N_cards_per_row, gap="large")
        #         # draw the card
        #         with cols[n_row%N_cards_per_row]:
        #             img = Image.open(row['image_path'])
        #             st.image(img, use_column_width=True, width=100)
        #             st.code(f"{row['component'].strip()}", language='html')
        #             st.markdown(f"Remaining Qty: **{row['remaining_qty']}**")
        #             st.markdown(f"Total: *{row['total_qty']}*")

    def add_user_page(self):
        st.title("Create New User")
        user_id = st.text_input("User ID")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Admin", "User"])

        if st.button("Create User"):
            if user_id and name and password:
                result = self.create_user(user_id, name, password, role)
                if result.get("success"):
                    st.success(result["message"])
                else:
                    st.error("Failed to create user!")
            else:
                st.error("All fields are required!")

    def get_components_list(self, querie):
        data = {
            "action": "getComponentsList",
            "querie": querie
        }
        response = requests.post(WEB_APP_URL, json=data)
        return response.json()

    def validate_credentials(self, username, password):
        data = {
            "action": "validateCredentials",
            "data": {
                "username": username,
                "password": password
            }
        }
        response = requests.post(WEB_APP_URL, json=data)
        # print(response.json())
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
        print(response)
        return response.json()  


if __name__ == '__main__':
    app = ComponentManagementSystem()
    app.run()