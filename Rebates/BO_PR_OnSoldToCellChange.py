#ScriptExecutor.ExecuteGlobal("BO_PR_SetInclExcl", {"EventArgs":EventArgs})
if Param is not None:
	EventArgs = Param.EventArgs
	#check whether all customer group
	for attr in Quote.GetCustomField('BO_CF_RCPT_OPT').AttributeValues:
		if attr.DisplayValue == Quote.GetCustomField('BO_CF_RCPT_OPT').Content:
			if attr.ValueCode == "1": #1 sold-to
				isRequired = False
			else: #all sold-to
				isRequired = True
			break

	#get new value
	for cell in EventArgs.Cells:
		#get changed column name
		colName = cell.ColumnName
		#get new value
		newVal	= cell.Value

	if colName == "CUST_HIER":
		#clear table
		for row in EventArgs.Table.Rows:
			for cell in row.Cells:
				if cell.ColumnName == "CUST_HIER":
					cell.Value = False
				elif cell.ColumnName == "REQUIRED":
					if newVal or not isRequired:#set not required
						cell.Value = "1"
					else:#set required
						cell.Value = "0"
		#get new value
		for cell in EventArgs.Cells:
			#set new value
			cell.Value = newVal
