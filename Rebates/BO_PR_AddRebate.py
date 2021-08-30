'''
Add Rebate button -> Periodic Rebates Quote Table
'''
import zlib
from Newtonsoft.Json import JsonConvert
from BO_Rebates_Module import clearCustomFields, getJson

#get rebate type using rebate code description
def getRebateType(rebateName):
	table = SqlHelper.GetFirst("""
	SELECT *
	FROM BO_REBATE_TYPE
	WHERE KEY_COMBO = '{0}'
	""".format(rebateName))
	return table

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
		tableDict[idx]["QUANTITY"] 	  = row.Cells["QUANTITY"].Value
		tableDict[idx]["PERC"] 	  	  = row.Cells["PERC"].Value.ToString()
		tableDict[idx]["ACCRUAL"] 	  = row.Cells["ACCRUAL"].Value.ToString()
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
	rebateType = Quote.GetCustomField('BO_CF_REBATE_TYPE').Content
#Check if rebate is selected---------------------------------------------------
	if rebateType != "":
		#get rebate details from table
		rebate = getRebateType(rebateType)
		if rebate:#entry found
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
			recipientOptCode	= ""
			#init rebate recipient name
			rebateRecptName		= ""
			if agrType == "End Customer":#rebate recipient = end customer
				rebateRecpt	    = Quote.GetCustomField('BO_CF_END_CUSTOMER').Content
			else:#rebate recipient  = sold-to
				for attr in recipientOpt.AttributeValues:
					if attr.DisplayValue == recipientOpt.Content:
						#get recipient option code
						recipientOptCode = attr.ValueCode
						if attr.ValueCode == "1": #rebate recipient = sold-to
							rebateRecpt	= Quote.GetCustomField('BO_CF_REBATE_RECIPIENT').Content.split(",")[0]
							rebateRecptName = Quote.GetCustomField('BO_CF_REBATE_RECIPIENT').Content.split(", ")[1] #BRC US1535 27/08/2021
						else:#rebate recipient = customer group
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
#build rebate sequence for each revision----------------------------------------
			#init sequence
			seq = 0
			#is it first entry
			if periodicRebateTable.Rows.Count > 0:#no!
				#get last row of rebates
				lastRow = periodicRebateTable.Rows[periodicRebateTable.Rows.Count - 1]
				#is it same revision number?
				if lastRow["REV_NUM"] == Quote.RevisionNumber: #yes!
					#increment sequence
					seq = lastRow['SEQ'] + 1
				else: #no!
					#reset sequence
					seq = 1
			else: #yes!
				#init sequence
				seq = 1
#get external reference number
			extRefNo = Quote.CompositeNumber + Quote.RevisionNumber.ToString() + seq.ToString()
#get rebate scale---------------------------------------------------------------
			# add row
			newRow = periodicRebateTable.AddNewRow()
#42 XML for rebates-------------------------------------------------------------
			#get XML
			jsonCreate, jsonUpdate = getJson(Quote, extRefNo)
			#START MOD BRIAN 25/08
			jsonCreateEncoded = str(JsonConvert.DeserializeXNode(jsonCreate, "root")).encode('utf8')
			jsonUpdateEncoded = str(JsonConvert.DeserializeXNode(jsonUpdate, "root")).encode('utf8')
			#compress string
			newRow['XML_CREATE']   = compressString(jsonCreateEncoded)
			newRow['XML_COND']     = compressString(jsonUpdateEncoded)
			newRow['JSON_CREATE']  = compressString(jsonCreate.encode('utf8'))
			newRow['JSON_COND']    = compressString(jsonUpdate.encode('utf8'))
			#END MOD BRIAN 25/08
			#convert rebate scale values stored as dictionary
			scaleDict = convScale2Dict(rebateScaleTable)
			#compress dictionary
			compDict  = compressString(str(scaleDict))
# set the values in the table for custom fields---------------------------------
			newRow['NAME']			      		= rebateType
			newRow['REBATE_TYPE']	     		= rebate.TYPE
			newRow['NAME_ON_OUTPUT']	  		= Quote.GetCustomField('BO_CF_NAME_OUTPUT').Content
			newRow['REBATE_RECIPIENT']    		= rebateRecpt #either sold-to/selected hierarchy/endcustomer
			newRow['VALID_FROM']		  		= UserPersonalizationHelper.CovertToDate(Quote.GetCustomField('BO_CF_VALIDITY_START').Content)
			newRow['VALID_UNTIL']	      		= UserPersonalizationHelper.CovertToDate(Quote.GetCustomField('BO_CF_VALIDITY_END').Content)
			newRow['CURRENCY']		      		= Quote.GetCustomField('BO_CF_PAY_CURRENCY').Content
			newRow['REBATE_AMOUNT']		  		= Quote.GetCustomField('BO_CF_REBATE_AMOUNT').Content if Quote.GetCustomField('BO_CF_REBATE_AMOUNT').Content != "" else "0.00"
			newRow['BO_CF_RCPT_OPT']	  		= recipientOptCode
			newRow['BO_CF_SETTLE_PERIOD'] 		= setlCode
			newRow['BO_CF_SAP_NUM']		  		= Quote.GetCustomField('BO_CF_SAP_NUM').Content
			newRow['BO_CF_ISSUED_BY']	  		= Quote.GetCustomField('BO_CF_ISSUED_BY').Content
			newRow['BO_CF_VALID_UNTIL']	  		= Quote.GetCustomField('BO_CF_VALID_UNTIL').Content
			newRow['BO_CF_UNIT']		  		= Quote.GetCustomField('BO_CF_UNIT').Content
			newRow['BO_CF_REBATE_PERC']	  		= Quote.GetCustomField('BO_CF_REBATE_PERC').Content if Quote.GetCustomField('BO_CF_REBATE_PERC').Content != "" else "0.00"
			newRow['REBATE_SCALE']  	  		= compDict
			newRow['REV_NUM']			  		= Quote.RevisionNumber
			newRow['EXT_REF_NUM']		  		= extRefNo
			newRow['SEQ']			  	  		= seq
			newRow['BO_CF_SETTLE_PERIOD_VALUE'] = setlValue   #BRC US 1535 26/08/2021
			newRow['BO_CF_REBATE_RECIPIENT']    = rebateRecptName   #BRC US 1535 27/08/2021
#2215 Sold to-------------------------------------------------------------------
			#convert exlusion values stored as dictionary
			soldDict  = convSoldto2Dict(soldtoTable)
			#compress dictionary
			compDict  = compressString(str(soldDict))
			newRow['BO_SOLDTO']           = compDict
#2215 Exclusion for the rebate accumulation-------------------------------------
			#convert exlusion values stored as dictionary
			exclDict = convExcl2Dict(exclAccTable)
			#compress dictionary
			compDict  = compressString(str(exclDict))
			newRow['BO_INCL_TBL']		  = compDict
#2215 Exclusion for the rebate payment calculation------------------------------
			#convert exlusion values stored as dictionary
			exclDict = convExcl2Dict(exclCalcTable)
			#compress dictionary
			compDict  = compressString(str(exclDict))
			newRow['BO_INCL_TBL_CALC']    = compDict

			periodicRebateTable.Save()
#2215 Filter on rebate type-----------------------------------------------------
			mylist = []
			for row in periodicRebateTable.Rows:
				mylist.append("TYPE != '{0}'".format(row.Cells["REBATE_TYPE"].Value))
			Quote.CustomFields.AssignValue("BO_CF_REBATE_FILTER", " and ".join(mylist))
#clear common fields------------------------------------------------------------
			clearCustomFields(Quote)
			#reset rebate type
			Quote.CustomFields.Disallow("BO_CF_REBATE_TYPE")
			Quote.CustomFields.Allow("BO_CF_REBATE_TYPE")
			Quote.CalculateAndSaveCustomFields()
	else:#no rebate type found
		Trace.Write("'Rebate Type' is not selected")
else:
#except Exception as e:
	pass
	Trace.Write("[ERROR] Add Rebate -> " + str(e))
