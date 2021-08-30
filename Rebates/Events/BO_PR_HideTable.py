
"""
Description: Hide Inclusions and Exclusions table

Input:

Output:
Set inclusion/exclusions table permissions to hidden

Dev: Shawn Yong, 25/07/2021, US 2215

"""
from Scripting.QuoteTables import AccessLevel
from BO_Rebates_Module import getVariableList, getVariable, rebateScaleVisibility

#get end customer inclusion/exclusion table and set permission to hidden
def hideTable(field, process):
	if Quote.GetCustomField(field).Content != "True":
		#get list of tables
		tables = getVariableList(process)
		#hide tables
		for field in tables:
			#get associated fields to custom fields
			variable  = getVariable(field.LOW)
			table = Quote.QuoteTables[variable["LOW"]]
			table.AccessLevel = AccessLevel.Hidden
			table.Save()

#hide rebate recipient
def hideRebateRcpt(Quote):
	if Quote.GetCustomField('MG_H_AGREEMENTTYPE').Content == "End Customer":
		#hide rebate recipient = sold-to
		Quote.CustomFields.Disallow("BO_CF_REBATE_RECIPIENT")
		#hide rebate recipient type
		Quote.CustomFields.Disallow("BO_CF_RCPT_OPT")
		#show rebate recipient = end customer
		Quote.CustomFields.Allow("BO_CF_END_CUSTOMER")
	else:
		#hide rebate recipient = end customer
		Quote.CustomFields.Disallow("BO_CF_END_CUSTOMER")
		for attr in Quote.GetCustomField('BO_CF_RCPT_OPT').AttributeValues:
			if attr.DisplayValue == Quote.GetCustomField('BO_CF_RCPT_OPT').Content:
				if attr.ValueCode == "1": #1 sold-to
					#show rebate recipient = sold-to
					Quote.CustomFields.Allow("BO_CF_REBATE_RECIPIENT")
				else: #all sold-to
					#hide rebate recipient = sold-to
					Quote.CustomFields.Disallow("BO_CF_REBATE_RECIPIENT")
				break

#set defaulted values to custom fields
def setDefaultVal(Quote):
	#set default settlement currency
	if Quote.GetCustomField("BO_CF_PAY_CURRENCY").Content == "":
		Quote.CustomFields.SelectValueByValueCode("BO_CF_PAY_CURRENCY", Quote.SelectedMarket.CurrencyCode)
		Quote.CustomFields.AssignValue("BO_CF_CURR_SIGN", Quote.SelectedMarket.CurrencySign)
	#set default rebate unit
	if Quote.GetCustomField("BO_CF_UNIT").Content == "":
		Quote.CustomFields.SelectValueByValueCode("BO_CF_UNIT", "TNE")

if EventArgs.CurrentTabName == "Periodic Rebates":
	#1. hide rebate recipients
	hideRebateRcpt(Quote)
	#2. hide rebate amount/scale/percentage
	#get rebate type
	rebType = Quote.GetCustomField("BO_CF_REBATE_TYPE").Content
	#get rebate scale table
	scTable = Quote.QuoteTables["BO_REBATE_SCALE"]
	rebateScaleVisibility(scTable, rebType, Quote)
	#3. Set default values
	setDefaultVal(Quote)
	#4. Hide rebate type

	#5. Hide sold-to
	soldToTable = Quote.QuoteTables['BO_SOLDTO']
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
				mylist.append("CUSTOMERID = '{0}'".format(product.Attr("MG_SOLD_TO").SelectedValue.ValueCode))
			#get additional sold-to
			for row in product.GetContainerByName("BO_ADD_SOLD_TO_CONT").Rows:
				mylist.append("CUSTOMERID = '{0}'".format(row["SOLD_TO_NAME"].ReferencingAttribute.SelectedValue.ValueCode))

	mylist.append("ACTIVE = 'True'") #only active customers
	mylist.append("CUSTOMER_TYPE = '1'") #only sold-to
	Quote.CustomFields.AssignValue("BO_CF_SOLDTO_FILTER", " and ".join(mylist))
	#6. #3008 Set settlement Period
	if Quote.GetCustomField("BO_CF_SETTLE_PERIOD").Content == "": #set default value to "After the end of rebate period"
		Quote.CustomFields.SelectValueByValueCode("BO_CF_SETTLE_PERIOD", "0")
