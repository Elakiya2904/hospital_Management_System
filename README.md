# MySQL ODBC (Connector/ODBC) Installation Guide

This README provides step-by-step instructions to install and configure MySQL ODBC (Connector/ODBC) on Windows, including setting up a System DSN for a database named `ECommerceDB`.

## 1. Download and Install MySQL Connector/ODBC
1. Go to the [MySQL Connector/ODBC download page](https://dev.mysql.com/downloads/connector/odbc/).
2. Download the appropriate version for your Windows (32-bit or 64-bit).
3. Run the installer and follow the on-screen instructions to complete the installation.

## 2. Configure ODBC Data Source for MySQL
1. Open **Control Panel** → **Administrative Tools** → **ODBC Data Sources** (choose 32-bit or 64-bit as per your driver).
2. Go to the **System DSN** tab and click **Add**.
3. Select **MySQL ODBC 8.0 Unicode Driver** (or the version you installed) and click **Finish**.
4. In the setup window, enter the following details:
   - **Data Source Name**: `ECommerceDSN`
   - **TCP/IP Server**: `localhost` (or your MySQL server address)
   - **Port**: `3306` (default MySQL port)
   - **User**: `root` (or your MySQL username)
   - **Password**: (your MySQL password)
   - **Database**: `ECommerceDB`
5. Click **Test** to verify the connection. You should see a "Connection successful" message.
6. Click **OK** to save the data source.

## 3. Example Output

When you test the connection, you should see a dialog like this:

```
Test Result
Connection successful
```

![MySQL ODBC Connection Successful](mysql_odbc_connection_successful.png)

## 4. Verify Installation
- Use your application or a command-line tool to connect using the `ECommerceDSN` data source.
- Ensure the connection is successful.

