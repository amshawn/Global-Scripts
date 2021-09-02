'''
Update & Save button -> Periodic Rebates Quote Table
'''
import zlib
from Newtonsoft.Json import JsonConvert
from BO_Rebates_Module import clearCustomFields, getJson
#convert exclusions quote table to dictionary object
def convExcl2Dict(table):
	tableDict = dict()
	idx = 0
	for row in table.Rows:
		tableDict[idx] = {}
		tableDict[idx]["OBJECT"] 	  = row.Cells["OBJECT"].Value
		tableDict[idx]["CODE"] 		  = row.Cells["CODE"].Value
		tableDict[idx]["TOPIC"] 	  = row.Cells["TOPIC"].Value
		tableDict[idx]["EXCLUDE"] 	  = row.Cells["EXCLUDE"].Value
		tableDict[idx]["OBJECT_CODE"] = row.Cells["OBJECT_CODE"].Value
		idx += 1
	table.Rows.Clear()
	table.Save()
	return tableDict

#convert scale quote table to dictionary object
def convScale2Dict(table):
	tableDict = dict()
	idx = 0
	for row in table.Rows:
		tableDict[idx] = {}
		tableDict[idx]["AMOUNT"] 	  = row.Cells["AMOUNT"].Value.ToString()
		tableDict[idx]["QUANTITY"] 	  = row.Cells["QUANTITY"].Value.ToString()
		tableDict[idx]["PERC"] 	  	  = row.Cells["PERC"].Value.ToString()
		tableDict[idx]["ACCRUAL"] 	  = row.Cells["ACCRUAL"].Value
		idx += 1
	table.Rows.Clear()
	table.Save()
	return tableDict

#convert sold to quote table to dictionary object
def convSoldto2Dict(table):
	tableDict = dict()
	idx = 0
	for row in table.Rows:
		tableDict[idx] = {}
		tableDict[idx]["NAME"] 	    = row.Cells["NAME"].Value
		tableDict[idx]["COUNTRY"]   = row.Cells["COUNTRY"].Value
		tableDict[idx]["SAPID"]     = row.Cells["SAPID"].Value
		tableDict[idx]["CUST_HIER"] = row.Cells["CUST_HIER"].Value
		tableDict[idx]["REQUIRED"]  = row.Cells["REQUIRED"].Value
		idx += 1
	table.Rows.Clear()
	table.Save()
	return tableDict

# Compressing text
def compressString(text):
	compressed = zlib.compress(text)
	return compressed

if 1 == 1:
#define required quote table----------------------------------------------------
	rebateScaleTable	= Quote.QuoteTables['BO_REBATE_SCALE']
	periodicRebateTable = Quote.QuoteTables['BO_REBATES']
	exclAccTable	 	= Quote.QuoteTables['BO_INCL_TBL']
	exclCalcTable	 	= Quote.QuoteTables['BO_INCL_TBL_CALC']
	soldtoTable 		= Quote.QuoteTables['BO_SOLDTO']
#get rebate recipient-----------------------------------------------------------
	#get recipient option [1 Sold-to, All Sold-to]
	recipientOpt		= Quote.GetCustomField('BO_CF_RCPT_OPT')
	#get agreement type [Sold-to, End customer]
	agrType				= Quote.GetCustomField('MG_H_AGREEMENTTYPE').Content
	#set rebate recipient
	rebateRecpt 		= ""
	#set rebate recipient code
	recipientOptCode 	= "1"
	#init rebate recipient name
	rebateRecptName		= ""
	if agrType == "End Customer":#rebate recipient = end customer
		rebateRecpt		= Quote.GetCustomField('BO_CF_END_CUSTOMER').Content
		Quote.GetCustomField('BO_CF_END_CUSTOMER').Editable = True
	else:#rebate recipient  = sold-to
		Quote.GetCustomField('BO_CF_REBATE_RECIPIENT').Editable = True
		for attr in recipientOpt.AttributeValues:
			if attr.DisplayValue == recipientOpt.Content:
				if attr.ValueCode == "1": #rebate recipient = sold-to
					recipientOptCode = attr.ValueCode
					rebateRecpt	 = Quote.GetCustomField('BO_CF_REBATE_RECIPIENT').Content.split(",")[0]
					rebateRecptName = Quote.GetCustomField('BO_CF_REBATE_RECIPIENT').Content.split(",")[1] #BRC US1535 27/08/2021
				else:#rebate recipient = customer group
					recipientOptCode = attr.ValueCode
					for row in soldtoTable.Rows:
						if row.Cells["CUST_HIER"].Value == "True":
							rebateRecpt = row.Cells["NAME"].Value
#get settlement period----------------------------------------------------------
			#init settlement code
			setlCode = ""
			setlValue = ""
			#get custom field
			setlPeriod = Quote.GetCustomField('BO_CF_SETTLE_PERIOD')
			for attr in setlPeriod.AttributeValues:
				if attr.DisplayValue == setlPeriod.Content:
					#get settlement code
					setlCode = attr.ValueCode
					# BRC US 1535 26/08/2021 --->  get settlement value
					setlValue = attr.DisplayValue
#get rebate scale---------------------------------------------------------------
	#convert rebate scale values stored as dictionary
	scaleDict = convScale2Dict(rebateScaleTable)
	#compress dictionary
	scaleDict  = compressString(str(scaleDict))
#2215 Sold to-------------------------------------------------------------------
	#convert exlusion values stored as dictionary
	soldDict  = convSoldto2Dict(soldtoTable)
	#compress dictionary
	soldDict  = compressString(str(soldDict))
#2215 Exclusion for the rebate accumulation-------------------------------------
	#convert exlusion values stored as dictionary
	exclAccDict = convExcl2Dict(exclAccTable)
	#compress dictionary
	exclAccDict = compressString(str(exclAccDict))
#2215 Exclusion for the rebate payment calculation------------------------------
	#convert exlusion values stored as dictionary
	exclCalDict = convExcl2Dict(exclCalcTable)
	#compress dictionary
	exclCalDict = compressString(str(exclCalDict))
# update periodic Rebate Table--------------------------------------------------
	for row in periodicRebateTable.Rows:
		# execute conditions only if a row is checked
		if row.Cells["IS_SELECTED"].Value:
# set the values in the table for custom fields---------------------------------
			row.Cells['NAME_ON_OUTPUT'].Value	   			= Quote.GetCustomField('BO_CF_NAME_OUTPUT').Content
			row.Cells['REBATE_RECIPIENT'].Value    			= rebateRecpt #either sold-to/selected hierarchy/endcustomer
			row.Cells['VALID_FROM'].Value		  			= UserPersonalizationHelper.CovertToDate(Quote.GetCustomField('BO_CF_VALIDITY_START').Content)
			row.Cells['VALID_UNTIL'].Value	       			= UserPersonalizationHelper.CovertToDate(Quote.GetCustomField('BO_CF_VALIDITY_END').Content)
			row.Cells['CURRENCY'].Value		       			= Quote.GetCustomField('BO_CF_PAY_CURRENCY').Content
			row.Cells['REBATE_AMOUNT'].Value	   			= Quote.GetCustomField('BO_CF_REBATE_AMOUNT').Content if Quote.GetCustomField('BO_CF_REBATE_AMOUNT').Content != "" else "0.00"
			row.Cells['BO_CF_RCPT_OPT'].Value	   			= recipientOptCode
			row.Cells['BO_CF_SETTLE_PERIOD'].Value			= setlCode
			row.Cells['BO_CF_SAP_NUM'].Value	   			= Quote.GetCustomField('BO_CF_SAP_NUM').Content
			row.Cells['BO_CF_ISSUED_BY'].Value	   			= Quote.GetCustomField('BO_CF_ISSUED_BY').Content
			row.Cells['BO_CF_VALID_UNTIL'].Value   			= Quote.GetCustomField('BO_CF_VALID_UNTIL').Content
			row.Cells['BO_CF_UNIT'].Value		   			= Quote.GetCustomField('BO_CF_UNIT').Content
			row.Cells['BO_CF_REBATE_PERC'].Value   			= Quote.GetCustomField('BO_CF_REBATE_PERC').Content if Quote.GetCustomField('BO_CF_REBATE_PERC').Content != "" else "0.00"
			row.Cells['REBATE_SCALE'].Value  	   			= scaleDict
			row.Cells['BO_SOLDTO'].Value           			= soldDict
			row.Cells['BO_INCL_TBL'].Value		   			= exclAccDict
			row.Cells['BO_INCL_TBL_CALC'].Value    			= exclCalDict
			row.Cells['BO_CF_SETTLE_PERIOD_VALUE'].Value    = setlValue   #BRC US 1535 26/08/2021
			row.Cells['BO_CF_REBATE_RECIPIENT'].Value       = rebateRecptName   #BRC US 1535 27/08/2021
			row.Cells["IS_SELECTED"].Value                  = False
			row.Cells["IS_UPDATED"].Value                   = True
			row.Cells["SAP_SENDING"].Value                  = "Pending"
#get XML------------------------------------------------------------------------
			jsonCreate, jsonUpdate       = getJson(Quote, row.Cells["EXT_REF_NUM"].Value)
			jsonUpdateEncoded            = str(JsonConvert.DeserializeXNode(jsonUpdate, "root")).encode('utf8')
			row.Cells['XML_COND'].Value  = compressString(jsonUpdateEncoded)
			row.Cells['JSON_COND'].Value = compressString(jsonUpdate.encode('utf8'))
			break
#save table
	periodicRebateTable.Save()
#set rebate type as readonly
	Quote.GetCustomField('BO_CF_REBATE_TYPE').Editable = True
	Quote.GetCustomField('BO_CF_PAY_CURRENCY').Editable = True
#clear common fields------------------------------------------------------------
	clearCustomFields(Quote)
	#reset rebate type
	Quote.CustomFields.Disallow("BO_CF_REBATE_TYPE")
	Quote.CustomFields.Allow("BO_CF_REBATE_TYPE")
	Quote.CalculateAndSaveCustomFields()
else:
#except Exception as e:
	pass
	Trace.Write('Update & Save ' + str(e))
