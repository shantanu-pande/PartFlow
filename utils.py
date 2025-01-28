import pandas as pd
from hashlib import sha256
import socket
import json
import os

class Operator():
    def __init__(self):
        # self.online = False
        self.issuer_login = False
        self.config_path = 'config.json'
        self.config = self.load_config()
        
    # def is_online(self):
    #     try:
    #         socket.create_connection(("1.1.1.1", 53))
    #         return True
    #     except OSError:
    #         pass
    #     return False

    def load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def add_component(self, component, qty, image):
        try:
            image_path = os.path.join(self.config["images_path"], image)
            # load the csv file using pandas
            components_df = pd.read_csv(self.config["components_file"])
            
            # check if the component already exists
            if component in components_df["component"].values:
                # if yes, add the quantity to the existing component
                idx = components_df[components_df["component"] == component].index[0]
                components_df.loc[idx, "total_qty"] += qty
                components_df.loc[idx, "remaining_qty"] += qty
                if image is not None:
                    components_df.loc[idx, "image_path"] = image_path
            else:
                # if no, add a new component
                new_id = components_df["id"].iloc[-1] + 1
                new_record = pd.DataFrame({
                    "component": [component],
                    "total_qty": [qty],
                    "remaining_qty": [qty],
                    "image_path": [image_path],
                    "defective": 0,
                    "id": [new_id]
                })
                components_df = pd.concat([components_df, new_record], ignore_index=True)
            components_df.to_csv(self.config["components_file"], index=False)
            return "Component added successfully"
        except Exception as e:
            return str(e)

    def issue_component(self, user, component, qty):
        try:
            components_df = pd.read_csv(self.config["components_file"])
            user_df = pd.read_csv(self.config["users_file"])
            # check if the component and users exists
            if component not in components_df["component"].values:
                return "Component not found"
            if user not in user_df["users"].values:
                return "User not found"
            # check if the quantity is available
            idx = components_df[components_df["component"] == component].index[0]
            if components_df["remaining_qty"].iloc[idx] < qty:
                return "Not enough quantity"
            # update the record
            components_df.loc[idx, "remaining_qty"]-= qty
            issued_components = user_df.loc[user_df["users"] == user, "issued_components"].values[0].split(",")
            # filter for empty strings
            issued_components = [x for x in issued_components if x]

            # if component in issued_components:
            item_found_flag = 0
            for i, item in enumerate(issued_components):
                if item.startswith(f"{component}("):
                    current_qty = int(item.split('(')[1].split(')')[0])
                    issued_components[i] = f"{component}({current_qty + qty})"
                    item_found_flag = 1
                    break
            user_df.loc[user_df["users"] == user, "issued_components"] = ','.join(issued_components)

            if not item_found_flag:
                user_df.loc[user_df["users"] == user, "issued_components"] += f"{component}({qty}),"

            components_df.to_csv(self.config["components_file"], index=False)
            user_df.to_csv(self.config["users_file"], index=False)
            return "Issued successfully"
        except Exception as e:
            return str(e)
 
    def return_component(self, user, component, qty, defective):
        try:
            components_df = pd.read_csv(self.config["components_file"])
            user_df = pd.read_csv(self.config["users_file"])
            # check if the component and users exists
            if component not in components_df["component"].values:
                return "Component not found"
            if user not in user_df["users"].values:
                return "User not found"

            idx = components_df[components_df["component"] == component].index[0]
            components_df.loc[idx, "defective"] += defective
            components_df.loc[idx, "remaining_qty"] += (qty-defective)

            issued_components = user_df.loc[user_df["users"] == user, "issued_components"].values[0].split(",")
            issued_components = [x for x in issued_components if x]

            for i, item in enumerate(issued_components):
                if item.startswith(f"{component}("):
                    current_qty = int(item.split('(')[1].split(')')[0])
                    if current_qty < qty:
                        return "Not enough quantity"
                    elif current_qty == qty:
                        issued_components.pop(i)
                    else:
                        issued_components[i] = f"{component}({current_qty - qty})"
                    break

            user_df.loc[user_df["users"] == user, "issued_components"] = ','.join(issued_components)
            components_df.to_csv(self.config["components_file"], index=False)
            user_df.to_csv(self.config["users_file"], index=False)
            return "Component returned successfully"
        except Exception as e:
            return str(e)

    def verify_issuer(self, uname, passwd):
        try:
            issuer_df = pd.read_csv(self.config["issuers_file"])
            if not (uname in issuer_df["username"].values):
                self.issuer_login = False
                return False
            else:
                idx = issuer_df[issuer_df["username"] == uname].index[0]
                if sha256(passwd.encode()).hexdigest() in issuer_df.loc[idx, "password"]:
                    self.issuer_login = True
                    return True
                else:
                    self.issuer_login = False
                    return False
        except Exception as e:
            return False
        
    def list_components(self):
        components_df = pd.read_csv(self.config["components_file"])
        return components_df.to_dict(orient='records')
    
    def list_issued_component(self, user):
        # Write your own code if need modification 🤷‍♂️
        user_df = pd.read_csv(self.config["users_file"])
        return [{"index": index, "component": issue.split('(')[0], "qty": issue.split('(')[1].split(')')[0]} for index, issue in enumerate([x for x in user_df.loc[user_df["users"] == user, "issued_components"].values[0].split(",") if x])]

