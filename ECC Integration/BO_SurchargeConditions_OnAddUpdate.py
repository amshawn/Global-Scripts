
"""
US 1513
Description: Creates the pricing conditions for SURCHARGE when product is added/updated to quote
Surcharge conditions are created based on values in the pricing container (grammage) and surcharge container if values were modified
There is a hidden attribute that checks if surcharge was changed
The data is stored in hidden attribute on product - BO_SURCHARGE_ECC
Note that the data is compressed using zlib and needs to be decompressed for readability

Input:

Output:

Dev: 04/08/2021 - US 1513 - Rowyn
	 15/08/2021 - Rowyn - Updated script

"""

def get_ConditionScale(scale):
	conditionScale = dict()
	conditionScale["ConditionScaleQty"] = scale["ScaleQty"]
	conditionScale["Rate"]				= scale["Rate"]
	return conditionScale

def get_emptyConditionScale():
	conditionScale = dict()
	conditionScale["ConditionScaleQty"] = ""
	conditionScale["Rate"]				= ""
	return conditionScale

def get_ConditionItems(condType, uom, currency, rate):
	conditionItems = dict()
	conditionItems["ConditionType"] 		= str(condType)
	conditionItems["CalculationType"] 		= "C"
	conditionItems["Rate"] 					= rate
	conditionItems["RateUnit"] 				= str(currency)
	conditionItems["ConditionPricingUnit"] 	= "1"
	conditionItems["ConditionUnit"] 		= str(uom)

	if len(surcharge["Scale"]) > 0:
		conditionItems["ScaleType"] 		= "A"
		conditionItems["ScaleIndicator"] 	= "C"
		conditionItems["ScaleConditionUnit"]= str(uom)
		condScale = list()
		for row in surcharge["Scale"]:
			condScale.append(get_ConditionScale(row))
		conditionItems["ConditionScale"] 	= condScale
	else:
		conditionItems["ScaleType"] 		= ""
		conditionItems["ScaleIndicator"] 	= ""
		conditionItems["ScaleConditionUnit"]= ""
		conditionItems["ConditionScale"] 	= get_emptyConditionScale()
	return conditionItems

def get_conditionHeader(startDate, endDate):
	conditionHeader = dict()
	conditionHeader["ValidFrom"] 		= str(startDate)
	conditionHeader["ValidTo"] 			= str(endDate)
	conditionHeader["ConditionItems"] 	= get_ConditionItems(condType, uom, currency, surcharge["Rate"])
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

# get access sequence from BO_SURCHARGE_CONDITIONS, based on configuration
def get_Surcharge_Conditions(flags, condType):
	sqlResult   = SqlHelper.GetFirst("""SELECT COND_TYPE, ACCESS, TABLE_NUM
									FROM BO_SURCHARGE_CONDITIONS WHERE
									SOLD_TO = '%s' AND
									SHIP_TO = '%s' AND
									END_USER = '%s' AND
									END_USE_OBJECT = '%s' AND
									IS_MAT = '%s' AND
									COND_TYPE = '%s'
									ORDER BY ACCESS ASC """ %(flags["SOLDTO"], flags["SHIPTO"], flags["ENDUSER"], flags["ENDOBJ"], flags["MAT"], condType))

	# Store condition type, priority, table number in variables
	condType	= sqlResult.COND_TYPE if sqlResult else ""
	priority	= sqlResult.ACCESS if sqlResult else ""
	tableNum	= sqlResult.TABLE_NUM if sqlResult else ""
	return condType, priority, tableNum

# build amount and scale_min list
def get_PriceRateList(scale_min, rate):
	surchargeMatCodeList = list()
	surchargeMatCodeList.append(scale_min)
	surchargeMatCodeList.append(rate)
	return surchargeMatCodeList


def price_cond(conditionKey):
	priceCond = dict()
	priceCond["Serial"]		  = ""  # no indication
	priceCond["ConditionKey"]	= conditionKey
	return priceCond

#get ECC fields for table
def getErpTable(tableNum):
	table = SqlHelper.GetList("""
	SELECT *
	FROM MG_TABLE_ECC
	WHERE TABLE_NAME = '{tableName}'
	""".format(tableName=tableNum))
	return table

#get multipliers
def getMultipliers(fields):
	table = SqlHelper.GetList("""
	SELECT *, 'False' as IS_USED
	FROM MG_MULTIPLIERS_ECC
	WHERE SAP_FIELD IN {}
	""".format(fields))
	return table

#build variable key
def getVarKey(
				erpTable,
				soldTos, 		#Sold-to party
				shipTos,		#Ship-to party
				sOrg,			#sales organisation
				distCh, 		#Distribution Channel
				matCode,		#Pricing Ref. Matl
				endCust,		#End user
				endObj,			#end use object
				ctry,			#destination country
				currency,		#Document Currency
				cat,			#Brand Category
				region,			#Region
				envLbl			#Environmental label
				):
	#build variable key
	variableKey = ""

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
			variableKey = variableKey + endObj.ljust(line.LENGTH)
		elif line.SAP_FIELD == "ZZLOADLVL": #end use object
			variableKey = variableKey + " ".ljust(line.LENGTH)
		elif line.SAP_FIELD == "AUART": #Order Type
			variableKey = variableKey + " ".ljust(line.LENGTH)
		elif line.SAP_FIELD == "LAND1": #Destination Country
			variableKey = variableKey + ctry.ljust(line.LENGTH)
		elif line.SAP_FIELD == "WAERK": #Document Currency
			variableKey = variableKey + currency
		elif line.SAP_FIELD == "ZZBRAND_CATEGORY": #Brand Category
			variableKey = variableKey + cat.ljust(line.LENGTH)
		elif line.SAP_FIELD == "ZZCUSZS": #Sales company
			variableKey = variableKey + soldTos.zfill(line.LENGTH)
		elif line.SAP_FIELD == "ZZHIEZU01": #CustomerHierarchy01
			variableKey = variableKey + " ".zfill(line.LENGTH)
		elif line.SAP_FIELD == "ZZLABEL_ENVIR": #Environmental label
			variableKey = variableKey + envLbl.ljust(line.LENGTH)
	return variableKey

def addMultiplier(variableKey, erpTable, record):#Multipliers
	for line in erpTable:
		if record.SAP_FIELD.strip() == line.SAP_FIELD.strip():
			variableKey = variableKey + record.VALUE.ljust(line.LENGTH)
	return variableKey

def getMultiplier(field):
	table = SqlHelper.GetList("""
	SELECT *
	FROM MG_MULTIPLIERS_ECC
	WHERE SAP_FIELD = '{}'
	""".format(field))
	return table

#create variant keys for multipliers
def getMultiplierKeys(varKey, erpTable, count, conditionKey, tableNum, condType, sOrg, distCh, divOrg):
	multiplierKeys = []

	for line in reversed(erpTable):
		multipliers = getMultiplier(line.SAP_FIELD.strip())

		if len(multiplierKeys) <= 0:
			for multiplier in multipliers:
				multiplierKeys.append(multiplier.VALUE.ljust(line.LENGTH))
		else:
			temp = []
			for myKey in multiplierKeys:
				for multiplier in multipliers:
					temp.append(multiplier.VALUE.ljust(line.LENGTH) + myKey)

			if multipliers:
				multiplierKeys = temp

	for myKey in multiplierKeys:
		 	myKey = varKey + myKey
			conditionKey.append(get_price_content(tableNum, condType, myKey, sOrg, distCh, divOrg))

	is_added = False
	if not multiplierKeys:
		if count == len(varKey):
			for key in conditionKey:
				if key["VariableKey"] == varKey and key["ConditionType"] == condType:
					is_added = True
					break
				else:
					is_added = False
			if not is_added:
				conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))

	return conditionKey


# Harded coded for testing purposes, as the info is not on CPQ yet
#/!\# to change - Start #/!\#
sOrg		= "1000"
distCh		= "10"
divOrg		= "PG"
#/!\# to change - END   #/!\#


from Newtonsoft.Json import JsonConvert
from Newtonsoft.Json.Linq import JObject
from datetime import datetime

# check if surcharges have been changed
if Product.Attributes.GetByName("BO_HIDDEN_ATTRIBUTE_SURCHARGE").GetValue() == "TRUE":

	# Define attributes to retrieve value from configuration
	# store value in variables
	mgType			= Product.Attributes.GetByName("MG_TYPE").GetValue()

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
	#get destination Country
	ctry 			= Product.Attributes.GetByName('BO_COUNTRY_PROFITABILITY_CALC').SelectedValue.ValueCode if Product.Attributes.GetByName('BO_COUNTRY_PROFITABILITY_CALC').SelectedValue else " "
	#get Region
	region 			= Quote.SelectedMarket.MarketCode.split("_")[0]
	#get Category
	cat				= Product.PartNumber
	flags = dict()
	# check if attribute is empty, else assign 'X'
	flags["SOLDTO"]  			= "" if (soldTo is None or soldTo == "") else "X"#sold2
	flags["SHIPTO"] 			= "" if (shipTo is None or shipTo == "") else "X"#shipTo2
	flags["ENDUSER"] 			= "" if (endCust is None or endCust == "") else "X"#endCust2
	flags["ENDOBJ"] 			= "" if (endUseObject is None or endUseObject == "") else "X"#endUseObject2

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
				invPrice = column.Value
			if column.Name == "MATERIAL_CODE":
				# add each 'Material Code' in a list
				pricingMatCodeList.append(column.Value)
				# build a dictionary of 'Material Code' : 'Invoice Price'
				pricingMatPrice[column.Value] = invPrice

	#is there any material? Yes! Set flag to X
	flags["MAT"] 	= "X" if pricingMatCodeList else ""
	# define surcharge container
	surchargeContainer		= Product.GetContainerByName('BO_SURCHARGE_CONT')
	surchargePriceRate 		= list()
	scaleList				= list()
	surType					= ""
	count					= 1
	tableLength				= surchargeContainer.Rows.Count
	# Loop in surcharge container to get values
	for row in surchargeContainer.Rows:
		if row["IS_UPDATED"] == "True":
# Build surchargePriceRate dictionary of values {surchargeCode : [scale_min, rate]}
			scale = dict()
			if row["BO_SCALE_MIN"] != "":
				scale["ScaleQty"] 	= float(row["BO_SCALE_MIN"])
				scaleMax = round(float(row["BO_SCALE_MAX"]))
				scale["Rate"]		= float(row["BO_AMOUNT"])
				scaleList.append(scale)

			if count == tableLength: #last row
				isLastRow = True
			elif row["BO_CODE"] != surchargeContainer.Rows[count]["BO_CODE"]: #new surcharge
				isLastRow = True
			else:
				if scale:
					isLastRow = False
				else:
					isLastRow = True

			if isLastRow:
				surcharge = dict()
				surcharge["SurchargeCode"] = row["BO_CODE"]
				surcharge["EnvironmentalLabel"] = row["ENV_LBL"]

				if len(scale) > 0:
					#add last line for 0
					scale = dict()
					scale["ScaleQty"] 	= scaleMax
					scale["Rate"]		= 0.00
					scaleList.append(scale)
					scaleList = sorted(scaleList, reverse=True)
					surcharge["Scale"] = scaleList
					surcharge["Rate"] = scaleList[0]["Rate"]
				else:
					surcharge["Scale"] = ""
					surcharge["Rate"] = row["BO_AMOUNT"]

				surchargePriceRate.append(surcharge)
				scaleList = list()
		count += 1

	# Define condition key list
	conditionKey = list()
	# Build the Surcharge structure
	is_added = False
#no materials/grammages in price sheets
	if not pricingMatCodeList:
		pricingMatCodeList.append(None)
#for each material generate a variable key
	for matCode in pricingMatCodeList:
		# initialize variable key
		varKey = ""
		# check if there are surcharges
		if surchargePriceRate:
			for surcharge in surchargePriceRate:
				#get Environmental label
				envLbl = surcharge["EnvironmentalLabel"]
				# get values // sql select -> to optimise
				# if no corresponding condition is met in custom table, it will skip
				condType, priority, tableNum = get_Surcharge_Conditions(flags, surcharge["SurchargeCode"])

				if tableNum == "":
					Trace.Write("[TRACE]"+surcharge["SurchargeCode"])
					continue
#BUILDING VARIABLE KEY----------------------------------------------------------
				#get fields to build the access sequence
				erpTable = getErpTable(tableNum)
				#get length of variable key
				count = 0
				for row in erpTable:
					count += row.LENGTH

				# check if Sold-To list is not empty
				if allSoldToList:
					for soldTos in allSoldToList:
						# check if Ship-To list is not empty
						if allShipToList:
							for shipTos in allShipToList:
								varKey = getVarKey(
													erpTable,
													soldTos[4:-1], 	#Sold-to party
													shipTos[4:-1],	#Ship-to party
													sOrg,			#sales organisation
													distCh, 		#Distribution Channel
													matCode,		#Pricing Ref. Matl
													endCustCde,		#End user
													endObjCde,		#end use object
													ctry,			#destination country
													currency,		#Document Currency
													cat,			#Brand Category
													region,			#Region
													envLbl			#Environmental label
													)
								conditionKey = getMultiplierKeys(varKey, erpTable, count, conditionKey, tableNum, condType, sOrg, distCh, divOrg)
						else:
							varKey = getVarKey(
												erpTable,
												soldTos[4:-1], 	#Sold-to party
												"",				#Ship-to party
												sOrg,			#sales organisation
												distCh, 		#Distribution Channel
												matCode,		#Pricing Ref. Matl
												endCustCde,		#End user
												endObjCde,		#end use object
												ctry,			#destination country
												currency,		#Document Currency
												cat,			#Brand Category
												region,			#Region
												envLbl			#Environmental label
												)

							conditionKey = getMultiplierKeys(varKey, erpTable, count, conditionKey, tableNum, condType, sOrg, distCh, divOrg)

				else:
					varKey = getVarKey(
										erpTable,
										"",				#Sold-to party
										"",				#Ship-to party
										sOrg,			#sales organisation
										distCh, 		#Distribution Channel
										matCode,		#Pricing Ref. Matl
										endCustCde,		#End user
										endObjCde,		#end use object
										ctry,			#destination country
										currency,		#Document Currency
										cat,			#Brand Category
										region,			#Region
										envLbl			#Environmental label
										)

					conditionKey = getMultiplierKeys(varKey, erpTable, count, conditionKey, tableNum, condType, sOrg, distCh, divOrg)
	# build pricing data
	pricingData	 = price_cond(conditionKey)
	# serialize the data
	priceDataJson   = RestClient.SerializeToJson(pricingData)

	# Compress the xml data
	import zlib
	compressedPayload = zlib.compress(priceDataJson)

	# assign the data to hidden attribute - BO_SURCHARGE_ECC
	Product.Attr('BO_SURCHARGE_ECC').AssignValue(compressedPayload)
