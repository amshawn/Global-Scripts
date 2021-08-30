"""
US 1513
Description: Fills the pricing conditions table on quote
For each parent item on the quote a maximum of 3 entries are added to the table (price, surcharge, discount)

Input: Pre-Action quote status 'Won'
Output:

Dev: 	Rowyn Chengalanee, 05/08/2021
		15/08/2021 - Rowyn -> Updated the script

"""
from Newtonsoft.Json import JsonConvert
import zlib
from Newtonsoft.Json.Linq import JObject
from System import DateTime
from datetime import datetime

def getQuoteAttrValue(mainItem, attrName):
	for attr in mainItem.SelectedAttributes:
		if attr.Name == attrName:
			attrValue = attr.Values[0].Display
			break
	return attrValue


def addRow_PricingQuoteTable(parentName, parentGuid, condition, status, payload, revNum):
	newRow = pricQuoteTable.AddNewRow()
	newRow['PRODUCT']   = str(parentName)
	newRow['GUID']	  = str(parentGuid)
	newRow['CONDITION'] = str(condition)
	newRow['STATUS']	= str(status)
	newRow['XML']	  	= zlib.compress(str(JsonConvert.DeserializeXNode(zlib.decompress(payload), "root")))# make it xml
	newRow['JSON']	 	= payload
	newRow['REV_NUM']   = revNum

if 1 == 1:

	# define quote table for pricing conditions
	pricQuoteTable 	= Quote.QuoteTables["BO_QTB_PRICING_COND"]
	# quote table Pricing conditions count
	qTableCount 	= pricQuoteTable.Rows.Count
	# set the status
	status			= "Pending"
	#set revision number
	revNum			= Quote.RevisionNumber
#UPDATE VALIDITY DATE FOR PREVIOUSLY SENT PRICING CONDITIONS--------------------
	if qTableCount > 0:
#get list of variable keys------------------------------------------------------
# Harded coded for testing purposes, as the info is not on CPQ yet
		sOrg		= "1000"
		distCh		= "10"
		divOrg		= "PG"
# Define condition key list which will contain all pricing conditions
		appendixList = list()
		#read all price sheets
		for item in Quote.MainItems:
			#edit only price sheets
			if item.ParentRolledUpQuoteItem == "":
				#init list of variable keys
				conditionKey = list()
				#init appendix details
				appendixDict = dict()
				#get product
				product = item.EditConfiguration()
#Data from Product Attributes---------------------------------------------------
				soldTo 				= product.Attributes.GetByName("MG_SOLD_TO").GetValue() if product.Attributes.GetByName("MG_SOLD_TO") else ""
				shipTo 				= product.Attributes.GetByName("MG_SHIP_TO").GetValue() if product.Attributes.GetByName("MG_SHIP_TO") else ""
				# Read the value of hidden attribute "Sold-To"
				allSoldTo 			= product.Attributes.GetByName("MG_SOLD_TO_VALUECODES").GetValue() if product.Attributes.GetByName("MG_SOLD_TO_VALUECODES") else ""
				# Break down the string of value into a list
				allSoldToList	   	= allSoldTo[1:-1].split(", ") if allSoldTo != "['']" else list()
				# Read the value of hidden attribute "Ship-To"
				allShipTo 			= product.Attributes.GetByName("MG_SHIP_TO_VALUECODES").GetValue() if product.Attributes.GetByName("MG_SHIP_TO_VALUECODES") else ""
				# Break down the string of value into a list
				allShipToList 		= allShipTo[1:-1].split(", ") if allShipTo != "['']" else list()
				# define Pricing container
				pricingContainer	= product.GetContainerByName('BO_PRICING_CONT')
				pricingMatCodeList 	= list()
				pricingMatPrice	 	= dict()
# Loop in pricing container to get values---------------------------------------
				for row in pricingContainer.Rows:
					for column in row.Columns:
						if column.Name == "INVOICED_PRICE":
							# value  of Invoice Price column
							invPrice = column.Value if column.Value != '' else '0.00'
						if column.Name == "MATERIAL_CODE":
							# add each 'Material Code' in a list
							pricingMatCodeList.append(column.Value)
							# build a dictionary of 'Material Code' : 'Invoice Price'
							pricingMatPrice[column.Value] = invPrice
#Build variable key-------------------------------------------------------------
				# Build the Pricing structure
				for matCode in pricingMatCodeList:
					# get the price for material
					rate = pricingMatPrice[matCode]
					# check if Sold-To list is not empty
					if allSoldToList:
						for soldTos in allSoldToList:
							# build variable key
							variableKey = sOrg + distCh + divOrg + soldTos[1:-1] + matCode
							conditionKey.append(variableKey)
					# check if Ship-To list is not empty
					if allShipToList:
						for shipTos in allShipToList:
							# build variable key
							variableKey = sOrg + distCh + divOrg + shipTos[1:-1] + matCode
							conditionKey.append(variableKey)
#build dictionary---------------------------------------------------------------
				appendixDict["NAME"]		= product.Name
				appendixDict["VALID_FROM"]	= product.Attributes.GetByName("MG_VALIDITY_START_DATE").GetValue()
				appendixDict["VAR_KEY"]	  	= conditionKey
				appendixList.append(appendixDict)
#-------------------------------------------------------------------------------
		for row in pricQuoteTable.Rows:
			if row['STATUS'] == "Sent to PO" and row['CONDITION'][0] != "Z" and row['REV_NUM'] == revNum - 1:
				#get sent json
				jsonStr		= zlib.decompress(row["JSON"])
				#convert json from string to object
				jsonObj		= JObject.Parse(jsonStr)
				#get todays date
				todayDate	= Quote.DateCreated.Now
				#read json
				for conditionKey in jsonObj.ConditionKey:
					#get validity date from JSON
					validTo 		= conditionKey.ConditionHeader.ValidTo.ToString()
					validFrom 		= conditionKey.ConditionHeader.ValidFrom.ToString()
					#convert validity date from string to date
					validToDate		= DateTime(int(validTo[:4]), int(validTo[4:6]), int(validTo[6:8]))
					validFromDate	= DateTime(int(validFrom[:4]), int(validFrom[4:6]), int(validFrom[6:8]))
					#validity dates are within current period
					if  Quote.DateCreated.Now >= validFromDate and Quote.DateCreated.Now < validToDate:
						#update validity end date to today date
						conditionKey.ConditionHeader.ValidTo = Quote.DateCreated.Now.ToString('yyyyMMdd')
					else: #validity dates are not within current period
						#update validity end date to validity start date
						conditionKey.ConditionHeader.ValidTo = conditionKey.ConditionHeader.ValidFrom
					#does pricing combination exists in the appendix #2 of both agreement?
					for apdx in appendixList:
						if conditionKey.VariableKey.ToString() in apdx["VAR_KEY"]: #yes?
							date 	= datetime.strptime(apdx["VALID_FROM"], '%m/%d/%Y')
							newDate = DateTime(date.year, date.month, date.day).AddDays(-1)
							#is new date starting before valid from date
							if newDate >= validFromDate:
								conditionKey.ConditionHeader.ValidTo = newDate.ToString('yyyyMMdd')
							else:
								conditionKey.ConditionHeader.ValidTo =conditionKey.ConditionHeader.ValidFrom
							break
				#add new rows
				addRow_PricingQuoteTable(row['PRODUCT'], row['GUID'], row['CONDITION'], status, zlib.compress(RestClient.SerializeToJson(jsonObj)), row['REV_NUM'])
#-------------------------------------------------------------------------------

	# loop in Main Items in quote
	for parent in Quote.MainItems:
		# Check only the parent items
		if parent.ParentRolledUpQuoteItem == "":
			# check the parent details
			parentName 	= parent.ProductTypeName
			parentGuid 	= parent.QuoteItemGuid

			# Check Payload and add entry to quote table
			try:
				pricePayload	= getQuoteAttrValue(parent, "BO_PRICE_ECC")
				condition		= "Price"
				# add row to quote table -> Price
				addRow_PricingQuoteTable(parentName, parentGuid, condition, status, pricePayload, revNum)
			except:
				pricePayload	= None

			try:
				surchargePayload	= getQuoteAttrValue(parent, "BO_SURCHARGE_ECC")
				condition			= "Surcharge"
				# add row to quote table -> Surcharge
				addRow_PricingQuoteTable(parentName, parentGuid, condition, status, surchargePayload, revNum)
			except:
				surchargePayload	= None

			try:
				discountPayload		= getQuoteAttrValue(parent, "BO_DISCOUNT_ECC")
				condition			= "Discount"
				# add row to quote table -> Discount
				addRow_PricingQuoteTable(parentName, parentGuid, condition, status, discountPayload, revNum)
			except:
				discountPayload		= None


#1516 Add rebate payload--------------------------------------------------------
	for row in Quote.QuoteTables["BO_REBATES"].Rows:
		addRow_PricingQuoteTable(row["NAME"], '', row["REBATE_TYPE"], status, row["JSON_CREATE"], revNum)
		addRow_PricingQuoteTable(row["NAME"], '', row["REBATE_TYPE"], status, row["JSON_COND"], revNum)

	# save
	pricQuoteTable.Save()
else:
#except Exception as e:
	Trace.Write("Error in script BO_QuoteTable_PricingConditions --> "+str(e))
