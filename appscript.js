let doc = SpreadsheetApp.openById("15weprxj5gq7YgyNYyuwKlZxi22kNJNRfVuSwBtUPDlA");
const components = doc.getSheetByName("components");
const issue_return_logs = doc.getSheetByName("issue_return_logs");
// const student_table = doc.getSheetByName("student_table");
const user_management = doc.getSheetByName("user_management");
const settings = doc.getSheetByName("settings");

function doPost(e) {
  const request = JSON.parse(e.postData.contents);
  
  if (request.action === "createUser") {
    return ContentService.createTextOutput(JSON.stringify(createUser(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "validateCredentials") {
    return ContentService.createTextOutput(JSON.stringify(validateCredentials(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "getComponentsList") {
    return ContentService.createTextOutput(JSON.stringify(getComponentsList(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "addComponent") {
    return ContentService.createTextOutput(JSON.stringify(addComponent(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "issueComponent") {
    return ContentService.createTextOutput(JSON.stringify(issueComponent(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "getIssuedComponents") {
    return ContentService.createTextOutput(JSON.stringify(getIssuedComponents(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "returnComponent") {
    return ContentService.createTextOutput(JSON.stringify(returnComponent(request.data))).setMimeType(ContentService.MimeType.JSON);
  }
  return ContentService.createTextOutput(JSON.stringify({ error: "Invalid action" }))
                       .setMimeType(ContentService.MimeType.JSON);
}

// console.log(getIssuedComponents({
//       user_id: "2022BEC057"
//     }))

function getIssuedComponents(data) {
  const { user_id } = data;

  // Find the user in the user_management sheet
  const userData = user_management.getRange(2, 1, user_management.getLastRow() - 1, 7).getValues();
  const userIndex = userData.findIndex(row => row[0] === user_id);

  if (userIndex === -1) {
    return { success: false, message: "User not found!" };
  }

  // Retrieve the user's issued components
  let issuedComponents = userData[userIndex][6]; // Column G (Currently Issued)
  issuedComponents = issuedComponents ? JSON.parse(issuedComponents) : [];

  if (!Array.isArray(issuedComponents)) {
    issuedComponents = []; // Ensure it's an array
  }

  // Retrieve all components from the components sheet
  const componentData = components.getRange(2, 1, components.getLastRow() - 1, 2).getValues(); // A: Component_ID, B: Component_Name
  const componentMap = Object.fromEntries(componentData.map(row => [row[0], row[1]])); // Map Component_ID -> Component_Name

  // Attach component names to the response
  const detailedIssuedComponents = issuedComponents.map(item => ({
    component_id: item.component_id,
    component_name: componentMap[item.component_id] || "Unknown Component",
    quantity: item.quantity
  }));

  return { success: true, data: detailedIssuedComponents };
}

// 


function returnComponent(data) {
  const { user_id, component_id, return_quantity, damaged_quantity } = data;

  // Find the user in the user_management sheet
  const userData = user_management.getRange(2, 1, user_management.getLastRow() - 1, 7).getValues();
  const userIndex = userData.findIndex(row => row[0] === user_id);

  if (userIndex === -1) {
    return { success: false, message: "User not found!" };
  }

  // Find the component in the components sheet
  const componentData = components.getRange(2, 1, components.getLastRow() - 1, 7).getValues();
  const componentIndex = componentData.findIndex(row => row[0] === component_id);

  if (componentIndex === -1) {
    return { success: false, message: "Component not found!" };
  }

  // Retrieve the issued components list of the user
  let issuedComponents = userData[userIndex][6]; // Column G (Currently Issued)
  issuedComponents = issuedComponents ? JSON.parse(issuedComponents) : [];

  if (!Array.isArray(issuedComponents)) {
    issuedComponents = []; // Ensure it's an array
  }

  // Check if the user has issued the component
  const issuedIndex = issuedComponents.findIndex(item => item.component_id === component_id);

  if (issuedIndex === -1) {
    return { success: false, message: "Component was not issued to this user!" };
  }

  let issuedQuantity = issuedComponents[issuedIndex].quantity;

  if (return_quantity + damaged_quantity > issuedQuantity) {
    return { success: false, message: "Return quantity exceeds issued quantity!" };
  }

  // Update the issued component quantity
  if (return_quantity + damaged_quantity === issuedQuantity) {
    issuedComponents.splice(issuedIndex, 1); // Remove component from issued list if fully returned
  } else {
    issuedComponents[issuedIndex].quantity -= (return_quantity + damaged_quantity);
  }

  // Update Available and Damaged Quantities in the components sheet
  let availableQuantity = componentData[componentIndex][5]; // Column F (Available_Quantity)
  let damagedQuantityOld = componentData[componentIndex][6]; // Column G (Damaged_Quantity)

  components.getRange(componentIndex + 2, 6).setValue(availableQuantity + return_quantity); // Update Available Quantity
  components.getRange(componentIndex + 2, 7).setValue(damagedQuantityOld + damaged_quantity); // Update Damaged Quantity

  // Store updated issued list in the sheet
  user_management.getRange(userIndex + 2, 7).setValue(JSON.stringify(issuedComponents)); // Column G (Currently Issued)

  // Log the return transaction in issue_return_logs
  issue_return_logs.appendRow([user_id, component_id, return_quantity, damaged_quantity, new Date(), "Returned"]);

  return { success: true, message: `Returned ${return_quantity} of ${component_id} (Damaged: ${damaged_quantity}) from ${user_id}` };
}



// function returnComponent(data) {
//   const { user_id, component_id, quantity } = data;

//   // Find the user in the user_management sheet
//   const userData = user_management.getRange(2, 1, user_management.getLastRow() - 1, 7).getValues();
//   const userIndex = userData.findIndex(row => row[0] === user_id);

//   if (userIndex === -1) {
//     return { success: false, message: "User not found!" };
//   }

//   // Find the component in the components sheet
//   const componentData = components.getRange(2, 1, components.getLastRow() - 1, 7).getValues();
//   const componentIndex = componentData.findIndex(row => row[0] === component_id);

//   if (componentIndex === -1) {
//     return { success: false, message: "Component not found!" };
//   }

//   // Get the user's currently issued components
//   let issuedComponents = userData[userIndex][6]; // Column G (Currently Issued)
//   issuedComponents = issuedComponents ? JSON.parse(issuedComponents) : [];

//   if (!Array.isArray(issuedComponents)) {
//     issuedComponents = []; // Ensure it's an array
//   }

//   // Find the issued record for this component
//   const issuedIndex = issuedComponents.findIndex(item => item.component_id === component_id);

//   if (issuedIndex === -1) {
//     return { success: false, message: "Component was not issued to this user!" };
//   }

//   if (issuedComponents[issuedIndex].quantity < quantity) {
//     return { success: false, message: "User is trying to return more than issued!" };
//   }

//   // Update available quantity in components sheet
//   const availableQuantity = componentData[componentIndex][5]; // Column F (Available Quantity)
//   components.getRange(componentIndex + 2, 6).setValue(availableQuantity + quantity); // Update Available_Quantity

//   // Update user's issued list
//   if (issuedComponents[issuedIndex].quantity === quantity) {
//     issuedComponents.splice(issuedIndex, 1); // Remove if all returned
//   } else {
//     issuedComponents[issuedIndex].quantity -= quantity; // Reduce quantity
//   }

//   // Store updated issued list back in the sheet
//   user_management.getRange(userIndex + 2, 7).setValue(issuedComponents.length ? JSON.stringify(issuedComponents) : ""); // Column G (Currently Issued)

//   // Log the return transaction in issue_return_logs
//   issue_return_logs.appendRow([user_id, component_id, quantity, new Date(), "Returned"]);

//   return { success: true, message: `Returned ${quantity} of ${component_id} from ${user_id}` };
// }


function issueComponent(data) {
  const { user_id, component_id, quantity } = data;

  // Find the user in the user_management sheet
  const userData = user_management.getRange(2, 1, user_management.getLastRow() - 1, 7).getValues();
  const userIndex = userData.findIndex(row => row[0] === user_id);

  if (userIndex === -1) {
    return { success: false, message: "User not found!" };
  }

  // Find the component in the components sheet
  const componentData = components.getRange(2, 1, components.getLastRow() - 1, 7).getValues();
  const componentIndex = componentData.findIndex(row => row[0] === component_id);

  if (componentIndex === -1) {
    return { success: false, message: "Component not found!" };
  }

  // Get available quantity from the components sheet
  const availableQuantity = componentData[componentIndex][5]; // Column F (Available_Quantity)

  if (availableQuantity < quantity) {
    return { success: false, message: "Not enough components available!" };
  }

  // Retrieve user's issued components
  let issuedComponents = userData[userIndex][6]; // Column G (Currently Issued)
  issuedComponents = issuedComponents ? JSON.parse(issuedComponents) : [];

  if (!Array.isArray(issuedComponents)) {
    issuedComponents = []; // Ensure it's an array
  }

  // Check if the component is already issued to the user
  const existingIndex = issuedComponents.findIndex(item => item.component_id === component_id);

  if (existingIndex !== -1) {
    // Update quantity if component already issued
    issuedComponents[existingIndex].quantity += quantity;
  } else {
    // Add new issued record
    issuedComponents.push({ component_id, quantity });
  }

  // Update available quantity in components sheet
  components.getRange(componentIndex + 2, 6).setValue(availableQuantity - quantity); // Column F (Available Quantity)

  // Store updated issued list in the sheet
  user_management.getRange(userIndex + 2, 7).setValue(JSON.stringify(issuedComponents)); // Column G (Currently Issued)

  // Log the issue transaction in issue_return_logs
  issue_return_logs.appendRow([user_id, component_id, quantity, new Date(), "Issued"]);

  return { success: true, message: `Issued ${quantity} of ${component_id} to ${user_id}` };
}



function addComponent(data) {
  const lastRow = components.getLastRow();
  const newComponentID = "C" + (lastRow).toString().padStart(4, '0'); // Generates a unique Component_ID like C0001, C0002, etc.

  components.appendRow([
    newComponentID,
    data.component_name,
    data.component_image_link,
    data.component_description,
    data.quantity,  // Total Quantity
    data.quantity,  // Initially, Available Quantity = Total Quantity
    0              // Initially, Damaged Quantity = 0
  ]);

  return { success: true, message: `Component ${newComponentID} added successfully!` };
}


function getComponentsList(data){
  const q = data.querie
  const a = components.getRange(2, 1, components.getLastRow() - 1, 4).getValues().filter(row => row.some(cell => cell.toString().toLocaleLowerCase().includes(q.toString().toLowerCase())));
  const b = JSON.stringify(a);
  return { success: true, data: b};
}

function createUser(data) {
  const hashedPassword = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, data.password));
  user_management.appendRow([data.userId, data.name, hashedPassword, data.role, data.email, data.contact, data.currently_issued]);
  return { success: true, message: `User ${data.userId} created successfully!` };
}

function validateCredentials(data) {
  const hashedPassword = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, data.password));
  const user = user_management.getRange(2, 1, user_management.getLastRow() - 1, 4).getValues().find(row => row[0] === data.username);
  const role = user[3];

  if (!user) {
    return { success: false, message: "User not found"};
  }
  if (user[2] !== hashedPassword) {
    return { success: false, message: "Invalid password"};
  }
  return { success: true, role: role, message: "Login successful"};
}