const CLOUD_FUNCTION_URL = "https://us-central1-shared-vikas.cloudfunctions.net/function-1";

function checkForNewFiles() {
  const folderId = '172V4xhL4n2cfJ1qZ6TKTc6sTjQAHOzyd'; 

  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();

  while (files.hasNext()) {
    const file = files.next();
    const fileId = file.getId();

    // Check if this file ID has been processed before
    if (!hasFileBeenProcessed(fileId)) {
      // File details
      const fileName = file.getName();
      const fileSize = file.getSize();
      const fileMimeType = file.getMimeType();

      const fileDetails = {
        id: fileId,
        name: fileName,
        size: fileSize,
        mimeType: fileMimeType
      };

      console.log(fileDetails); // Print the fileDetails object content

      // Send file details to Cloud Function
      sendToCloudFunction(fileDetails);

      // Store the file ID to mark it as processed
      markFileAsProcessed(fileId);
    }
  }
}

function sendToCloudFunction(fileDetails) {
  const options = {
    method: 'post',
    contentType: 'application/json', // Set the content type to JSON
    payload: JSON.stringify(fileDetails)
  };

  try {
    const response = UrlFetchApp.fetch(CLOUD_FUNCTION_URL, options);
    console.log(response.getContentText()); // Log the response content
  } catch (error) {
    console.error(error); // Log any errors
  }
}

function hasFileBeenProcessed(fileId) {
  // Replace "spreadsheetId" with your actual spreadsheet ID
  const sheet = SpreadsheetApp.openById("1TRuhqWHKjyZOZYlXyrimSzN2C3Y7eNUkeEoMxmUR17w").getSheetByName("Sheet1");
  const fileIds = sheet.getRange("A:A").getValues().map(row => row[0]); // Get all file IDs in column A
  return fileIds.includes(fileId);
}

function markFileAsProcessed(fileId) {
  // Replace "spreadsheetId" with your actual spreadsheet ID
  const sheet = SpreadsheetApp.openById("1TRuhqWHKjyZOZYlXyrimSzN2C3Y7eNUkeEoMxmUR17w").getSheetByName("Sheet1");
  sheet.appendRow([fileId, true]); // Append a new row with fileId and processed=true
}

