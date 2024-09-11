import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
from hashlib import sha256



# show data from csv file
class ComponentManagementSystem:
    def __init__(self):
        self.auth_hashes = ["9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                            "7fbe048ce792eb308f911551731d9df9da5f65a27a3eca5d51103150210ef26c",
                            "be18b85f77fc024db379acf19e8a1ce62307ab7bb1bca395389ecfc2dafaf741"]
        self.df = pd.read_csv('data.csv')
        self.selected_menu = None
        st.set_page_config(page_title="Component Management System", page_icon='''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-kanban" viewBox="0 0 16 16">
  <path d="M13.5 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zm-11-1a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
  <path d="M6.5 3a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm-4 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm8 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1z"/>
</svg>''')
        hide_decoration_bar_style = '''
            <style>
                header {visibility: hidden;}
            </style>
        '''
        st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


    def add_component_record(self, component, qty, image_path):
        if component.strip().lower() in self.df["component"].values:
            self.df["total_qty"].iloc[self.df[self.df["component"] == component.strip().lower()].index[0]] += int(qty)
            self.df["remaining_qty"].iloc[self.df[self.df["component"] == component.strip().lower()].index[0]] += int(qty)
            self.df.to_csv('data.csv', index=False)
            st.success("Component already exists, Adding quantity to existing component.")
            return

        new_id = self.df["id"].iloc[-1] + 1
        new_record = pd.DataFrame({
            "component": [component.strip().lower()],
            "total_qty": [qty],
            "remaining_qty": [qty],
            "image_path": [image_path],
            "defective": 0,
            "issued_users": [""],
            "id": [new_id]
        })
        self.df = pd.concat([self.df, new_record], ignore_index=True)
        self.df.to_csv('data.csv', index=False)
        st.success("Component added successfully")

    def issue_component_record(self, component, user_name, qty):
        # Check if the component exists
        component = component.strip().lower()
        if component not in self.df["component"].values:
            st.error("Component not found")
            st.write(self.df["component"].values)
            st.write(component)
            return
        # Check if the quantity is available
        idx = self.df[self.df["component"] == component].index[0]
        if self.df["remaining_qty"].iloc[idx] < int(qty):
            st.error("Not enough quantity")
            return
        # Update the record
        self.df["remaining_qty"].iloc[idx] -= int(qty)
        if str(self.df["issued_users"].iloc[idx]) == "nan":
            self.df["issued_users"].iloc[idx] = f"{user_name}({qty}),"
        else:
            self.df["issued_users"].iloc[idx] = str(self.df["issued_users"].iloc[idx]) + f"{user_name}({qty}),"
        self.df.to_csv('data.csv', index=False)

        st.success("Component issued successfully")

    def return_component_record(self, component, user_name, qty):
        # Check if the component exists
        component = component.strip().lower()
        if component not in self.df["component"].values:
            st.error("Component not found")
            return
        # Check if the user has issued the component
        idx = self.df[self.df["component"] == component].index[0]
        if user_name not in self.df["issued_users"].iloc[idx]:
            st.error("Component not issued to this user")
            return
        # Update the record
        self.df["remaining_qty"].iloc[idx] += int(qty)
        self.df["issued_users"].iloc[idx] = str(self.df["issued_users"].iloc[idx]).replace(f"{user_name}({qty}),", "")
        self.df.to_csv('data.csv', index=False)
        st.success("Component returned successfully")


    def render_user_enquiry(self):
        st.title("User Enquiry")
        user_name = st.text_input("Registration No", value="").strip().lower()
        btn_presses = st.button("Submit")
        if btn_presses:
            st.write("Registration no: ", user_name)
            st.write("Components Issued: ")
            for idx, row in self.df.iterrows():
                if str(row["issued_users"]) != "nan" and user_name in row["issued_users"]:
                    # st.write(f"{row['component']}({row['issued_users'].count(user_name)})")
                    st.write(f"{row['component']} ==>  {', '.join([item.split('(')[-1][:-1] for item in row['issued_users'].split(',') if user_name in item])}")
            # st.write("Total Components Issued: ")
            # total = 0
            # for idx, row in self.df.iterrows():
            #     if str(row["issued_users"]) != "nan" and user_name in row["issued_users"]:
            #         total += row['issued_users'].count(user_name)
            # st.write(total)

    def render_issue_component(self):
        st.title("Issue Component")
        component_name = st.text_input("Component Name (copy from component list)", value="")
        user_name = st.text_input("Registration No", value="")
        qty = st.text_input("Quantity", value="")
        btn_presses = st.button("Submit")


        if btn_presses:
            st.write("Component Name: ", component_name)
            st.write("Registration No: ", user_name)
            st.write("Quantity: ", qty)
            self.issue_component_record(component_name, user_name, qty)
        

    def render_add_component(self):
        st.title("Add Component")
        comp_name = st.text_input("Component Name (copy from component list)", value="")
        qty = st.text_input("Quantity", value="")
        image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg'], accept_multiple_files=False)
        if image_file is not None:
            img = Image.open(image_file)
        btn_presses = st.button("Submit")

        if btn_presses:
            # st.write("Button Pressed")
            st.write("Component Name: ", comp_name)
            st.write("Quantity: ", qty)
            with open(f"images/{image_file.name}", "wb") as f:
                f.write(image_file.getbuffer())
            st.write("Image: ", "images/"+image_file.name)
            st.image(img,width=250)
            self.add_component_record(comp_name, qty, "images/"+image_file.name)

        
    def render_return_component(self):
        st.title("Return Component")
        component_name = st.text_input("Component Name (copy from component list)", value="")
        user_name = st.text_input("Registration No", value="")
        qty = st.text_input("Quantity", value="")
        btn_presses = st.button("Submit")

        if btn_presses:
            st.write("Component Name: ", component_name)
            st.write("Registration No: ", user_name)
            st.write("Quantity: ", qty)
            self.return_component_record(component_name, user_name, qty)


    def render_show_data(self):
        st.title("Components List")
        # st.subheader("Component list")

        self.component_text_search = st.text_input("Search Component", value="").strip().lower()
        m1 = self.df["component"].str.contains(self.component_text_search)
        m2 = self.df["image_path"].str.contains(self.component_text_search)
        df_search = self.df[m1 | m2]

        # Show the cards
        N_cards_per_row = 3
        if self.component_text_search:
            for n_row, row in df_search.reset_index().iterrows():
                i = n_row%N_cards_per_row
                if i==0:
                    st.write("---")
                    cols = st.columns(N_cards_per_row, gap="large")
                # draw the card
                with cols[n_row%N_cards_per_row]:
                    img = Image.open(row['image_path'])
                    st.image(img, use_column_width=True, width=100)
                    st.code(f"{row['component'].strip()}", language='html')
                    st.markdown(f"Remaining Qty: **{row['remaining_qty']}**")
                    st.markdown(f"Total: *{row['total_qty']}*")

    def verify_auth_code(self):
        auth_code = st.text_input("Enter Auth Code", value="", type="password")
        if sha256(auth_code.encode()).hexdigest() in self.auth_hashes:
            return True
        return False


    def render(self):
        with st.sidebar:
            st.image("logo.png", width=270)

            self.selected_menu = option_menu(
                menu_title='Menu',
                options=["Components List", 'Issue Component', "Return Component", "User Enqury",'Add Component'],
                icons=['list-task', 'pencil-square', 'arrow-clockwise', 'person-lines-fill','plus-circle-fill']
            )
        
        if self.selected_menu == 'Issue Component' and self.verify_auth_code():
            self.render_issue_component()
        if self.selected_menu == 'Add Component'  and self.verify_auth_code():
            self.render_add_component()
        if self.selected_menu == 'Return Component' and self.verify_auth_code():
            self.render_return_component()
        if self.selected_menu == 'Components List':
            self.render_show_data()
        if self.selected_menu == 'User Enqury':
            self.render_user_enquiry()


if __name__ == '__main__':
    app = ComponentManagementSystem()
    app.render()