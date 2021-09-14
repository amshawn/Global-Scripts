
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

#build variable key
def getVarKey(variableKey,
				erpTable,
				soldTos, 	#Sold-to party
				shipTos,	#Ship-to party
				sOrg,		#sales organisation
				distCh, 	#Distribution Channel
				matCode,	#Pricing Ref. Matl
				endCust,	#End user
				endObj		#end use object
				):
	#buid variable key
	for line in erpTable:
		if line.SAP_FIELD == "VKORG": #sales organisation
			variableKey = variableKey + sOrg
		elif line.SAP_FIELD == "VTWEG": #Distribution Channel
			variableKey = variableKey + distCh
		elif line.SAP_FIELD == "SPART": #Division
			variableKey = variableKey + divOrg
		elif line.SAP_FIELD == "KUNNR": #Sold-to party
			variableKey = variableKey + soldTos.zfill(line.LENGTH)
		elif line.SAP_FIELD == "PMATN": #Pricing Ref. Matl
			variableKey = variableKey + matCode.ljust(line.LENGTH)
		elif line.SAP_FIELD == "KUNWE": #Ship-to party
			variableKey = variableKey + shipTos.zfill(line.LENGTH)
		elif line.SAP_FIELD == "ZZCUSZE": #End user
			variableKey = variableKey + endCust.zfill(line.LENGTH)
		elif line.SAP_FIELD == "ZZVCENDUSEOBJCT": #end use object
			variableKey = variableKey + soldTos.zfill(line.LENGTH)
		elif line.SAP_FIELD == "ZZHIEZU01": #CustomerHierarchy01
			variableKey = variableKey + "".zfill(line.LENGTH)
	return variableKey

#get ECC fields for table
def getErpTable(tableNum):
	table = SqlHelper.GetList("""
	SELECT *
	FROM MG_TABLE_ECC
	WHERE TABLE_NAME = '{tableName}'
	""".format(tableName=tableNum))
	return table

# Harded coded for testing purposes, as the info is not on CPQ yet
#/!\# to change - Start #/!\#
sOrg		= "1000"
distCh		= "10"
divOrg		= "PG"
#/!\# to change - END   #/!\#

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
endCustCde		= Product.Attributes.GetByName("MG_END_CUSTOMER").SelectedValue.ValueCode[4:] if Product.Attributes.GetByName("MG_END_CUSTOMER").SelectedValue else ""
endUseObject 	= Product.Attributes.GetByName("MG_END_USE_OBJECT").GetValue()
endObjCde		= Product.Attributes.GetByName("MG_END_USE_OBJECT").SelectedValue.ValueCode if Product.Attributes.GetByName("MG_END_USE_OBJECT").SelectedValue else ""

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

#get fields to build the access sequence
erpTable = getErpTable(tableNum)

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
	# initialize variable key
	varKey = ""
	# get the price for material
	rate = pricingMatPrice[matCode]
	# check if Sold-To list is not empty
	if allSoldToList:
		for soldTos in allSoldToList:
			# check if Ship-To list is not empty
			if allShipToList:
				for shipTos in allShipToList:
					# build variable key
					varKey = getVarKey(varKey,
										erpTable,
										soldTos[4:-1], 	#Sold-to party
										shipTos[4:-1],	#Ship-to party
										sOrg,			#sales organisation
										distCh, 		#Distribution Channel
										matCode,		#Pricing Ref. Matl
										endCustCde,		#End user
										endObjCde		#end use object
										)
					# add the pricing content to 'condition key'
					conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))
					varKey = ""
			else:
				varKey = getVarKey(varKey,
									erpTable,
									soldTos[4:-1], 	#Sold-to party
									"",				#Ship-to party
									sOrg,			#sales organisation
									distCh, 		#Distribution Channel
									matCode,		#Pricing Ref. Matl
									endCustCde,		#End user
									endObjCde		#end use object
									)
				conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))
				varKey = ""		# check if Ship-To list is not empty
	else:
		varKey = getVarKey(varKey,
							erpTable,
							"",				#Sold-to party
							"",				#Ship-to party
							sOrg,			#sales organisation
							distCh, 		#Distribution Channel
							matCode,		#Pricing Ref. Matl
							endCustCde,		#End user
							endObjCde		#end use object
							)
		conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))
		varKey = ""

# build pricing data
pricingData	 = price_cond(conditionKey)
# serialize the data
priceDataJson   = RestClient.SerializeToJson(pricingData)
# Compress the xml data
import zlib
compressedPayload = zlib.compress(priceDataJson)
# assign the data to hidden attribute - BO_PRICE_ECC
Product.Attr('BO_PRICE_ECC').AssignValue(compressedPayload)
