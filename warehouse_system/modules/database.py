import pymysql

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="mysql-fbb4b6a-heckgrammar-bca2.i.aivencloud.com",
  password="AVNS_3K1SgLzxo8FcpkUD0I2",
  read_timeout=timeout,
  port=26619,
  user="avnadmin",
  write_timeout=timeout,
)
  
try:
  cursor = connection.cursor()
  cursor.execute('''SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA='defaultdb' ''')
  print(cursor.fetchall())
finally:
  connection.close()