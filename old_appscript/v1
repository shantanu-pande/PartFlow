let doc = SpreadsheetApp.openById("15weprxj5gq7YgyNYyuwKlZxi22kNJNRfVuSwBtUPDlA");
const components = doc.getSheetByName("components");
const issue_return_logs = doc.getSheetByName("issue_return_logs");
const student_table = doc.getSheetByName("student_table");
const user_management = doc.getSheetByName("user_management");
const settings = doc.getSheetByName("settings");

function doPost(e) {
  const request = JSON.parse(e.postData.contents);
  
  if (request.action === "createUser") {
    return ContentService.createTextOutput(JSON.stringify(createUser(request.data)))
                         .setMimeType(ContentService.MimeType.JSON);
  }
  else if (request.action === "validateCredentials") {
    return ContentService.createTextOutput(JSON.stringify(validateCredentials(request.data)))
  }
  return ContentService.createTextOutput(JSON.stringify({ error: "Invalid action" }))
                       .setMimeType(ContentService.MimeType.JSON);
}

function createUser(data) {
  const hashedPassword = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, data.password));
  
  sheet.appendRow([data.userId, data.name, hashedPassword, data.role]);
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