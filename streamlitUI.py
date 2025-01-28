import streamlit as st
from streamlit_option_menu import option_menu
from utils import Operator


class UserInterface:
    def __init__(self):
        self.op = Operator()
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
        st.success(self.op.add_component(component.strip().lower(), qty, image_path))
        

    def issue_component_record(self, component, user_name, qty):
        st.success(self.op.issue_component(user_name, component.strip().lower(), qty))

    def return_component_record(self, component, user_name, qty):
        st.success(self.op.return_component(user_name, component.strip().lower(), qty))


    def render_user_enquiry(self):
        '''Render the user enquiry form operator'''
        st.title("User Enquiry")
        user_name = st.text_input("Registration No", value="")
        btn_presses = st.button("Submit")
        if btn_presses:
            st.write("Registration No: ", user_name)
            st.write(self.op.list_issued_component(user_name))


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
            # self.issue_component_record(component_name, user_name, qty)
            st.write(self.op.issue_component(user_name, component_name.strip().lower(), qty))
        

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

