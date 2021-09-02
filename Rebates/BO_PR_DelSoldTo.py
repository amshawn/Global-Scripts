soldToTable = Quote.QuoteTables['BO_SOLDTO']
#Filter on sold to--------------------------------------------------------------
mylist = []
#get sold-to already used
for row in soldToTable.Rows:
	mylist.append("EXTERNALID != '{0}'".format(row.Cells["SAPID"].Value))

for item in Quote.MainItems:
	#edit only price sheets
	if item.ParentRolledUpQuoteItem == "":
		#get product
		product = item.EditConfiguration()
		#get main sold-to
		if product.Attr("MG_SOLD_TO").SelectedValue:
			mylist.append("EXTERNALID = '{0}'".format(product.Attr("MG_SOLD_TO").SelectedValue.ValueCode))
		#get additional sold-to
		for row in product.GetContainerByName("BO_ADD_SOLD_TO_CONT").Rows:
			mylist.append("EXTERNALID = '{0}'".format(row["SOLD_TO_NAME"].ReferencingAttribute.SelectedValue.ValueCode))

mylist.append("ACTIVE = 'True'") #only active customers
mylist.append("CUSTOMER_TYPE = '1'") #only sold-to
Quote.CustomFields.AssignValue("BO_CF_SOLDTO_FILTER", " and ".join(mylist))
