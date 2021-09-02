"""
Description:
			#1987 - Set up internal control for Sold To selection inside Appendix #3s
					Control - Cannot select a sold to which has already been selected within the same Appendix #3

Input:
		Quote
Output:
		SQL Pre-selection filter for attribute BO_SOLD_TO

Dev: Shawn Yong, 31/08/2021

"""
#get sold-to quote table
soldToTable = Quote.QuoteTables['BO_SOLDTO']
#Initiate Sold To external IDs list
extIds = list()
#Initiate Sold To customer IDs list
cusIds = list()
#get sold-to already used
for row in soldToTable.Rows:
	cusIds.append(row.Cells["SAPID"].Value)

for item in Quote.MainItems:
	#edit only price sheets
	if item.ParentRolledUpQuoteItem == "":
		#get product
		product = item.EditConfiguration()
		#get main sold-to
		if product.Attr("MG_SOLD_TO").SelectedValue:
			extIds.append(product.Attr("MG_SOLD_TO").SelectedValue.ValueCode)
		#get additional sold-to
		for row in product.GetContainerByName("BO_ADD_SOLD_TO_CONT").Rows:
			if row.Columns["SOLD_TO_NAME"].ReferencingAttribute is not None:
				addSoldTo = row.Columns["SOLD_TO_NAME"].ReferencingAttribute.SelectedValue.ValueCode if row.Columns["SOLD_TO_NAME"].ReferencingAttribute.SelectedValue is not None else str()
				if addSoldTo != "":
					extIds.append(addSoldTo)

if len(extIds) > 0 and len(custIds) > 0:
	#Get all active sold to customers that havent been selected yet
	Result = """
	CUSTOMER_TYPE = '1'
	AND ACTIVE = 'TRUE'
	AND CUSTOMERID NOT IN({custIds})
	AND EXTERNALID NOT IN({soldTos})""".format(custIds= str(cusIds)[1:-1], soldTos= str(extIds)[1:-1])
elif len(extIds) > 0:
	Result = """
	CUSTOMER_TYPE = '1'
	AND ACTIVE = 'TRUE'
	AND EXTERNALID NOT IN({soldTos})""".format(soldTos= str(extIds)[1:-1])
elif len(custIds) > 0:
	Result = """
	CUSTOMER_TYPE = '1'
	AND ACTIVE = 'TRUE'
	AND CUSTOMERID NOT IN({custIds})""".format(custIds= str(cusIds)[1:-1])
else: #Get all active sold tos
	Result = """CUSTOMER_TYPE = '1' AND ACTIVE = 'TRUE'"""
