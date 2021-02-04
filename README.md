# NHXDB

NHXDB is a lightweight Database which combines the SQL language with the ease of ORM syntax
# Update v1.3.0
- ##### Performance Improvements and bug fixes
# Features currently supported

  - _Logging in/Creating of Database_
  - _Deleting a Database_
  - _Backing up of Database in its own archive format, .NHX_
  - _Restoring the Database via the same .NHX file_
  -  _Creating a table with currently following supported features:_ 
        - _Null_
        - _Default_
        - _Index_
        - _Unique_
        - _Primary_
  - _Modifying the table_
  - _Truncating a table_
  - _Deleting a whole table_
  - _Inserting Data in the table with the following types of data supported:_
    - _Integers_
    - _Floating Numbers_
    - _Boolean_
    - _Strings_
- _Selecting data from the table_
- _Updating data from the table_
- _Deleting data from the table_

# Installation

NHXDB requires Python version 3 or above.
Open up your Command Prompt or Terminal and type the following command to download NHXDB module.

```sh
$ pip install NHXDB
```
Make sure you have pip installed.
You have now successfuly installed NHXDB module.
Now to get started in your Python shell, write:

```sh
import NHXDB
```

### Functions and Syntax
NHXDB syntax is made as closer as possible to the syntax of Python. Moreover, this is designed to be more developer friendly and so, instead of giving exceptions on any kind of error, this returns a pre-defined status code that a developer can use to analyze the error or so.

The main database object is called by the following syntax:
```sh
database = NHXDB.database(<verbose=False>)
```
If verbose functionality is required, use 1 or True as argument to enable verbosity (or otherwise verbose=True). This allows to return, instead of status code, an exception on screen (when occured).
All the functions are then called on the ```database``` variable.
#### .isPermitted()
Checks whether the permissions to read/write is granted in the desired folder. Returns 200 if granted, 101 if denied.
#### .create(properties)
To create a new database, with ```properties``` as an argument. The ```properties``` is a dictionary with ```name```, ```username```, and ```password``` as key. "name" is the name of the database to be created.  Returns a status code.
>You are recommended to use more than 8 characters in both username and password to prevent any kind of brute-force attack, however there is no compulsion on that.
#### .login(properties)
To login in a database. The ```properties``` argument is the same as in ```create()```.  Returns a status code.
> Notice: All functions other than ```create``` and ```restore``` REQUIRE to be logged in via this function first.
#### .drop()
To delete a database. Requires no argument.  Returns a status code.
#### .backup(path)
To backup a database. Requires a ```path``` argument of full path to where the backup in .NHX format should be stored.  Returns a status code.
#### .restore(properties)
To restore a database back from backup file. For additional security and preventing anyone from restoring a backup, a ```properties``` argument is given, which is a dictionary, with all same keys as that of ```login``` and requires additional key in the dictionary, named ```file``` which is the full path ___including___ the file name of the backup. Returns a status code.
For example: ```"C:\path\to\file.NHX"```
#### table(table_name)
For manipulation of table, you must initialize a table object with name of the table: ```table = NHXDB.table("users")```. All below functions rely on table(table_name) object.
#### .create(structure)
To create a table. This requires a ```structure``` argument. Structure is a __list__ of dictionaries for the structure of table fields. These dictionaries represent how many field would be there in the table. Each dictionary require at least __2 keys__, ```name``` and ```type```. The "name" being the name of the field, and "type" being any of the type of field from following: ```int, float, bool and str```. Returns a status code.
##### For example:
####
```sh
database = NHXDB.database()
database.login(your_credentials_here)
table = NHXDB.table("users")
table.create(
    [{
        "name": "UserID",
        "type": "int",
        "length": 11,
        "attribute": "primary",
        "null": False,
        "ai": True,
    },
    {
        "name": Password,
        "type": "str"
    }]
)
```
The ```name``` and ```type``` decleration is mandatory, the rest are as follows:

| Field  | Description | Default Value
| ------ | ------ | --------- |
| length  | Maximum length of field | 255 for int and float, 16384 for str
| null | Field value can be Empty |False 
| ai | Auto Increment an int field by 1 | False  
| default | The default value for a field | None (even if it is used and parallely ```ai``` is used, it defaults to None)
| attribute | The default attribute (primary, unique or index) | None

 Primary vs Unique vs Index will be differentiated later here.
#### .alter(properties)
This is used to make any kind of modifications in the structure of Table. ```Properties``` is a dictionary with keys, ```operation```, one of operation from: "add" or "drop" field(s), and ```fields```, a __list__. For __"add"__ operation, the list contains dictionaries of fields to be added, whereas in __"drop"__ operation, the list only contains the field names to drop. Returns a status code.
##### For Example: 
###
```sh
# To add a field(s) to the table "users"
table.alter({
    "operation": "add",
    fields = [{
        "name": "on_spotify",
        "type": "bool"
    }]
})
# To drop/delete a field(s) from the table "users"
table.alter({
    "operation": "drop",
    fields = ["on_spotify", "userid"]
})
```
> Notice, NHXDB is case insensitive so Username = username, better is to write all lower case letters.
#### .drop()
Drops/Deletes a table. Takes ```table_name``` as an argument, which is string, the name of the table to delete.
#### .truncate(table_name)
Same as drop table but just deletes the data inside the table, not the structure itself. Returns a status code.
#### .insert(data)
Inserts a data in the table the function is called on. Takes a dictionary ```data``` as an argument, with ```field name``` as key(s) itself and it's value being the value to add. Returns a status code.
##### For Example:
###
```sh
# To insert 12 in UserId and "secret_password" in Password
table.insert_data({
    "userid": 12,
    "password": "secret_password"
})
```
#### .select(criteria)
To select specific data in the table meeting the ```criteria```. Criteria and table_name being __str__, ```criteria``` follows Python's rule of matching criteria. To return every record, use '*' only in criteria. Returns a list of each record containing of dictionaries with ```field name``` as the key and the data as their values.
##### For Example:
###
```sh
# To get every record in the table Usernames
table.select("*") # Returns [{example: value} etc]
# To get records only with "secret_password" as its "Password" field data
table.select("password == secret_password") # Returns list with dictionaries only matching the described criteria
```
#### .update(properties)
Updates the existing data in the table with properties as a dictionary with key ```criteria```, same as that for ```select()```, and key ```fields```, as a dictionary containing ```field name``` as key(s) for the dictionary and their value as the data to be updated. Returns a status code. If field(s) added, and data exists already for the table, the values defaulted for the field(s) is as follows:

| Field Type | Default Data |
|----|----|
|int|0
|str|" " (Empty String)
|float| 0.00
|bool| False


##### For Example:
###
```sh
# To update every record's UserID and Password having UserID greater than 12
table.update({ 
    fields: {
    "UserID": 21,
    "Password": "new_random_password"
    },
    "criteria": "UserID >= 12"
})
```
#### .delete(criteria)
Deletes records from table with matching ```criteria```. Returns a status code.
### Primary vs Unique vs Index
##### Starting from Bottom, what does each mean in NHXDB?
####
>Index fields are those fields which are meant to be quickly accessible in contrast to the data in other fields. The fields are indexed in a file just like you may index a page in a book, to read it later or just quickly opening a specific page of the book. It works the same way.
####
>Unique fields are also indexed, just like Index fields. The difference between Unique and Index is that unique fields value can only occur once in a table, another record with same value as before is not acceptable by the table.
####
> Lastly, a Primary field is also a Unique field, the real differencewhich lies is that in a table, Index and Unique fields can be more than one in number, but the Primary field is single in the whole table and there cannot be any other primary field in a table. Consider it as your distinct identity card number. It works the same way.



## Status Codes
Since this Database is designed to be as developer friendly as possible, we believe that we can make the module even more developer friendly by rather than giving back exceptions, giving them a status code so they can analyze the problem. Moreover, the annoying popups of exceptions does make a bit untidy, and for cleaner interfaces, the NHXDB uses a cleaner pre-defined status codes. The pre-defined status codes are defined in the following table:

| Status Code | Meaning |
| --------| ---------|
| 100 | Database System not Initialized Yet
| 101 | Permissions Error
| 200 | Success
| 300 | Invalid Entry
| 301 | Already Exists
| 302 | Incomplete
| 303 | Credentials error
| 304 | Not Logged In
| 404 | Not found
| 500 | Data file for the current table exists
| 501 | Cannot increment other type than int
| 502 | Cannot have more than 1 Primary
| 503 | Primary or Index field cannot be Null
| 504 | Default cannot be Null if the field cannot be null
| 505 | Attribute cannot be other than Primary, Index or Unique
| 506 | Cannot create two fields with same name
| 507 | Cannot have length more than 255 for int and more than 16384 for str
| 508 | Cannot have bool type in an attributed field
| 509 | Unsupported Operation
| 510 | Invalid Default values for Field
| 600 | Values for a non Null field is not specified
| 601 | Values provided do not match their types
| 602 | Values provided are longer than the size allocated
| 603 | Unique and Primary values can not have previous values
| 604 | Primary and Index fields cannot be empty
| 605 | Cannot find a valid criteria
| 606 | Cannot compare with int operands on non int fields
| 607 | Cannot have the right operand as non int on int comparisons
| 608 | Expected Left operand as A field Name, none found
| 609 | Cannot find essential Operands
| 610 | No criteria given
| 700 | Unknown Internal Error

> Key: 1xx is Database Setting Up, 200 is Success, 3xx is Database related error, 404 is not found error for any, 5xx is Table related Error, 6xx is data related error, and 700 is Internal error. (Approximately)

**Found it useful? Go, install the module and get started!**
