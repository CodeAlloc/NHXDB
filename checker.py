import NHXDB
DB = NHXDB.db()
# Test Values
valuesx = {
	"name": "Test",
	"username": "NHX",
	"password": "xxsadnjsdbnasnd",
	"file": "/root/nhx.NHX"
	}
contentx = {
	"name": "NHX",
	"fields": [{
		"name": "True", 
		"length": 255,
		"attribute": "unique",
		"type": "str",
		"ai": False,
	},
	{
		"name": "Password", 
		"length": 22,
		"attribute": "primary",
		"type": "int",
		"ai": True,
		"null": False
	},
	{
		"name": "hash", 
		"length": 22,
		"type": "int",
		"ai": True,
		"null": False
	}]
	}
valuex = {
	"table_name": "NHX",
	"operation": "add",
	"fields":[{
		"name": "hq",
		"type": "int"
	}]
	}
dropx = {
	"table_name": "NHX",
	"operation": "drop",
	"fields": ["true"]
	}
datax = {
	"true": "dsadsaddsa",
	"hq": 1331,
	"password": 9714227
	}
criteria = {
	"fields": {
		"true": "SomethfsfsjfgdingDIFF",
		"password": 12164342113,
		"hq": 101
		},
	"criteria": "hash >= 2"
	}
status = DB.isPermitted()
status = DB.create(valuesx)
status = DB.login(valuesx)
status = DB.drop()
status = DB.backup("/root/")
status = DB.restore(valuesx)
status = DB.create_table(contentx)
status = DB.alter_table(valuex)
status = DB.alter_table(dropx)
status = DB.drop_table("NHX")
status = DB.insert_data("NHX", datax)
status = DB.select_data("NHX", "*")
status = DB.update_data("NHX", criteria)
status = DB.delete_data("NHX", "hash >= 1")
status = DB.truncate_table("NHX")
print(status)