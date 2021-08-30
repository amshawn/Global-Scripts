
"""
US 1513
Description: Creates the pricing conditions when product is added/updated to quote
Pricing conditions are created based on values in the pricing container
The data is stored in hidden attribute on product - BO_PRICE_ECC
Note that the data is compressed using zlib and needs to be decompressed for readability

Input:

Output:


Dev: 04/08/2021 - US 1513 - Rowyn
	 15/08/2021 - Rowyn - Updated script

"""


def get_ConditionScale():
	conditionScale = dict()
	conditionScale["ConditionScaleQty"] = int()
	conditionScale["Rate"]				= float()
	return conditionScale

def get_ConditionItems(condType, uom, currency, rate):
	conditionItems = dict()
	conditionItems["ConditionType"] 		= str(condType)
	conditionItems["ScaleType"] 			= ""
	conditionItems["ScaleIndicator"] 		= ""
	conditionItems["ScaleConditionUnit"] 	= ""
	conditionItems["CalculationType"] 		= "C"
	conditionItems["Rate"] 					= float(rate)
	conditionItems["RateUnit"] 				= str(currency)
	conditionItems["ConditionPricingUnit"] 	= 1 # empty for % else int(1)
	conditionItems["ConditionUnit"] 		= str(uom)
	conditionItems["ConditionScale"] 		= get_ConditionScale()
	return conditionItems

def get_conditionHeader(startDate, endDate):
	conditionHeader = dict()
	conditionHeader["ValidFrom"] 		= str(startDate)
	conditionHeader["ValidTo"] 			= str(endDate)
	conditionHeader["ConditionItems"] 	= get_ConditionItems(condType, uom, currency, rate)
	return conditionHeader

def get_price_content(tableNum, condType, variableKey, sOrg, distCh, divOrg):
	price_content = dict()
	price_content["ConditionTable"]  = str(tableNum)[1:]
	price_content["Application"]	 = "V"
	price_content["Usage"]		   = "A"
	price_content["ConditionType"] 	 = str(condType)
	price_content["VariableKey"] 	 = str(variableKey)
	price_content["SalesOrg"] 		 = str(sOrg)
	price_content["DistChan"] 		 = str(distCh)
	price_content["Division"] 		 = str(divOrg)
	price_content["ConditionHeader"] = get_conditionHeader(startDate, endDate)
	return price_content

def price_cond(conditionKey):
	priceCond = dict()
	priceCond["Serial"]		  = ""  # no indication
	priceCond["ConditionKey"]	= conditionKey
	return priceCond

# Harded coded for testing purposes, as the info is not on CPQ yet
#/!\# to change - Start #/!\#
sOrg		= "1000"
distCh		= "10"
divOrg		= "PG"
#/!\# to change - END   #/!\#


try:
	from Newtonsoft.Json import JsonConvert
	from Newtonsoft.Json.Linq import JObject
	from datetime import datetime

	# Define attributes to retrieve value from configuration
	# store value in variables
	mgType			= Product.Attributes.GetByName("MG_TYPE").GetValue()

	#startDate 		= Product.Attributes.GetByName("MG_VALIDITY_START_DATE").GetValue()
	#endDate		= Product.Attributes.GetByName("MG_VALIDITY_END_DATE").GetValue()

	startDate	   = datetime.strptime(Product.Attr('MG_VALIDITY_START_DATE').GetValue(), '%m/%d/%Y').ToString().split(' ')[0].replace('-', '')
	endDate		 = datetime.strptime(Product.Attr('MG_VALIDITY_END_DATE').GetValue(), '%m/%d/%Y').ToString().split(' ')[0].replace('-', '')

	currency		= Product.Attributes.GetByName("MG_CURRENCY_AUTO").GetValue()
	uom			 = Product.Attributes.GetByName('MG_UOM').SelectedValue.ValueCode

	soldTo 			= Product.Attributes.GetByName("MG_SOLD_TO").GetValue()
	shipTo 			= Product.Attributes.GetByName("MG_SHIP_TO").GetValue()
	endCust 		= Product.Attributes.GetByName("MG_END_CUSTOMER").GetValue()
	endUseObject 	= Product.Attributes.GetByName("MG_END_USE_OBJECT").GetValue()

	# check if attribute is empty, else assign 'X'
	sold2  			= "" if (soldTo is None or soldTo == "") else "X"
	shipTo2 		= "" if (shipTo is None or shipTo == "") else "X"
	endCust2 		= "" if (endCust is None or endCust == "") else "X"
	endUseObject2 	= "" if (endUseObject is None or endUseObject == "") else "X"

	# get access sequence from BO_PRICING_CONDITIONS, based on configuration
	sqlResult 	= SqlHelper.GetSingle("""SELECT COND_TYPE, PRIORITY, TABLE_NUM
									FROM BO_PRICING_CONDITIONS WHERE
									SOLD_TO = '%s' AND
									SHIP_TO = '%s' AND
									END_USER = '%s' AND
									END_USE_OBJECT = '%s' """ %(sold2, shipTo2, endCust2, endUseObject2))

	# Store condition type, priority, table number in variables
	condType 			= sqlResult.COND_TYPE
	priority 			= sqlResult.PRIORITY
	tableNum 			= sqlResult.TABLE_NUM

	# Read the value of hidden attribute "Sold-To"
	allSoldTo 			= Product.Attributes.GetByName("MG_SOLD_TO_VALUECODES").GetValue()
	# Break down the string of value into a list
	allSoldToList	   = allSoldTo[1:-1].split(", ") if allSoldTo != "['']" else list()

	# Read the value of hidden attribute "Ship-To"
	allShipTo 			= Product.Attributes.GetByName("MG_SHIP_TO_VALUECODES").GetValue()
	# Break down the string of value into a list
	allShipToList 		= allShipTo[1:-1].split(", ") if allShipTo != "['']" else list()

	# define Pricing container
	pricingContainer	= Product.GetContainerByName('BO_PRICING_CONT')
	pricingMatCodeList 	= list()
	pricingMatPrice	 = dict()

	# Loop in pricing container to get values
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

	# Define condition key list which will contain all pricing conditions
	conditionKey = list()

	# Build the Pricing structure
	for matCode in pricingMatCodeList:
		# get the price for material
		rate = pricingMatPrice[matCode]
		# check if Sold-To list is not empty
		if allSoldToList:
			for soldTos in allSoldToList:
				# build variable key
				variableKey = sOrg + distCh + divOrg + soldTos[3:-1] + matCode
				# add the pricing content to 'condition key'
				conditionKey.append(get_price_content(tableNum, condType, variableKey, sOrg, distCh, divOrg))
		# check if Ship-To list is not empty
		if allShipToList:
			for shipTos in allShipToList:
				# build variable key
				variableKey = sOrg + distCh + divOrg + shipTos[3:-1] + matCode
				# add the pricing content to 'condition key'
				conditionKey.append(get_price_content(tableNum, condType, variableKey, sOrg, distCh, divOrg))


	# build pricing data
	pricingData	 = price_cond(conditionKey)
	# serialize the data
	priceDataJson   = RestClient.SerializeToJson(pricingData)
	# make it xml
	#priceDataXml	= str(JsonConvert.DeserializeXNode(priceDataJson, "root"))


	# assign flag to hidden attr BO_PRICE_ECC_FLAG
	#Product.Attr('BO_PRICE_ECC_FLAG').AssignValue("Pending")

	# # Check the data
	# myVal = Product.Attr('BO_PRICE_ECC').GetValue()

	# Compress the xml data
	import zlib
	compressedPayload = zlib.compress(priceDataJson)

	# assign the data to hidden attribute - BO_PRICE_ECC
	Product.Attr('BO_PRICE_ECC').AssignValue(compressedPayload)
	# qt = Quote.QuoteTables['BO_QTB_PRICING_COND']
	# a = qt.AddNewRow()

	# try:
	#	 qt.Rows[0].SetColumnValue('XML', compressedPayload)
	#	 qt.Save()
	# except Exception as e:
	#	 Trace.Write("Error -> " +str(e))

except Exception as e:
	Trace.Write("Error in script BO_PricingConditions_OnAddUpdate--> "+str(e))
