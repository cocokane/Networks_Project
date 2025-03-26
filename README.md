# Database Project

# Dispensary Management System

The given problem statement required team to develop a web application using Flask and MySQL to manage a dispensary. The team is divided into two groups, G1 and G2, with G1 responsible for the front-end and G2 for the back-end. The application should support the dynamic execution of database functions, such as insert, rename, update, delete, (CRUD) and where clause. Additionally, the application should have a login page with user and stakeholder authentication.

To develop this application, the team was first needed to design and implement the database schema. We identified the tables and fields required to store information related to the dispensary, such as products, suppliers, employees, customers, and transactions.
Once the database schema is in place, G2 began working on the back-end development. We have used Flask to create the API endpoints that interact with the database. These endpoints should implement the required functions, such as inserting new records, updating existing records, deleting records, and executing where clause queries.

Meanwhile, G1 worked on the front-end development. They used Bootstrap, HTML, and CSS to create a user-friendly interface for the web application. The interface allows users to interact with the database by providing forms and buttons to add, update, and delete records. The interface displays the data stored in the database in a clear and organized manner.

As a part of the project, the team implemented user authentication to ensure that only authorized users can access the application. The login page should prompt users to enter their credentials, and upon successful authentication, the user should be redirected to the main page of the application.
Finally, the team tested the application to ensure that all functions are working correctly, and the changes made through the application are correctly reflected in the main database and web page. Once the application is ready, it was pushed to GitHub.
In summary, this project required the team to develop a web application using Flask and MySQL to manage a dispensary. The application supports the database functions such as insert, update, delete, rename, and where clause, and should have a login page with user authentication. The team also designed the database schema, develop the back-end using Flask, and created a user-friendly front-end using Bootstrap, HTML, and CSS. Finally, the application was be tested and pushed to GitHub for submission.




## Installation

Installation requirements to run this project:

```bash
  python3 -m venv env_flask
```
```bash
  pip3 install flask
```
```bash
  pip3 install flask-mysqldb
```
```bash
  pip3 install pyyaml
```

    
## Modules used

To run this project, you will need to add the following modules

`from flask import Flask, render_template, request, redirect, url_for, session`

`from flask_mysqldb import MySQL
`

`from sql_tools import *   `

`from html_tools import *`

`import flask`

`import yaml`

`import MySQLdb.cursors`

`import re`

Note: MySQL Server(workbench) should be installed on the PC. Dump the “dispensary.sql” in the same directory.



#### These are the major steps to launch the website:


- Move all the files in one folder. Open folder as code in VS Code.
- Create virtual environment using command “python -m venv venv”
- Activate environment using command “./venv/Scripts\activate.ps1”
- Install required libraries (mentioned above)
- Run the “app.py” file using command “python ./app.py”
- Click on the URL 



#### Now after running the server you will get a login page:
![image](https://user-images.githubusercontent.com/105475941/226404419-984a5c0a-ee78-4b7d-950d-77a21bd77187.png)

For the existing users(login details should be available in the database), they can login to their account. Insert email and password and select the role correctly. You will be redirected to the home page.

If you are new user, you can click on “create new” on the bottom of the login page, you will be redirected to registration page:

![image](https://user-images.githubusercontent.com/105475941/226404979-02b5a685-a223-4032-b112-469113874bfa.png)

Here, user need to insert username, a not existing email, password and role. You credentials will be saved in the database and now you can click on login. Login with your credentials.

For example, adding these credentials:

#### Database previously: 

![image](https://user-images.githubusercontent.com/105475941/226405453-b2775cc5-5ec8-447d-b85a-9bccd96bdf63.png)

![image](https://user-images.githubusercontent.com/105475941/226405561-828912db-42f3-4012-9e30-7e8d4ab30669.png)

After hitting “Sign up” and refreshing database, new database snapshot, with updated entry:

![image](https://user-images.githubusercontent.com/105475941/226405760-020bcbe8-4d80-4ee6-b8c8-d72fd47caf4d.png)

After you are logged in, you will be able to see home page:

![image](https://user-images.githubusercontent.com/105475941/226405973-a71d2e27-d7d1-4bcf-b768-950f1793d2fc.png)

From here you can explore options. Clicking on “IIT-GN Dispensary logo” will refresh the page, “Home” will return to the same page. “Edit” allows to to update/delete the data from the tables. And “About_us” contains basic information about our project, teammates and motivation.

#### “Edit” View1:

![image](https://user-images.githubusercontent.com/105475941/226406278-90274cba-bcab-45d5-ab1d-61acf6814675.png)

#### “Edit” View2:
![image](https://user-images.githubusercontent.com/105475941/226406372-e548c29a-abe2-4b3e-9543-7513732c526d.png)


#### Editing particular table(here “equipment”):

![image](https://user-images.githubusercontent.com/105475941/226406634-0b72208a-5477-44b9-a459-2e82f22c7ae9.png)

#### “About us” view:

![image](https://user-images.githubusercontent.com/105475941/226406768-158d0ed9-d387-48f6-bf37-cbe272c75001.png)

# Content of the repository:

### Screenshots of the Web Application showing all the Functionalities

The web application shows the view of the different relations with the Insert, Update, and Delete operations on these relations. Screenshots include the view of the relation with the following operations and the results with the changes in the MySQL database itself. We also include the results which give an error due to some constraints defined by us while making the database, such as primary-key error etc.

## Prescription Table
- **View of Prescription Relation**

![prescription_web_table](https://user-images.githubusercontent.com/105475941/226407332-f955a9a1-29dd-49f4-afb9-876fb9f1934e.png)

- **View of Prescription Relation in Workbench**

![prescription_on_mysql](https://user-images.githubusercontent.com/105475941/226407615-a4dffa08-a9ac-4382-8dd2-5d7aaf72e44d.png)

- **Inserting Entries in Prescription Relation**

![insert_on_prescription](https://user-images.githubusercontent.com/105475941/226407711-255bf054-6fd0-4c99-8b30-cade07b3b04c.png)

- **Inserting Entries Result on MySql**

![insert_result_on_prescription](https://user-images.githubusercontent.com/105475941/226407763-8ab06f17-82d8-40bd-8426-94e555bd85ca.png)

- **Updating Entries in Prescription Relation**

![update_on_prescription](https://user-images.githubusercontent.com/105475941/226408095-10c71542-187b-49e9-977b-f017da14d838.png)

- **Updating Entries Result on Mysql**

![update_result_on_prescription](https://user-images.githubusercontent.com/105475941/226408137-3823c517-e7b3-49ec-bbd4-ed3de72b0e22.png)


- **Deleting Entries in Prescription Relation**

![delete_on_prescription](https://user-images.githubusercontent.com/105475941/226408279-89b9d7f3-1587-4ba4-ade4-1291ee0252af.png)

- **Deleting Entries Result on Mysql**

![delete_result_on_prescription](https://user-images.githubusercontent.com/105475941/226408312-1c8310c4-2c2e-4611-91f7-e93bfc1558b9.png)

#### Reason for the error!
Since the delete operation is performed in the Prescription Relation, which consists of the primary key of the patient, in order to hold the foreign key constraint in the delete operation, The above error is shown from MySQL and it is reflected on the page. 

## Patient Tabe

- **View of Patient Relation**

![patient_web_table](https://user-images.githubusercontent.com/105475941/226408921-4c4623cf-3ccf-4a40-b5d8-58ecf43648a0.png)

- **View of Patient Relation in Workbench**

![patient_mysql_table](https://user-images.githubusercontent.com/105475941/226409002-45284c98-400d-428f-83b4-6cc4c0145dbe.png)

- **Inserting Entries in Patient Relation**

![insert_on_patient](https://user-images.githubusercontent.com/105475941/226409042-b3f57f9d-4e85-4e7f-9846-9d18e6b5a08b.png)

- **Inserting Entries Result on Mysql**
![insert_result_on_patient](https://user-images.githubusercontent.com/105475941/226409094-2fb57657-e441-4d01-98e4-6513db0ddcbe.png)

- **Updating Entries in Patient Relation**

![update_on_patient](https://user-images.githubusercontent.com/105475941/226409295-795b52ef-bd02-4e56-b6c0-cf00f9fceb30.png)

- **Updating Entries Result on Mysql**

![update_result_on_patient](https://user-images.githubusercontent.com/105475941/226409318-83d9e439-8a6f-46e0-88e2-fbbff5a21cfe.png)

- **Deleting Entries in Patient Relation**

![delete_on_patient](https://user-images.githubusercontent.com/105475941/226409466-828973c6-79ca-4f4b-93fc-61ca3682a13c.png)

- **Deleting Entries Result on Mysql**

![delete_result_on_patient](https://user-images.githubusercontent.com/105475941/226409498-1799cc8d-f55d-4fce-975e-5e3d2d44bef1.png)

## General Visit Table

- **View of General Visit Relation**

![generalvisit_web_table](https://user-images.githubusercontent.com/105475941/226410153-c52ee1ba-a801-4636-9097-d37d53205d07.png)

- **View of General Visit Relation in Workbench**

![generalvisit_mysql_table](https://user-images.githubusercontent.com/105475941/226410203-0f5fd5de-5421-419e-ae87-c91433cfd783.png)

- **Inserting General Visit in Prescription Relation**

![insert_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410257-ac89e532-85f8-45eb-9c4d-c8c4d191f742.png)

- **Inserting General Visit Result on Mysql**  

![insert_result_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410303-46edd641-6d28-4245-954b-9f2f92b0c371.png)

- **Updating Entries in General Visit Relation**

![update_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410361-d710418f-9bb1-46d4-b514-ab4a4a3f03de.png)

- **Updating Entries in General Visit Result on Mysql** 

![update_result_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410413-df1108dc-80e3-4bb1-bb42-c50771437e6b.png)

- **Deleting Entries in General Visit Relation**

![delete_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410458-c0c2ecf7-8625-444c-b6f2-7ad935c3a302.png)

- **Deleting Entries in General Visit Result on Mysql**  

![delete_result_on_generalvisit](https://user-images.githubusercontent.com/105475941/226410487-5a26c839-f42c-4846-a1fc-5081fd0eb713.png)

## Medicine Table

- **View of Medicine Relation**

![medicine_web_table](https://user-images.githubusercontent.com/105475941/226411053-6120afbb-4295-41a8-b5a1-1af62482abc1.png)

- View of Medicine Relation in Workbench

![medicine_on_mysql](https://user-images.githubusercontent.com/105475941/226411088-9acace65-dab1-461c-9505-6d94b9480421.png)

- Inserting Medicine in Prescription Relation

![insert_on_medicine](https://user-images.githubusercontent.com/105475941/226411127-3755830b-6580-4ce2-badc-c7459b52a48e.png)

- Inserting Medicine in Prescription Result on Mysql 

![insert_result_on_medicine](https://user-images.githubusercontent.com/105475941/226411154-13be2b54-d1c6-4d9e-bd80-b745c58613bc.png)

- Updating Entries in Medicine Relation

![update_on_medicine](https://user-images.githubusercontent.com/105475941/226411184-0ef6dbae-8aa7-4056-8e68-dc3d32d243a8.png)

- Updating Entries in Medicine Result on Mysql  

![update_result_on_medicine](https://user-images.githubusercontent.com/105475941/226411207-e58ba682-1faa-4d87-ba20-bd5b247d892c.png)

- Deleting Entries in Medicine Relation

![delete_on_medicine](https://user-images.githubusercontent.com/105475941/226411242-dc115be1-3f5e-4f8e-94e2-4800185852f4.png)

- Deleting Entries in Medicine Result on Mysql  

![delete_on_medicine](https://user-images.githubusercontent.com/105475941/226411261-8040a34c-deda-48f4-a7eb-00e6203edafe.png)

## Doctor Table

- View of Doctor Relation

![doctors_web_table](https://user-images.githubusercontent.com/105475941/226411712-dcce4829-3e3d-4492-94c5-7d5376680ec3.png)

- View of Doctor Relation in Workbench

![doctors_on_mysql](https://user-images.githubusercontent.com/105475941/226411753-abd2a021-9a7c-4d64-9fcd-c9a2c8be1391.png)

- Inserting Doctor in Prescription Relation

![insert_on_doctors](https://user-images.githubusercontent.com/105475941/226411784-8d04a26f-d6e6-4576-839a-99e583ab8138.png)

- Inserting Doctor in Prescription Result on Mysql

![insert_result_on_doctors](https://user-images.githubusercontent.com/105475941/226411815-7e8408d4-c5b3-4386-8781-e8e4a1c0aea3.png)

- Updating Entries in Doctor Relation

![update_on_doctors](https://user-images.githubusercontent.com/105475941/226411850-e1b61f85-b4f4-4b22-860c-8d878a0e1909.png)

- Updating Entries in Doctor Result on Mysql

![update_result_on_doctors](https://user-images.githubusercontent.com/105475941/226411876-61c6f924-7c5e-488d-9360-17cdb509a9b5.png)

- Deleting Entries in Doctor Relation

![delete_on_doctors](https://user-images.githubusercontent.com/105475941/226411914-f8c583df-3cb2-4a3d-bc4c-9ed33a81cb10.png)

- Deleting Entries in Doctor Result on Mysql

![delete_result_on_doctors](https://user-images.githubusercontent.com/105475941/226411963-3f2c0e77-8edb-422a-aff0-5240dde5b48a.png)

## Employee Table

- View of Employee Relation

![employee_on_web](https://user-images.githubusercontent.com/105475941/226412429-8f68470c-6d81-4e7d-a064-937992c1c237.png)

- View of Employee Relation in Workbench

![employee_on_mysql](https://user-images.githubusercontent.com/105475941/226412463-464af6cf-baf8-40b6-83d9-fd9fb2a24b8b.png)

- Inserting Entries in Employee Relation

![insert_on_employee](https://user-images.githubusercontent.com/105475941/226412518-fa1cdbf1-4afa-4455-9235-ae43990a060c.png)

- Inserting Entries in Employee Result on Mysql

![insert_result_on_employee](https://user-images.githubusercontent.com/105475941/226412553-356b6e53-3228-4594-97c2-9c67864000a6.png)

- Updating Entries in Employee Relation

![update_on_employee](https://user-images.githubusercontent.com/105475941/226412609-f5a0b245-88f5-4bdf-a0fd-d34dd5e7e75b.png)

- Updating Entries in Employee Result on Mysql

![update_result_on_employee](https://user-images.githubusercontent.com/105475941/226412634-1af13f65-4ec8-4a60-8e6b-d4e6da6340e0.png)

- Deleting Entries in Employee Relation

![delete_on_employee](https://user-images.githubusercontent.com/105475941/226412669-69583008-0e26-4fe8-a28d-fd807e650f64.png)

- Deleting Entries in Employee Result on Mysql

![delete_result_on_employee](https://user-images.githubusercontent.com/105475941/226412699-43a3abd2-a2f4-464e-9104-15a5c89256bd.png)

## Medical Products

- View of Medical Products Relation

![medicalproducts_web_table](https://user-images.githubusercontent.com/105475941/226413951-6a153f2f-3cbf-4c32-940d-f52410a29dba.png)

- View of Medical Products Relation in Workbench

![medicalproducts_on_mysql](https://user-images.githubusercontent.com/105475941/226414022-e37a5c74-e23d-4307-a0ac-d4ed00aec471.png)

- Inserting Entries in Medical Products Relation

![insert_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414178-5b6983c0-f2d1-4072-b740-fc3645a0748d.png)

- Inserting Entries in Medical Products Result on Mysql

![insert_result_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414258-dc090685-fd91-4760-aa49-676078ead926.png)

- Updating Entries in Medical Products Relation

![update_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414315-7b3565e6-0195-4555-aaa1-f8d8809beb95.png)

- Updating Entries in Medical Products Result on Mysql

![update_results_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414340-1fd34ef5-b16e-4088-9302-48d2c98d162d.png)

- Deleting Entries in Medical Products Relation

![delete_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414375-fad4d9c6-137f-47c4-a4fe-16d711f5f7bf.png)

- Deleting Entries in Medical Products Result on Mysql

![delete_result_on_medicalproducts](https://user-images.githubusercontent.com/105475941/226414400-f13fe760-53f2-434c-a308-7fee4cf60626.png)

### Here is the link for other tables snapshots
- https://drive.google.com/drive/folders/1BWoMf2b5mdxWAuyzJag5LntfV9GY9Aqi?usp=share_link

## Note: 
Because of a foreign key constraint error on insertion/deletion of a record, we faced a few issues with implementing deletion and insertion on some tables. We plan to resolve this issue in further iterations of the webpage.

#### Contribution of group Members


- **Aishwarya Omar (20110008)**:
  User authentification frontend, Connected authentication frontend with backend, Integrated webapp, Report Documentation

- **Akshat Shrivastava (20110009)**:
  Frontend debugging, Backend Development, Report documentation.

- **Amaan Ansari (20110011)**: 
  Integrated frontend and developed the UI, Report compilation, Frontend Development.

- **Mahesh Dange (20110050)**:
  Frontend designing, Frontend Development, Backend Development, integrated frontend and backend,  Made Readme File, Report documentaion.

- **Dhakad Bhagat Singh (20110055)**:
   Backend debugging, Backend Development, Report compilation.

- **Govardhan Ingale (20110070)**:
  Connected database backend, Frontend Development, Report compilation.

- **Ronak Hingonia (20110170)**:
  Report compilation

- **Ojas Washimkar (20110234)**:

- **Yash Adhiya (20110235)**:
  Backend Development,Frontend designing, Report documentation.

- **Yash Kokane (20110237)**:
   User authentification backend, Frontend designing, connected database backend for authtification, report compilation.

- **Shubham Kumar (19110137)**:
  Backend Development, Frontend debugging, Report compilation.


## Refrences

Here are some refrences used - 

[Flask Tutorial](https://www.javatpoint.com/flask-tutorial)

[Database Connection](https://pynative.com/python-mysql-database-connection/)

[Youtube Tutorial](https://www.youtube.com/watch?v=yBDHkveJUf4&t=1132s&ab_channel=freeCodeCamp.org)


















