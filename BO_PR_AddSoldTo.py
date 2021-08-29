
"""
Description: Add Sold-to to quote table

Input:
Attr: MG_SOLDTO

Output:
update sold to quote table

Dev: Shawn Yong, 25/07/2021, US 2215

"""

#get external id of sold to from master data table
def getCustomerId(soldToName):
	table = SqlHelper.GetFirst("""
	SELECT *
	FROM MG_CUSTOMERS
	WHERE COMPANY = '{company}'
	AND CUSTOMER_TYPE = '1'
	AND ACTIVE = 'TRUE'
	""".format(company=soldToName))
	return table.CUSTOMERID if table else ""

#add sold to to table
def addSoldTo():
	isRequired = False
	#check whether all customer group
	for attr in Quote.GetCustomField('BO_CF_RCPT_OPT').AttributeValues:
		if attr.DisplayValue == Quote.GetCustomField('BO_CF_RCPT_OPT').Content:
			if attr.ValueCode == "1": #1 sold-to
				isRequired = False
			else: #all sold-to
				isRequired = True
			break

	#get sold to name
	soldToName  = Quote.GetCustomField('BO_CF_SOLD_TO').Content
	#sold-to field has entry
	if soldToName:
		#get external for sold to
		soldToId	= getCustomerId(soldToName.split(",")[1].lstrip())
		#get sold-to table
		soldToTable = Quote.QuoteTables['BO_SOLDTO']
		#add new row to sold-to table
		newRow = soldToTable.AddNewRow()
		#set sold-to to column -> Name
		newRow.Cells['NAME'].Value  = soldToName
		#set external to column -> Sapid
		newRow.Cells['SAPID'].Value = soldToId
		#set required column
		if isRequired:
			newRow.Cells['REQUIRED'].Value = "0"
		else:
			newRow.Cells['REQUIRED'].Value = "1"
		#save changes to quote table
		soldToTable.Save()
		#reset sold-to field
		Quote.CustomFields.Disallow("BO_CF_SOLD_TO")
		Quote.CustomFields.Allow("BO_CF_SOLD_TO")
		Quote.CalculateAndSaveCustomFields()
#Filter on sold to--------------------------------------------------------------
		mylist = []
		#get sold-to already used
		for row in soldToTable.Rows:
			mylist.append("CUSTOMERID != '{0}'".format(row.Cells["SAPID"].Value))

		for item in Quote.MainItems:
			#edit only price sheets
			if item.ParentRolledUpQuoteItem == "":
				#get product
				product = item.EditConfiguration()
				#get main sold-to
				if product.Attr("MG_SOLD_TO").SelectedValue:
					mylist.append("CUSTOMERID = '{0}'".format(product.Attr("MG_SOLD_TO").SelectedValue.ValueCode[3:]))
				#get additional sold-to
				for row in product.GetContainerByName("BO_ADD_SOLD_TO_CONT").Rows:
					mylist.append("CUSTOMERID = '{0}'".format(row["SOLD_TO_NAME"].ReferencingAttribute.SelectedValue.ValueCode[3:]))

		mylist.append("ACTIVE = 'True'") #only active customers
		mylist.append("CUSTOMER_TYPE = '1'") #only sold-to
		Quote.CustomFields.AssignValue("BO_CF_SOLDTO_FILTER", " and ".join(mylist))
	else:
		Trace.Write("[INFO] No value in field BO_CF_SOLD_TO")

#add sold to to table
addSoldTo()
