                SQL Injection: attacks and defenses
                ===================================

ABSTRACT
---------
With its first appearance in 1998![ref-1][1]![ref-2][2], have attract so much
attention in database sciense and various other field, especially WEB
applications industry. It's a code injection technique used to attack
data-driven application. By using SQL injection, attackers can spoof identity,
tamper with existing data, cause repudiation issues such as voiding transactions
or changing balances, and even become administrators of the database server. So
far, plenty of techniques and "common practices" have been developed to tackle
this problem![ref-3][3]. This paper try to serve as a survey to discuss various
of topics about SQL injection, such as how it can be carried out, what it looks
like, and how to protect application from it. We first describe various of forms
of SQL injection by giving a few examples, and along the way we present some
popular techniques used to prevent it. Then we concludes all the materials we
have presented so far.


What is SQL-Injection ?
------------------------
SQL injection happen when programmers want to add user input dynamically into
the SQL statement they construct. When a sql statement is construct dynamically,
using external input, attacker can easily form a malicious input to alter the
behaviour of the original SQL statement, causing security problem. For example,
below is program in php that can easily be SQL-injected:

    ```php
    $query         = "SELECT * FROM users where id=$expected_data";
    ```
with a normal input like `$expected_data = 1;`, it would produce a harmless SQL
query:
    
    ```SQL
    SELECT * FROM users where id=1
    ```

However, unregular statement like `$expected_data = "1; DROP TABLE users;` would
produce a malicious query:

    ```SQL
    SELECT * FROM users where id=1; DROP TABLE users;
    ```
which would unexpectly delete table "users".
This is one of the canonical examples of SQL-injection, and it can be avoided by
disallowing multiple queries to be execute at the same time.
However, in some other examples, disallowing multiple queries does not work:
Here is a commonly routine (wrong) snippet in php for user authentication:

    ```php
    $username = $_POST['username'];
	$password = $_POST['password'];
    $sql = "SELECT uid,username FROM user WHERE username='{$username}' AND password='{$password}'";
    ```

while we can disallow more than one SQL injection to be executed at a time, a
hacket can easily come up with something like this:

    ```php
    $username = "foo' AND 1=1 --"
	$password = "whatever-password"
    ```

which would generate a malicious SQL query like this:

    ```SQL
    SELECT uid,username FROM user WHERE username='foo' AND 1=1--' AND password='whatever-password'
    ```

(note that -- is used for comments in SQL).
This is unexpected even we disallow multi-query in one statement, and enforce
input to match the single quote. With that, a malicous user can use any random
string for password and gain access to a user's account information. This can
be prevented by validate data type of input data or using Prepared 
Statement(see below).

Another kind of attack is called **Bind SQL Injection**. By using blind SQL
injection, attacker can no longer see the result of the query, but, however,
he/she can guess by the output of applications(e.g. error messages) to figure
out how internally is the query carried out and even the structure of the
database. For example, it common for web application to use this kind of URL
to query database:

    http://books.example.com/showReview.php?ID=5

and then corresponding SQL generated would be something like this:

    SELECT * FROM bookreviews WHERE ID = 5;

Upon seeing this kind of URL, an attacker will try to enter some URL like these:

    http://books.example.com/showReview.php?ID=5 OR 1=1
    http://books.example.com/showReview.php?ID=5 AND 1=2

and the corresponding SQL generated would be:

    SELECT * FROM bookreviews WHERE ID = '5' OR '1'='1';
    SELECT * FROM bookreviews WHERE ID = '5' AND '1'='2';

if the first one success and the second fail with no error message alerting
about invalid input, then we can determine that the second one can pass the
validation check(though the result is wrong) and know that this site is 
vulnerable to SQL injection attack. This is call Blind SQL Injection.


Defense against SQL injection
------------------------------

Various of techniques have been developed to protect application against SQL
injections:
    1. Escaping special characters
    2. Data-validate all external input
    3. Prepared Statements(Parameterized Queries)
    4. White List Input Validation
    5. Stored Procedures
    6. Database Permission Check

#### Escaping special characters
The manual for an SQL DBMS explains which characters have a special meaning,
which allows creating a comprehensive "blacklist" of characters that need
translation. For instance, every occurrence of a single quote (') in a parameter
must be replaced by two single quotes ('') to form a valid SQL string literal.
For example, in PHP it is usual to escape parameters using the function
"mysqli_real_escape_string()" before sending the SQL query:

```
$mysqli = new mysqli('hostname', 'db_username', 'db_password', 'db_name');
$query = sprintf("SELECT * FROM `Users` WHERE UserName='%s' AND Password='%s'",
                  $mysqli->real_escape_string($username),
                  $mysqli->real_escape_string($password));
$mysqli->query($query);
```

This is a straightforward way but may be error-prone sometimes because it
usually impossible for someone to remember all those special characters and it
is easy to forget to escape a given string in applications.

#### Data-validate all external input

   (blah blah blah...)



#### Prepared Statement
This is propably the most prevelant method against SQL injection and thus
deserved a more detailed discussion.

Essentially, the root of SQL injection is **mixing code and data**.
A SQL statement is a legitimate 'program'. It is, like other program, be parsed
and executed by the SQL server. When we are dynamically construct SQL statement,
however, we are mixing code and data. Once data become part of the program, they
can alter the behavior of our program, causing unexpected result. So,
intuitively, all we have to do is seperate _code_ and _data_. That is where this
common technique called **Prepared statement** come to help.

A prepared statement is also called parameterized statement. It takes the form
of a SQL template, into which certain placeholder can be substituted substitued
during each execution. It offer many advantages:

    * Execution speed-up. Because Prepared Statement is essentially a template,
    it can be compiled once and used many time afterward without repeated
    compilation, thus can speed up program execution.
    
    * Avoid SQL injection. When using Prepared Statement, one can send SQL-code
    and SQL-data seperately to SQL server, so that it is compiled seperately and
    cannot be mixed. With this, we can garauntee that external data will not
    alter the behaviour of our program.

Example of Prepared Statement in php:

    ```php
    $username = isset($_GET['username']) ? $_GET['username'] : '';
    $sql = "SELECT uid,username FROM user WHERE username=?";
	$stmt = $mysqli->prepare($sql);
	$stmt->bind_param("s", $username);
	$stmt->execute();
    ```

In a MySQL client, it's something like this:

   ```
   mysql> PREPARE stmt1 FROM 'SELECT uid, username FROM user WHERE username=?';
   mysql> SET @u_name = 'alex';
   mysql> EXECUTE stmt1 USING @u_name;
   ```

With prepared statement like these, the parameter value(i.e., $username) is
combined with a **compiled  statement**, not a SQL string, this way, only legal
input can be accepted by the SQL server, and no harm can occur.

However, Prepared Statement is not perfect and cannot protect us completely SQL
injection. Actually, in case of dynamically constructed SQL, there are four
types of it:
    * string
    * number
    * identifier
    * syntax keyword
Prepared Statement can only cover the first two but not the last two because the
structure of the dynamic query itself cannot be parametrized and certain query
features cannot be parametrized. With the last two, you have to use some other
techniques such as "White List Input Validation".


#### White List Input Validation
White List Input Validation try to ensure database security by only allowing
some words to appear in a SQL query. Those words are put altogether into a
"white list"(thus the name White List Input Validation). In contrast, Black List
Input Validation, which is used in Escaping special character, try to achieve
that by using a black list and disallowing any character in the black list.
Comparing the two, we can see that the White List Input Validation is more
robust and efficient. Also, where trying to dynamically put SQL identifier or
syntax keyword into a SQL query, White List Input Validation can provide a
greate help. For example:

  ```
  // Value whitelist
  // $dir can only be 'DESC' or 'ASC'
  $dir = !empty($direction) ? 'DESC' : 'ASC'; 
  $query = "SELECT uid FROM user ORDER BY uid $dir";
  ```

As can be seen in the above example, we now have a white list that only allow
two SQL keywords to appear in our final SQL query statement. The $dir variable
can only be 'DESC' or 'ASC'. This way, we can have a dynamically constructed SQL
query statement while at the same time ensure database security.


#### Stored Procedures

------- Unsafe Example
    ```java
    String query = "SELECT account_balance FROM user_data WHERE user_name = "
      + request.getParameter("customerName");
    
    try {
    	Statement statement = connection.createStatement( … );
    	ResultSet results = statement.executeQuery( query );
    }
    ```
    (what if the famoust "OR 1=1"? Then it always evaluate to true...)
    

-------- Safe Example (using Stored-procedure)
    ```java
    // This should REALLY be validated
    String custname = request.getParameter("customerName");
    try {
    	CallableStatement cs =
            connection.prepareCall("{call sp_getAccountBalance(?)}");
    	cs.setString(1, custname);
    	ResultSet results = cs.executeQuery();		
    	// … result set handling 
    } catch (SQLException se) {			
    	// … logging and error handling
    }
    ```
    (note that the `sp_getAccountBalance()' should have been defined in the
     database)

-------- difference between Stored-procedure and Prepared-statement:
    The difference between prepared statements and stored procedures is that
    the SQL code for a stored procedure is defined and stored in the database
    itself, and then called from the application

(TODO: fullfilled this block...)


#### Database Permission Check

     (blah blah blah ...)




Conclusion
-----------
(blah blah blah ...)




TODO: real world SQL-injection example

[1]: http://www.esecurityplanet.com/network-security/how-was-sql-injection-discovered.html
[2]: http://phrack.org/issues/54/8.html#article
[3]: 2015 Web Application Attack Report (WAAR)
