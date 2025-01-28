from streamlitUI import UserInterface as ui 

if __name__ == '__main__':
    app = ui()
    app.render()
    
    # operator = Operator()
    # operator.add_component("resistor", 10, "resistor.png")
    # print(operator.issue_component("user1", "arduino uno", 5))
    # print(operator.return_component("user1", "arduino uno", 2, 1))
    # print(operator.list_components())
    # print(operator.list_issued_component("user1"))
    # print(operator.verify_issuer("shantanu", "sp"))