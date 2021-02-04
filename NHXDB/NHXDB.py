import sys, os, csv, hashlib, shutil
from ast import literal_eval

class database:

	def __init__(self, verbose=False):
		try:
			self.logged_in = False
			self.logged_DB = None
			if verbose == True:
				self.verbose = True
			else:
				self.verbose = False
			if sys.platform.lower().startswith("linux") or sys.platform.lower().startswith("darwin"):
				defaultwd = "/usr/local/share/"
			elif sys.platform.lower().startswith("win32"): 
				defaultwd = "C:/Users/" + os.getlogin() + "/AppData/Local/"
			if os.path.exists(defaultwd + "NHX") != True:
				os.mkdir(defaultwd + "NHX")
				os.mkdir(defaultwd + "NHX/NHXDB-Data")
			elif os.path.exists(defaultwd + "NHX/NHXDB-Data") != True:
				os.mkdir(defaultwd + "NHX/NHXDB-Data")
			self.defaultwd = defaultwd + "NHX/NHXDB-Data/"
			os.mkdir(self.defaultwd + "cache")
			shutil.rmtree(self.defaultwd + "cache")
			self.initialized = True
			self.permissions = True
			self.pop = False
		except PermissionError:
			self.permissions = False
			self.initialized = False


	def isPermitted(self):
		if self.permissions == True:
			return 200
		else:
			return 101


	def returner(self, code):
		if type(code) != int:
			return code
		if self.verbose == False:
			return code
		else:
			error = {
				100: "Database System is not yet initialized",
				101: "Insufficient Permissions or permission denied",
				300: "Invalid Entry",
				301: "The entry already exists",
				302: "Incomplete Data",
				303: "Credentials Error",
				304: "Cannot process because you are not logged in",
				404: "Not Found",
				500: "Data file for the specified table already exists",
				501: "Cannot increment any data type other than int",
				502: "Cannot have more than one Primary Field in same Table",
				503: "Primary/Index values cannot be specified as Null",
				504: "Default cannot be Null if field is specified as not Null",
				505: "Attributes cannot be other than Primary, Index or Unique",
				506: "Cannot create two fields with same names",
				507: "Cannot have length more than 255 for int, 16384 for str",
				508: "Cannot have a bool data type for a field specified as attributed field",
				509: "Specified operation is unsupported",
				510: "Invalid Default values for he specified Field",
				600: "Values for a non Null Field is not specified",
				601: "Values provided do not match their data types",
				602: "Values provided are longer than the size allocated",
				603: "Unique and Primary values can not have previously contained values",
				604: "Primary and Index fields cannot be empty",
				605: "Cannot find a valid criteria",
				606: "Cannot compare using int operands on non int fields",
				607: "Cannot have the right operand as non int on int comparisons",
				608: "Expected Left operand as field Name, no field with specified name found",
				609: "Cannot find required operands",
				610: "No Criteria provided",
				700: "Unknown Internal Error"
				}
			if code == 200:
				return code
			else:
				print("NHXError (" + str(code) + "): " + error[code] + ".")
				raise SystemExit
				

	def __validator(self, db_properties, no_cred=False):
		self.db_properties = db_properties
		if type(db_properties) != dict:
			# Returns status code 300 = Invalid Entry
			return self.returner(300)
		if "name" in db_properties and "username" in db_properties and "password" in db_properties and no_cred == False:
			if type(db_properties["name"]) == str and type(db_properties["username"]) == str and type(db_properties["password"]) == str:
				self.database_name = self.db_properties["name"].lower()
				self.database_usr = self.db_properties["username"]
				self.database_pass = self.db_properties["password"]
			else:
				return self.returner(300)
		elif no_cred == True and "name" in db_properties:
			if type(db_properties["name"]) == str:
				self.database_name = self.db_properties["name"]
			else:
				return self.returner(300)
		else:
			# Returns status code 302 = Incomplete
			return self.returner(302)
		return self.returner(200)


	def create(self, db_properties):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		status_code = self.__validator(db_properties)
		if status_code != 200:
			return self.returner(status_code)
		if os.path.exists(self.defaultwd + self.database_name) and os.path.isfile(self.defaultwd + self.database_name + "/config.NHX"):
			# Returns status code 301 = Already Exists
			return self.returner(301)
		else:
			os.mkdir(self.defaultwd + self.database_name)
			with open(self.defaultwd + self.database_name + "/config.NHX", "w") as handler:
				encoded = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
				pass_encoded = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
				handler.write(self.database_name + "|" + str(encoded) + "|" + str(pass_encoded))
		# Returns status code 200 = Success
		return self.returner(200)


	def login(self, db_properties):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		self.status_code = self.__validator(db_properties)
		if self.status_code != 200:
			return self.returner(self.status_code)
		# Verification Starts
		if os.path.isfile(self.defaultwd + self.database_name + "/config.NHX") == False and os.path.exists(self.defaultwd + self.database_name + "/tables/") == False:
			# Returns status code 404 = Not found
			self.status_code = 404
			return self.returner(404)
		with open(self.defaultwd + self.database_name + "/config.NHX") as readf:
			self.database_usr = self.database_usr
			self.database_pass = self.database_pass
			content = readf.read()
			content = content.split("|")
			verification = content[1]
			post_verification = content[2]
			verified = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
			post_verified = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
			if verification == verified and post_verification == post_verified:
				self.logged_in = True
				self.logged_DB = self.database_name
				return self.returner(200)
			else:
				# Returns status code 303 = Credentials error
				return self.returner(303)


	def drop(self):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		shutil.rmtree(self.defaultwd + self.database_name)
		self.logged_in = False
		return self.returner(200)


	def backup(self, path):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if type(path) != str:
			return self.returner(300)
		shutil.make_archive(self.defaultwd + "cache/" + self.database_name, "zip", self.defaultwd + self.database_name)
		file = open(self.defaultwd + "cache/" + self.database_name + ".zip", "r+b")
		data = file.read()
		file.close()
		to_write = data[2:] + 64*b"\x4e\x48\x58"
		file = open(path + self.database_name + ".NHX", "w+b")
		file.write(to_write)
		file.close()
		os.remove(self.defaultwd + "cache/" + self.database_name + ".zip")
		return self.returner(200)


	def restore(self, db_properties):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		status_code = self.__validator(db_properties)
		if status_code != 200:
			return self.returner(status_code)
		if "file" not in db_properties:
			return self.returner(302)
		if type(db_properties["file"]) != str:
			return self.returner(300)
		if os.path.isfile(db_properties["file"]) != True:
			return self.returner(404)
		file = open(db_properties["file"], "r+b")
		data = file.read()
		file.close()
		to_restore = b"PK" + data[:-192]
		file = open(self.defaultwd + "cache.NHX", "w+b")
		file.write(to_restore)
		file.close()
		os.mkdir(self.defaultwd + "cache.?.?.?NHX")
		shutil.unpack_archive(self.defaultwd + "cache.NHX", self.defaultwd + "cache.?.?.?NHX/", "zip")
		file = open(self.defaultwd + "cache.?.?.?NHX/config.NHX", "r")
		content = file.read()
		file.close()
		content = content.split("|")
		name = content[0]
		os.remove(self.defaultwd + "cache.NHX")
		verification = content[1]
		post_verification = content[2]
		verified = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
		post_verified = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
		if verification == verified and post_verification == post_verified:
			os.rename(self.defaultwd + "cache.?.?.?NHX", name)
			self.status_code = 200
			return self.returner(200)
		else:
			shutil.rmtree(self.defaultwd + "cache.?.?.?NHX")
			self.status_code = 303
			return self.returner(303)


class table:


	def __init__(self, db, table_name):
		self.defaultwd = db.defaultwd
		self.logged_DB = db.logged_DB
		self.initialized = db.initialized
		self.logged_in = db.logged_in
		self.database_name = db.database_name
		self.returner = db.returner
		if type(table_name) != str:
			self.ntable = True
			return
		self.ntable = False
		if os.path.exists(self.defaultwd + self.logged_DB + "/tables/" + table_name.lower()) == False:
			self.__tablexists = False
			self.fields = []
			self.indexdata = []
		else:
			self.__tablexists = True
			with open(self.defaultwd + self.logged_DB + "/tables/" + table_name.lower() + "/config.NHX", "r+", newline='') as file:
				reader = csv.reader(file, delimiter="|")
				for index, row in enumerate(reader):
					if index == 0:
						self.fields = row
						break
			cfields = []
			for field in self.fields:
				cfields.append(literal_eval(field))
			self.fields = cfields
			indexread = []
			for field in self.fields:
				if field["attribute"] != None:
					indexread.append(field["name"].lower())
			indexlines = []
			with open(self.defaultwd + self.logged_DB + "/tables/" + table_name.lower() + "/index.NHX", "r+", newline="") as file:
				reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
				for row in reader:
					indexlines.append(row)
			self.indexdata = indexlines
		self.table_name = table_name


	def __valitable(self, table_fields):
		primaryy = False
		field_names = []
		for field in table_fields:
			if type(field) == str:
				field = literal_eval(field)
			if "name" not in field or "type" not in field:
				return self.returner(302)
			if ("name" in field and type(field["name"]) != str) or ("type" in field and type(field["type"]) != str) or ("length" in field and type(field["length"]) != int) or ("ai" in field and type(field["ai"]) != bool) or ("null" in field and type(field["null"]) != bool) or ("default" in field and ((field["type"] == "str" and type(field["default"]) != str) or (field["type"] == "int" and type(field["default"]) != int) or (field["type"] == "bool" and type(field["default"]) != bool) or (field["type"] == "float" and type(field["default"]) != float)) and (field["default"] != None)) or ("attribute" in field and ((type(field["attribute"]) != str) and (field["attribute"] != None))):
				return self.returner(300)
			if "name" not in field or "type" not in field: 
				return self.returner(302)
			if "ai" in field and field["ai"] == True and field["type"].lower() != "int":
				# Returns status code 501 = Cannot increment other type than int
				return self.returner(501)
			if "attribute" in field and field["attribute"] != None and field["attribute"].lower() == "primary" and primaryy == False:
				primaryy = True
			elif "attribute" in field and field["attribute"] != None and field["attribute"].lower() == "primary" and primaryy == True:
				# Returns status code 502 = Cannot have more than 1 Primary
				return self.returner(502)
			if "null" in field and field["null"] == True and "attribute" in field and (field["attribute"].lower() == "primary" or field["attribute"].lower() == "index"):
				# Returns status code 503 = Primary or Index field cannot be Null
				return self.returner(503)
			if "default" in field and field["default"] == "null" and "null" in field and (field["null"] == False or field["null"] == ""):
				# Returns status code 504 = Default cannot be Null if the field cannot be null
				return self.returner(504)
			if "length" in field and type(field["length"]) == int and (((field["type"].lower() == "int" and field["length"] > 255) or (field["type"].lower() == "str" and field["length"] > 16384))):
				# Returns status code 507 = Cannot have length more than 255 for int and more than 16384 for str
				return self.returner(507)
			if "attribute" in field and field["type"].lower() == "bool":
				# Returns status code 508 = Cannot have bool type in an attributed field
				return self.returner(508)
			if "attribute" in field and field["attribute"] != None and field["attribute"].lower() != "primary" and field["attribute"].lower() != "index" and field["attribute"].lower() != "unique":
				# Returns status code 505 = Attribute cannot be other than Primary, Index or Unique
				return self.returner(505)
			if field["name"].lower() in field_names:
				# Returns status code 506 = Cannot create two fields with same name
				return self.returner(506)
			else:
				field_names.append(field["name"].lower())
		return self.returner(200)


	def create(self, structure, override=False):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.ntable == True:
			return self.returner(300)
		if self.logged_in != True:
			return self.returner(304)
		if type(structure) != list:
			return self.returner(300)
		no_field = len(structure)
		if os.path.exists(self.defaultwd + self.database_name + "/tables/") == False:
			os.mkdir(self.defaultwd + self.database_name + "/tables/")
		if os.path.exists(self.defaultwd + self.database_name + "/tables/" + self.table_name) and os.path.isfile(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/config.NHX"):
			return self.returner(301)
		if os.path.exists(self.defaultwd + self.database_name + "/tables/" + self.table_name) == False:
			os.mkdir(self.defaultwd + self.database_name + "/tables/" + self.table_name)
		status_code = self.__valitable(structure)
		if status_code != 200:
			return self.returner(status_code)
		to_write = []
		to_write_index = []
		to_write_data = []
		for field in structure:
			buff = {"name": field["name"].lower(), "type": field["type"]}
			if "length" in field and type(field["length"]) == int and ((field["type"].lower() == "int" and field["length"] < 256) or field["type"].lower() == "str" and field["length"] < 16385):
				buff.update({"length": field["length"]})
			elif field["type"].lower() == "int":
				buff.update({"length": 255})
			elif field["type"].lower() == "float":
				buff.update({"length": 255})
			elif field["type"].lower() == "bool":
				buff.update({"length": 5})
			else:
				buff.update({"length": 16384})
			if "ai" in field and field["ai"] == True:
				buff.update({"ai": True})
			else:
				buff.update({"ai": False})
			if "null" in field and field["null"] == True:
				buff.update({"null": True})
			else:
				buff.update({"null": False})
			if "default" in field and (((type(field["default"]) == int and field["type"] != "int") or (type(field["default"]) == str and field["type"] != "str") or (type(field["default"]) == bool and field["type"] != "bool") or (type(field["default"]) == float and field["type"] != "float")) or (len(str(field["default"])) > buff["length"])):
				# Returns status code 510 = Invalid default values for Field
				return self.returner(510)
			elif "default" in field and ("ai" not in field or field["ai"] != True):
				buff.update({"default": field["default"]})
			else:
				buff.update({"default": None})
			if "attribute" in field and field["attribute"] != None and (field["attribute"].lower() == "unique" or field["attribute"].lower() == "index" or field["attribute"].lower() == "primary"):
				buff.update({"attribute": field["attribute"].lower()})
			else:
				buff.update({"attribute": None})
			if "attribute" in field and field["attribute"] != None and (field["attribute"].lower() == "unique" or field["attribute"].lower() == "index" or field["attribute"].lower() == "primary"):
				to_write_index.append(buff["name"].lower())
			else:
				to_write_data.append(buff["name"].lower())
			to_write.append(buff)
		with open(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/config.NHX", "w+", newline='') as file:
			writer = csv.writer(file, delimiter="|")
			writer.writerow(to_write)
			self.fields = to_write
		if (os.path.isfile(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/nindex.NHX") == True or os.path.isfile(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/index.NHX")) and override == False:
			# Returns status code 500 = Data file for the current table exists
			return self.returner(500)
		with open(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/index.NHX", "w+", newline='') as file:
			self.indexdata = []
		if os.path.isfile(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/nindex.NHX") == True and override == False:
			# Returns status code 500 = Data file for the current table exists
			return self.returner(500)
		with open(self.defaultwd + self.database_name + "/tables/" + self.table_name + "/nindex.NHX", "w+", newline='') as file:
			pass
		self.__tablexists = True
		return self.returner(200)


	def drop(self):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if self.__tablexists == False:
			return self.returner(404)
		shutil.rmtree(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower())
		self.fields = []
		self.indexdata = []
		self.__tablexists = False
		return self.returner(200)


	def truncate(self):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if self.__tablexists == False:
			return self.returner(404)
		head = []
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "w") as file:
			pass
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "w") as file:
			pass
		self.indexdata = []
		return self.returner(200)
	

	def alter(self, values):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if "fields" not in values or "operation" not in values:
			return self.returner(302)
		if type(values) != dict or type(values["operation"]) != str or type(values["fields"]) != list:
			return self.returner(300)
		if self.__tablexists == False:
			return self.returner(404)
		if values["operation"].lower() == "add":
			cfields = []
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/config.NHX", "r+") as file:
				reader = csv.reader(file, delimiter="|")
				for index, row in enumerate(reader):
					if index == 0:
						cfields = row
						break
			for field in values["fields"]:
				if type(field) != dict:
					return self.returner(300)
				if "name" not in field or "type" not in field:
					return self.returner(302)
				if ("name" in field and type(field["name"]) != str) or ("type" in field and type(field["type"]) != str) or ("length" in field and type(field["length"]) != int) or ("ai" in field and type(field["ai"]) != bool) or ("null" in field and type(field["null"]) != bool) or ("default" in field and type(field["default"]) != str) or ("attribute" in field and type(field["attribute"]) != str):
					return self.returner(300)
			table_fields = cfields + values["fields"]
			status_code = self.__valitable(table_fields)
			if status_code != 200:
				return self.returner(status_code)
			to_write = []
			for field in table_fields:
				if type(field) == str:
					field = literal_eval(field)
				buff = {"name": field["name"].lower(), "type": field["type"]}
				if "length" in field and type(field["length"]) == int and ((field["type"] == int and field["length"] < 256) or field["type"] == str and field["length"] < 16385):
					buff.update({"length": field["length"]})
				elif field["type"].lower() == "int":
					buff.update({"length": 255})
				elif field["type"].lower() == "float":
					buff.update({"length": 255})
				elif field["type"].lower() == "bool":
					buff.update({"length": 5})
				else:
					buff.update({"length": 16384})
				if "ai" in field and field["ai"] == True:
					buff.update({"ai": True})
				else:
					buff.update({"ai": False})
				if "null" in field and field["null"] == True:
					buff.update({"null": True})
				else:
					buff.update({"null": False})
				if "default" in field and (((type(field["default"]) == int and field["type"] != "int") or (type(field["default"]) == str and field["type"] != "str") or (type(field["default"]) == bool and field["type"] != "bool") or (type(field["default"]) == float and field["type"] != "float")) or (len(str(field["default"])) > buff["length"])):
					# Returns status code 510 = Invalid default values for Field
					return self.returner(510)
				elif "default" in field and ("ai" not in field or field["ai"] != True):
					buff.update({"default": field["default"]})
				else:
					buff.update({"default": None})
				if "attribute" in field:
					buff.update({"attribute": field["attribute"]})
				else:
					buff.update({"attribute": None})
				to_write.append(buff)
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/config.NHX", "w+", newline='') as file:
				writer = csv.writer(file, delimiter="|")
				writer.writerow(to_write)
			self.fields = to_write
			to_update = {}
			for field in values["fields"]:
				data = None
				if "default" not in field:
					if field["type"] == "int":
						data = 0
					elif field["type"] == "float":
						data = 0.00
					elif field["type"] == "str":
						data = ""
					elif field["type"] == "bool":
						data = False
				else:
					data = field["default"]
				to_update.update({field["name"]: data})
			status = self.update(self.table_name, {
				"fields": to_update,
				"criteria": "*"	})
			if status != 200:
				return self.returner(700)
		elif values["operation"].lower() == "drop":
			to_drop = values["fields"]
			fields = []
			to_update = []
			for field in values["fields"]:
				if type(field) != str:
					return self.returner(300)
			to_edit = {}
			for field in values["fields"]:
				to_edit.update({field: None})
			self.pop = True
			status_code = self.update(self.table_name, {"fields": to_edit, "criteria": "*"})
			self.pop = False
			if status_code != 200:
				return self.returner(status_code)
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/config.NHX", "r+", newline="") as file:
				reader = csv.reader(file, delimiter="|")
				for index, row in enumerate(reader):
					if index == 0:
						fields = row
			for field in fields:
				field = literal_eval(field)
				if field["name"].lower() in to_drop:
					pass
				else:
					to_update.append(field)
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/config.NHX", "w+", newline='') as file:
				writer = csv.writer(file, delimiter='|')
				writer.writerow(to_update)
			self.fields = to_update
		else:
			# Returns status code 509 = Unsupported Operation
			return self.returner(509)
		return self.returner(200)


	def insert(self, values):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if type(values) != dict:
			return self.returner(300)
		field_names_nindex = []
		field_names_index = []
		if self.__tablexists == False:
			return self.returner(404)
		nindexread = []
		indexread = []
		for field in self.fields:
			if field["attribute"] != None:
				indexread.append(field["name"].lower())
			else:
				nindexread.append(field["name"].lower())
		indexvalues = {}
		nindexvalues = {}
		for field in self.fields:
			if field["ai"] != True:
				if ((field["name"].lower() not in values and field["null"] != True) or (values[field["name"].lower()] == "")) and (field["ai"] == False and field["default"] == None):
					# Returns status code 600 = Values for a non Null field is not specified
					return self.returner(600)
				if (field["type"].lower() == "int" and type(values[field["name"]]) != int) or (field["type"] == "float" and type(values[field["name"]]) != float) or (field["type"] == "str" and type(values[field["name"]]) != str) or ((field["type"] == "bool" and type(values[field["name"]]) != bool)):
					# Returns status code 601 = Values provided do not match their types
					return self.returner(601)
				if len(str(values[field["name"]])) > field["length"]:
					# Returns status code 602 = Values provided are longer than the size allocated
					return self.returner(602)
			else:
				pass
			if field["name"].lower() in values:
				if field["attribute"] != None:
					indexvalues.update({field["name"].lower(): values[field["name"]]})
					if field["attribute"].lower() == "unique" or field["attribute"].lower() == "primary":
						file = open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='')
						reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
						flagged = False
						for row in reader:
							if str(values[field["name"].lower()]) == str(row[field["name"]]):
								flagged = True
								break
						if flagged:
							# Returns status code 603 = Unique and Primary values can not have previous values
							return self.returner(603)
				else:
					nindexvalues.update({field["name"].lower(): values[field["name"]]})
			else:
				if field["default"] != None and field["attribute"] != None:
					indexvalues.update({field["name"]: field["default"]})
				elif field["default"] != None and field["attribute"] == None:
					nindexvalues.update({field["name"]: field["default"]})
				if field["attribute"] != None and field["ai"] != True:
					indexvalues.update({field["name"]: ""})
				if field["attribute"] == None and field["ai"] != True:
					nindexvalues.update({field["name"]: ""})
				if field["attribute"] != None and field["ai"] == True:
					if os.path.getsize(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX") != 0:
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+") as file:
							data = file.read().splitlines()[-1]
						data = data.split("|")
						index_no = indexread.index(field["name"].lower())
						required = int(data[index_no]) + 1
						indexvalues.update({field["name"].lower(): required})
					else:
						indexvalues.update({field["name"].lower(): 0})
				if field["attribute"] == None and field["ai"] == True:
					if os.path.getsize(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX") != 0:
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+") as file:
							data = file.read().splitlines()[-1]
						data = data.split("|")
						index_no = nindexread.index(field["name"].lower())
						required = int(data[index_no]) + 1
						nindexvalues.update({field["name"].lower(): required})
					else:
						nindexvalues.update({field["name"].lower(): 0})
				if field["attribute"] == "primary" or field["attribute"] == "index":
					# Returns status code 604 = Primary and Index fields cannot contain be empty
					return self.returner(604)
		indexed = open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "a+", newline="")
		nindexed = open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "a+", newline="")
		indexwrite = csv.DictWriter(indexed, delimiter="|", fieldnames=indexread)
		nindexwrite = csv.DictWriter(nindexed, delimiter="|", fieldnames=nindexread)
		nindexwrite.writerow(nindexvalues)
		indexwrite.writerow(indexvalues)
		nindexed.close()
		indexed.close()
		self.indexdata.append(indexvalues)
		return self.returner(200)


	def update(self, criteria, fields):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if type(fields) != dict:
			return self.returner(300)
		if self.__tablexists == False:
			return self.returner(404)
		nindexread = []
		indexread = []
		to_alter = []
		for field_name in fields:
			to_alter.append(field_name)
		for field in self.fields:
			if field["attribute"] != None:
				indexread.append(field["name"].lower())
			else:
				nindexread.append(field["name"].lower())
		flagged = True
		if criteria == "*":
			for field in self.fields:
				if field["name"] in to_alter:
					if self.pop != True:
						if field["attribute"] == "primary" or field["attribute"] == "unique":
							return self.returner(603)
						if (field["null"] == False) and ([field["name"]] == "" or fields[field["name"]] == None) and (field["ai"] == False and field["default"] == None):
							return self.returner(600)
						if len(str(fields[field["name"]])) > field["length"]:
							return self.returner(602)
						if (field["type"].lower() == "int" and type(fields[field["name"]]) != int) or (field["type"] == "float" and type(fields[field["name"]]) != float) or (field["type"] == "str" and type(fields[field["name"]]) != str) or ((field["type"] == "bool" and type(fields[field["name"]]) != bool)):
							return self.returner(601)
					flagged = False
					to_up = []
					if field["attribute"] != None:
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='') as file:
							reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
							for index, row in enumerate(reader):
								if self.pop and field["name"] in fields:
									row.pop(field["name"])
									to_up.append(row)
								else:
									row.update({field["name"] : fields[field["name"]]})
									to_up.append(row)
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "w+", newline='') as file:
							if self.pop:
								indexread.remove(field["name"])
							writer = csv.DictWriter(file, fieldnames=indexread, delimiter="|")
							for index, row in enumerate(to_up):
								writer.writerow(row)
					else:
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
							reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
							for index, row in enumerate(reader):
								if self.pop and field["name"] in fields:
									row.pop(field["name"])
									to_up.append(row)
								else:
									row.update({field["name"] : fields[field["name"]]})
									to_up.append(row)
						with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "w+", newline='') as file:
							if self.pop:
								nindexread.remove(field["name"])
							writer = csv.DictWriter(file, fieldnames=nindexread, delimiter="|")
							for index, row in enumerate(to_up):
								writer.writerow(row)
		elif type(criteria) == str and criteria != "*":
			flagged = False
			splitted = []
			typ = 0
			operand = 1
			left = 2
			right = 3
			operands = []
			if "==" in criteria:
				splitted = ["all", "=="] + criteria.split("==")
			elif "!=" in criteria:
				splitted = ["all", "!="] + criteria.split("!=")
			elif ">=" in criteria:
				splitted = ["if", ">="] + criteria.split(">=")
			elif "<=" in criteria:
				splitted = ["if", "<="] + criteria.split("<=")
			elif "<" in criteria:
				splitted = ["if", "<"] + criteria.split("<")
			elif ">" in criteria:
				splitted = ["if", ">"] + criteria.split(">")
			else:
				# Returns status code 605 = Cannot find a valid criteria
				return self.returner(605)
			for operanda in splitted:
				operands.append(operanda.strip())
			flagged = False
			try:
				int(operands[right])
			except ValueError:
				flagged = True
			if operands[right] == "" or operands[left] == "":
				# Returns status code 609 = Cannot find essential Operands
				return self.returner(609)
			if operands[typ] == "if" and flagged:
				# Returns status code 607 = Cannot have the right operand as non int on int comparisons
				return self.returner(607)
			results = False
			crit = {}
			for fieldaa in self.fields:
				if fieldaa["name"] == operands[left]:
					results = True
					if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
						# Returns status code 606 = Cannot compare with int operands on non int fields
						return self.returner(606)
					else:
						if fieldaa["attribute"] != None:
							crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": True})
						else:
							crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": False})
			if results != True:
				# Returns status code 608 = Expected Left operand as A field Name, none found
				return self.returner(608)
			line_no = []
			if field["attribute"] != None:
				if crit["is_index"]:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				else:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					# Returns status code 700 = Unknown Internal Error
					return self.returner(700)
			else:
				if crit["is_index"]:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				else:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					return self.returner(700)
			for field in fields:
				nindexlines = []
				indexlines = []
				for fieldx in self.fields:
					if field == fieldx["name"]:
						if (fieldx["attribute"] != None and(fieldx["attribute"] == "primary" or fieldx["attribute"] == "index")) and (fields[field] == "" or fields[field] == None):
							return self.returner(604)
						if (fieldx["null"] == False) and (fields[field] == "" or fields[field] == None) and (fieldx["ai"] == False and fieldx["default"] == None):
							return self.returner(600)
						if len(str(fields[field])) > fieldx["length"]:
							return self.returner(602)
						if (fieldx["type"].lower() == "int" and type(fields[field]) != int) or (fieldx["type"] == "float" and type(fields[field]) != float) or (fieldx["type"] == "str" and type(fields[field]) != str) or ((fieldx["type"] == "bool" and type(fields[field]) != bool)):
							return self.returner(601)
						flag = False
						if fieldx["attribute"] == "unique" or fieldx["attribute"] == "primary":
							file = open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='')
							reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
							flagged = False
							for row in reader:
								if str(fields[fieldx["name"].lower()]) == str(row[fieldx["name"]]):
									flag = True
									break
							if flag:
								return self.returner(603)
						break
				if field in indexread:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline="") as file:
						reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
						for row in reader:
							indexlines.append(row)
					for line in line_no:
						indexlines[line].update({field: fields[field]})
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "w+", newline='') as file:
						writer = csv.DictWriter(file, delimiter="|", fieldnames=indexread)
						for line in indexlines:
							writer.writerow(line)
					self.indexdata = indexlines
				if field in nindexread:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline="") as file:
						reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
						for row in reader:
							nindexlines.append(row)
					for line in line_no:
						nindexlines[line].update({field: fields[field]})
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "w+", newline='') as file:
						writer = csv.DictWriter(file, delimiter="|", fieldnames=nindexread)
						for line in nindexlines:
							writer.writerow(line)
		else:
			return self.returner(300)
		return self.returner(200)


	def delete(self, criteria):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if type(criteria) != str:
			return self.returner(300)
		if os.path.exists(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower()) == False:
			return self.returner(404)
		nindexread = []
		indexread = []
		for field in self.fields:
			if field["attribute"] != None:
				indexread.append(field["name"])
			else:
				nindexread.append(field["name"])
		splitted = []
		typ = 0
		operand = 1
		left = 2
		right = 3
		operands = []
		if "==" in criteria:
			splitted = ["all", "=="] + criteria.split("==")
		elif "!=" in criteria:
			splitted = ["all", "!="] + criteria.split("!=")
		elif ">=" in criteria:
			splitted = ["if", ">="] + criteria.split(">=")
		elif "<=" in criteria:
			splitted = ["if", "<="] + criteria.split("<=")
		elif "<" in criteria:
			splitted = ["if", "<"] + criteria.split("<")
		elif ">" in criteria:
			splitted = ["if", ">"] + criteria.split(">")
		else:
			return self.returner(605)
		for operanda in splitted:
			operands.append(operanda.strip())
		flagged = False
		try:
			int(operands[right])
		except ValueError:
			flagged = True
		if operands[right] == "" or operands[left] == "":
			return self.returner(609)
		if operands[typ] == "if" and flagged:
			return self.returner(607)
		crit = {}
		results = False
		for fieldaa in self.fields:
			if fieldaa["name"] == operands[left].lower():
				results = True
				if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
					return self.returner(606)
				else:
					if fieldaa["attribute"] != None:
						crit.update({"name": operands[left].lower(), "value": operands[right], "type": operands[operand], "is_index": True})
					else:
						crit.update({"name": operands[left].lower(), "value": operands[right], "type": operands[operand], "is_index": False})
		if results != True:
			return self.returner(608)
		line_no = []
		if field["attribute"] != None:
			if crit["is_index"]:
				with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				# Returns status code 700 = Unknown Internal Error
				return self.returner(700)
		else:
			if crit["is_index"]:
				with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				return self.returner(700)
		nindexlines = []
		indexlines = []
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
			for row in reader:
				indexlines.append(row)
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
			for row in reader:
				nindexlines.append(row)
		count = 0
		for line in line_no:
			nindexlines.pop(line - count)
			indexlines.pop(line - count)
			count = count + 1
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/index.NHX", "w+", newline="") as file:
			writer = csv.DictWriter(file, delimiter="|", fieldnames=indexread)
			for row in indexlines:
				writer.writerow(row)
		self.indexdata = indexlines
		with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "w+", newline="") as file:
			writer = csv.DictWriter(file, delimiter="|", fieldnames=nindexread)
			for row in nindexlines:
				writer.writerow(row)
		return self.returner(200)


	def select(self, criteria):
		if self.initialized != True:
			# Returns status code 100 = Database System not Initialized Yet
			return 100
		if self.logged_in != True:
			return self.returner(304)
		if self.ntable == True:
			return self.returner(300)
		if type(criteria) != str:
			return self.returner(300)
		if os.path.exists(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower()) == False:
			return self.returner(404)
		nindexread = []
		indexread = []
		for field in self.fields:
			if field["attribute"] != None:
				indexread.append(field["name"].lower())
			else:
				nindexread.append(field["name"].lower())
		if criteria == "*":
			nindexlines = []
			indexlines = self.indexdata
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline="") as file:
				reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
				for row in reader:
					nindexlines.append(row)
			tout = []
			try:
				nindexlines[0]
			except IndexError:
				return self.returner(indexlines)
			try:
				indexlines[0]
			except IndexError:
				return self.returner(nindexlines)
			for index, row in enumerate(indexlines):
				row.update(nindexlines[index])
				tout.append(row)
			return self.returner(tout)
		if criteria != "*":
			splitted = []
			typ = 0
			operand = 1
			left = 2
			right = 3
			operands = []
			if "==" in criteria:
				splitted = ["all", "=="] + criteria.split("==")
			elif "!=" in criteria:
				splitted = ["all", "!="] + criteria.split("!=")
			elif ">=" in criteria:
				splitted = ["if", ">="] + criteria.split(">=")
			elif "<=" in criteria:
				splitted = ["if", "<="] + criteria.split("<=")
			elif "<" in criteria:
				splitted = ["if", "<"] + criteria.split("<")
			elif ">" in criteria:
				splitted = ["if", ">"] + criteria.split(">")
			else:
				return self.returner(605)
			for operanda in splitted:
				operands.append(operanda.strip())
			flagged = False
			try:
				int(operands[right])
			except ValueError:
				flagged = True
			if operands[right] == "" or operands[left] == "":
				return self.returner(609)
			if operands[typ] == "if" and flagged:
				return self.returner(607)
			crit = {}
			results = False
			for fieldaa in self.fields:
				if fieldaa["name"] == operands[left].lower():
					results = True
					if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
						return self.returner(606)
					else:
						if fieldaa["attribute"] != None:
							crit.update({"name": operands[left].lower(), "value": operands[right], "type": operands[operand], "is_index": True})
						else:
							crit.update({"name": operands[left].lower(), "value": operands[right], "type": operands[operand], "is_index": False})
			if results != True:
				return self.returner(608)
			line_no = []
			if field["attribute"] != None:
				if crit["is_index"]:
					for index, row in enumerate(self.indexdata):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
				else:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					# Returns status code 700 = Unknown Internal Error
					return self.returner(700)
			else:
				if crit["is_index"]:
					for index, row in enumerate(self.indexdata):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
				else:
					with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					return self.returner(700)
			nindexlines = []
			indexlines = self.indexdata
			with open(self.defaultwd + self.logged_DB + "/tables/" + self.table_name.lower() + "/nindex.NHX", "r+", newline="") as file:
				reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
				for row in reader:
					nindexlines.append(row)
			tout = []
			for line in line_no:
				to_append = {}
				to_append.update(indexlines[line])
				to_append.update(nindexlines[line])
				tout.append(to_append)
			return self.returner(tout)
