import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import requests
from io import BytesIO
import json

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxnFXCqYbbSfFZjT2wOUe2v9innSydVQC5Ekv7OP2nADWvvgcuyMpSr--luVUNeQGMU3g/exec"


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
                st.image("logo.png", width=260)
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
        st.title("Issue Component")
        userId = st.text_input("User ID")
        componentId = st.text_input("Component ID")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        if st.button("Issue"):
            data = {
                "action": "issueComponent",
                "data": {
                    "user_id": userId,
                    "component_id": componentId,
                    "quantity": quantity
                }
            }
            response = requests.post(WEB_APP_URL, json=data)
            if response.json().get("success"):
                st.success("Component issued successfully!")
            else:
                st.error("Failed to issue component!")


    def return_component_page(self):
        st.title("Return Component")
        userId = st.text_input("User ID")

        if 'components' not in st.session_state:
            st.session_state['components'] = []

        if st.button("Fetch Components"):
            data = {
                "action": "getIssuedComponents",
                "data": {
                    "user_id": userId
                }
            }
            response = requests.post(WEB_APP_URL, json=data)
            if response.json().get("success"):
                st.session_state['components'] = response.json().get("data")
            else:
                st.error("Failed to fetch components!")
                return

        components = st.session_state['components']
        for i in range(0, len(components), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j >= len(components):
                    break
                row = components[i + j]
                with col:
                    with st.expander(f"Component: {row['component_name'].strip()}"):
                        # img = Image.open(BytesIO(requests.get(row['image_path']).content))
                        # st.image(img, use_column_width=True, width=100)
                        st.markdown(f"**ID:** {row['component_id']}")
                        st.markdown(f"**Quantity Issued:** {row['quantity']}")
                        quantity_r = st.number_input(f"Return Quantity ({row['component_name']})", min_value=0, max_value=row['quantity'], value=0, key=f"r_quantity_{row['component_id']}")
                        quantity_d = st.number_input(f"Return Quantity ({row['component_name']})", min_value=0, max_value=row['quantity'], value=0, key=f"d_quantity_{row['component_id']}")
                        if st.button(f"Return {row['component_name']}", key=f"return_{row['component_id']}"):
                            return_data = {
                                "action": "returnComponent",
                                "data": {
                                    "user_id": userId,
                                    "component_id": row['component_id'],
                                    "return_quantity": quantity_r,
                                    "damaged_quantity": quantity_d
                                }
                            }
                            return_response = requests.post(WEB_APP_URL, json=return_data)
                            if return_response.json().get("success"):
                                st.success(f"Component {row['component_name']} returned successfully!")
                            else:
                                st.error(f"Failed to return component {row['component_name']}!")


    def user_enquiry_page(self):
        st.title("User Enquiry")
        userId = st.text_input("User ID")

        if 'components' not in st.session_state:
            st.session_state['components'] = []

        if st.button("Fetch Components"):
            data = {
                "action": "getIssuedComponents",
                "data": {
                    "user_id": userId
                }
            }
            response = requests.post(WEB_APP_URL, json=data)
            if response.json().get("success"):
                st.session_state['components'] = response.json().get("data")
            else:
                st.error("Failed to fetch components!")
                return

        components = st.session_state['components']
        for i in range(0, len(components), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j >= len(components):
                    break
                row = components[i + j]
                with col:
                    with st.expander(f"Component: {row['component_name'].strip()}"):
                        st.markdown(f"**ID:** {row['component_id']}")
                        st.markdown(f"**Quantity Issued:** {row['quantity']}")
                        

    def add_component_page(self):
        st.title("Add Component")
        component_name = st.text_input("Component Name")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        component_image_link = st.text_input("Component Image Link")
        component_description = st.text_area("Component Description")
        if st.button("Add Component"):
            data = {
                "action": "addComponent",
                "data": {
                    "component_name": component_name,
                    "quantity": quantity,
                    "component_image_link": component_image_link,
                    "component_description": component_description
                }
            }
            response = requests.post(WEB_APP_URL, json=data)
            if response.json().get("success"):
                st.success("Component added successfully!")
            else:
                st.error("Failed to add component!")

    def components_list_page(self):
        st.title("Search Components")
        component_name = st.text_input("Component Name")
        if st.button("Search"):
            data = {
                "action": "getComponentsList",
                "data": {
                    "querie": component_name
                }
            }
            response = requests.post(WEB_APP_URL, json=data)
            if response.json().get("success"):
                components = json.loads(response.json().get("data"))
                for i in range(0, len(components), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(components):
                            row = components[i + j]
                            with col:
                                with st.expander(f"**Component: {row[1].strip()}**"):
                                    img = Image.open(BytesIO(requests.get(row[2]).content))
                                    st.image(img, use_column_width=True, width=100)
                                    st.markdown(f"**ID:** {row[0]}")
                                    st.markdown(f"**Description:** {row[3]}")
            else:
                st.error("Component not found!")
        pass

    def add_user_page(self):
        st.title("Create New User")
        user_id = st.text_input("User ID")
        name = st.text_input("Name")
        email = st.text_input("Email")
        contact = st.number_input("Contact Number", min_value=0, step=1, format="%d")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Admin", "User"])

        if st.button("Create User"):
            if user_id and name and password:
                result = self.create_user(user_id, name, password, role, email, contact)
                if result.get("success"):
                    st.success(result["message"])
                else:
                    st.error("Failed to create user!")
            else:
                st.error("All fields are required!")


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
    
    def create_user(self, user_id, name, password, role, email, contact):
        data = {
            "action": "createUser",
            "data": {
                "userId": user_id,
                "name": name,
                "password": password,
                "role": role,
                "email": email,
                "contact": contact,
                "currently_issued": []
            }
        }
        response = requests.post(WEB_APP_URL, json=data)
        print(response)
        return response.json()  


if __name__ == '__main__':
    app = ComponentManagementSystem()
    app.run()