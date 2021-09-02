'''
Edit button -> Periodic Rebates Quote Table
'''
import zlib
# Decompressing text
def decompressString(text):
	decompressed=zlib.decompress(text)
	return decompressed

if 1 == 1:
#define required quote table----------------------------------------------------
    rebateScaleTable    = Quote.QuoteTables['BO_REBATE_SCALE']
    periodicRebateTable = Quote.QuoteTables['BO_REBATES']
    soldtoTable 		= Quote.QuoteTables['BO_SOLDTO']
    exclAccTable	 	= Quote.QuoteTables['BO_INCL_TBL']
    exclCalcTable	 	= Quote.QuoteTables['BO_INCL_TBL_CALC']
#get values from periodic Rebate Table------------------------------------------
    for row in periodicRebateTable.Rows:
        # only for selected line
        if row.Cells["IS_SELECTED"].Value:
#set rebate recipient-----------------------------------------------------------
            if Quote.GetCustomField('MG_H_AGREEMENTTYPE').Content == "End Customer":
                Quote.CustomFields.AssignValue('BO_CF_END_CUSTOMER', row.Cells["REBATE_RECIPIENT"].Value)
            elif row.Cells["BO_CF_RCPT_OPT"].Value == "1":
                Quote.CustomFields.AssignValue('BO_CF_REBATE_RECIPIENT', row.Cells["REBATE_RECIPIENT"].Value)
# set the values in the table for custom fields---------------------------------
            Quote.CustomFields.AssignValue('BO_CF_NAME_OUTPUT', row.Cells["NAME_ON_OUTPUT"].Value)
            Quote.CustomFields.AssignValue('BO_CF_VALIDITY_START', UserPersonalizationHelper.ToUserFormat(row.Cells["VALID_FROM"].Value))
            Quote.CustomFields.AssignValue('BO_CF_VALIDITY_END', UserPersonalizationHelper.ToUserFormat(row.Cells["VALID_UNTIL"].Value))
            Quote.CustomFields.AssignValue('BO_CF_PAY_CURRENCY', row.Cells["CURRENCY"].Value)
            Quote.CustomFields.AssignValue('BO_CF_REBATE_TYPE', row.Cells["REBATE_TYPE"].Value)
            Quote.CustomFields.AssignValue('BO_CF_REBATE_AMOUNT', row.Cells["REBATE_AMOUNT"].Value.ToString())
            Quote.CustomFields.AssignValue('BO_CF_RCPT_OPT', row.Cells["BO_CF_RCPT_OPT"].Value)
            Quote.CustomFields.SelectValueByValueCode('BO_CF_SETTLE_PERIOD', row.Cells["BO_CF_SETTLE_PERIOD"].Value)
            Quote.CustomFields.AssignValue('BO_CF_SAP_NUM', row.Cells["BO_CF_SAP_NUM"].Value)
            Quote.CustomFields.AssignValue('BO_CF_ISSUED_BY', row.Cells["BO_CF_ISSUED_BY"].Value)
            Quote.CustomFields.AssignValue('BO_CF_VALID_UNTIL', row.Cells["BO_CF_VALID_UNTIL"].Value)
            Quote.CustomFields.AssignValue('BO_CF_UNIT', row.Cells["BO_CF_UNIT"].Value)
            Quote.CustomFields.AssignValue('BO_CF_REBATE_PERC', row.Cells["BO_CF_REBATE_PERC"].Value.ToString())
            #set rebate type as readonly
            Quote.GetCustomField('BO_CF_REBATE_TYPE').Editable      = False
#get rebate scale---------------------------------------------------------------
            rebateScaleTable.Rows.Clear()
            #get compressed text
            compressedTxt   = row.Cells["REBATE_SCALE"].Value
            #decompress dictionary
            decompressedTxt = decompressString(compressedTxt)
            #get dictionary
            dict            = eval(decompressedTxt)
            for idx in dict:
                # add row
                newRow = rebateScaleTable.AddNewRow()
                newRow["AMOUNT"]   = dict[idx]["AMOUNT"]
                newRow["QUANTITY"] = dict[idx]["QUANTITY"]
                newRow["PERC"]     = dict[idx]["PERC"]
                newRow["ACCRUAL"]  = dict[idx]["ACCRUAL"]
            rebateScaleTable.Save()
#2215 Sold to-------------------------------------------------------------------
            soldtoTable.Rows.Clear()
            #get compressed text
            compressedTxt   = row.Cells["BO_SOLDTO"].Value
            #decompress dictionary
            decompressedTxt = decompressString(compressedTxt)
            #get dictionary
            dict            = eval(decompressedTxt)
            for idx in dict:
                # add row
                newRow = soldtoTable.AddNewRow()
                newRow["NAME"]      = dict[idx]["NAME"]
                newRow["SAPID"]     = dict[idx]["SAPID"]
                newRow["CUST_HIER"] = dict[idx]["CUST_HIER"]
                newRow["REQUIRED"]  = dict[idx]["REQUIRED"]
            soldtoTable.Save()
#2215 Exclusion for the rebate accumulation-------------------------------------
            exclAccTable.Rows.Clear()
            #get compressed text
            compressedTxt   = row.Cells["BO_INCL_TBL"].Value
            #decompress dictionary
            decompressedTxt = decompressString(compressedTxt)
            #get dictionary
            dict            = eval(decompressedTxt)
            for idx in dict:
                # add row
                newRow = exclAccTable.AddNewRow()
                newRow["OBJECT"]      = dict[idx]["OBJECT"]
                newRow["CODE"]        = dict[idx]["CODE"]
                newRow["TOPIC"]       = dict[idx]["TOPIC"]
                newRow["EXCLUDE"]     = dict[idx]["EXCLUDE"]
                newRow["OBJECT_CODE"] = dict[idx]["OBJECT_CODE"]
            exclAccTable.Save()
#2215 Exclusion for the rebate payment calculation------------------------------
            exclCalcTable.Rows.Clear()
            #get compressed text
            compressedTxt   = row.Cells["BO_INCL_TBL_CALC"].Value
            #decompress dictionary
            decompressedTxt = decompressString(compressedTxt)
            #get dictionary
            dict            = eval(decompressedTxt)
            for idx in dict:
                # add row
                newRow = exclCalcTable.AddNewRow()
                newRow["OBJECT"]      = dict[idx]["OBJECT"]
                newRow["CODE"]        = dict[idx]["CODE"]
                newRow["TOPIC"]       = dict[idx]["TOPIC"]
                newRow["EXCLUDE"]     = dict[idx]["EXCLUDE"]
                newRow["OBJECT_CODE"] = dict[idx]["OBJECT_CODE"]
            exclCalcTable.Save()

        else: #no row selected
            Trace.Write("[WARNING] No row was selected in rebate table")
else:
#except Exception as e:
    pass
    Trace.Write('Edit -> Periodic rebates ' + str(e))

#-------------------------------------------------------------------------------------
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

if 1 == 1:
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
