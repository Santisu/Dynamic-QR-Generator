# DYNAMIC QR CODE GENERATOR
#### Video Demo: [https://youtu.be/_28d_gK2h8Q](URL)
#### Description:

This Flask application generates QR codes that store a unique address to the application's host, redirecting to the active URL for that QR code. It keeps track of how many times the QR code has been scanned for a particular URL and allows you to change the URL to which the same code redirects.

#### Problem Statement:
Depending on the amount of data/characters a QR code stores, the complexity of the image and the matrix of its squares will increase exponentially. In other words, when storing text or a URL with many characters, the image will contain a pattern of squares that becomes more complex. This complexity can make it difficult, for example, to print the image in small sizes, such as business cards, keychains, or badges.

By keeping the number of characters in the QR code to a minimum, you can maintain a simple pattern that is easy to print and read.

So, if you can create a QR code whose simple pattern connects to a database where more complex data is stored, it is possible to store large amounts of data in a QR code image without increasing its complexity.

## Main Dependencies:
*All the detailed dependencies are stored in the requirements.txt file.*

- Flask
- Qrcode
- SQLAlchemy
- BCrypt
- ShortUUID

### Flask

Contains the main application and allows running the application in a production web environment.

### QRCode

A QR code generator that stores QR codes in .png format.

### SQLAlchemy
A link to the database used, in this case, an sqlite3 .db file.

### BCrypt
An encryptor for the passwords created for each QR code.

### ShortUUID
Generates the unique path for each QR code based on a UUID.

## Database Structure

### QR Table

| Field         | Type   | Primary Key | Unique | Nullable | Description               |
|---------------|--------|-------------|--------|----------|---------------------------|
| qr_id         | Integer| Yes         | No     | No       | Unique ID of the QR code  |
| short_url     | String | No          | Yes    | Yes      | Short URL of the QR code  |
| path          | String | No          | Yes    | Yes      | Path of the QR code       |
| qr_image      | String | No          | No     | Yes      | Path to the QR image      |
| password      | String | No          | No     | Yes      | QR code password          |
| info          | Relationship| No          | No     | No       | Relationship with the Info table |

### Info Table

| Field         | Type   | Primary Key | Unique | Nullable | Description                          |
|---------------|--------|-------------|--------|----------|--------------------------------------|
| info_id       | Integer| Yes         | No     | No       | Unique information ID                 |
| qr_id         | Integer| No          | No     | No       | ID of the related QR code             |
| original_url  | String | No          | No     | No       | Original URL to which it redirects   |
| number_opened | Integer| No          | No     | No       | Number of times it has been opened    |
| current_link  | Integer| No          | No     | No       | Current active link (0 or 1)          |
| qr            | Relationship| No          | No     | No       | Relationship with the QR table       

## Views
### index:
#### Template: index.html
A simple view that redirects to the application's main page.
### generate:
#### Template: generate.html
Redirects to the page for generating a QR code.

A form is used to enter the link to which you want the QR code to redirect, and a password is added to access the data of that QR code.

The internal logic of this view stores the unique path to which the QR code will redirect, the name of the QR code image, and the password to access the QR code information in the database. It also stores the record of the actual URL to which the QR code redirects in the table, the number of times the QR code has redirected to that URL, and, using a Boolean value, whether that is the current active link for the QR code.

### get_info:
#### Template: get_info.html
A form is used to enter the short path and the QR code password. If correct, this view redirects to the QR code information page, which is stored in the browser's session.

### info:
#### Template: info.html
This view displays information related to the QR code stored in the browser's session.

The page displays the QR code image, the short path, and a table with the history of URLs to which the QR code has been linked. This history shows each real link to which the QR code redirects, the number of times it has been opened, and whether it is the active link to which the QR code currently redirects. Of all the links in the history, only one is active, and the rest are displayed as inactive.

Additionally, there is a form for changing the active URL to which the QR code redirects. If the URL already exists in the records of the same QR code, it becomes active again. If it is a new record, it is added and marked as active, deactivating the previous active record.

### dynamic_redirect:
This view takes a 6-character path generated for each code as an argument. It searches the records in the "qr" table of the database. If it finds the record, it redirects to the URL marked as active for that QR code. If the 6-character path does not exist, it returns a 404 error.

### clear_session:
If the user has an active editable QR code in their browser session, they can click the "Clear Session" button in the navigation bar to clear the session, preventing others from accessing the information of the last QR code consulted.
