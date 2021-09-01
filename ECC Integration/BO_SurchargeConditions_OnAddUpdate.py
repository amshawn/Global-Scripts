
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

def get_ConditionScale(scaleMin):
	conditionScale = dict()
	if scaleMin != "":
		conditionScale["ConditionScaleQty"] = scaleMin
		conditionScale["Rate"]				= rate
	else:
		conditionScale["ConditionScaleQty"] = ""
		conditionScale["Rate"]				= ""
	return conditionScale

def get_ConditionItems(condType, uom, currency, rate):
	conditionItems = dict()
	conditionItems["ConditionType"] 		= str(condType)
	conditionItems["ScaleType"] 			= ""
	if scaleMin != "":
		conditionItems["ScaleIndicator"] 	= "C"
	else:
		conditionItems["ScaleIndicator"] 	= ""
	conditionItems["ScaleConditionUnit"] 	= str(uom)
	conditionItems["CalculationType"] 		= "C"
	conditionItems["Rate"] 					= str(rate)
	conditionItems["RateUnit"] 				= str(currency)
	conditionItems["ConditionPricingUnit"] 	= "1"
	conditionItems["ConditionUnit"] 		= str(uom)
	conditionItems["ConditionScale"] 		= get_ConditionScale(scaleMin)
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

# get access sequence from BO_SURCHARGE_CONDITIONS, based on configuration
def get_Surcharge_Conditions(sold2, shipTo2, endCust2, endUseObject2, condType):
	sqlResult   = SqlHelper.GetFirst("""SELECT COND_TYPE, ACCESS, TABLE_NUM
									FROM BO_SURCHARGE_CONDITIONS WHERE
									SOLD_TO = '%s' AND
									SHIP_TO = '%s' AND
									END_USER = '%s' AND
									END_USE_OBJECT = '%s' AND
									COND_TYPE = '%s'
									ORDER BY ACCESS ASC """ %(sold2, shipTo2, endCust2, endUseObject2, condType))

	# Store condition type, priority, table number in variables
	condType	= sqlResult.COND_TYPE
	priority	= sqlResult.ACCESS
	tableNum	= sqlResult.TABLE_NUM
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
	WHERE TABLE = '{table}'
	""".format(table=tableNum))
	return table

#get ECC fields for table
def getErpTable(tableNum):
	table = SqlHelper.GetList("""
	SELECT *
	FROM MG_TABLE_ECC
	WHERE TABLE = '{table}'
	""".format(table=tableNum))
	return table

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
			variableKey = variableKey + sOrg[:line.LENGTH-1]
		elif line.SAP_FIELD == "VTWEG": #Distribution Channel
			variableKey = variableKey + distCh[:line.LENGTH-1]
		elif line.SAP_FIELD == "SPART": #Division
			variableKey = variableKey + divOrg[:line.LENGTH-1]
		elif line.SAP_FIELD == "KUNNR": #Sold-to party
			variableKey = variableKey + soldTos
		elif line.SAP_FIELD == "PMATN": #Pricing Ref. Matl
			variableKey = variableKey + matCode[:line.LENGTH-1]
		elif line.SAP_FIELD == "KUNWE": #Ship-to party
			variableKey = variableKey + shipTos
		elif line.SAP_FIELD == "ZZCUSZE": #End user
			variableKey = variableKey + endCust
		elif line.SAP_FIELD == "ZZVCENDUSEOBJCT": #end use object
			variableKey = variableKey + endObj[:line.LENGTH-1]
		elif line.SAP_FIELD == "AUART": #Order Type
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "LAND1": #Destination Country
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "WAERK": #Document Currency
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZBRAND_CATEGORY": #Brand Category
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZCONVERTER": #Converter
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZCRDIALVL": #Core Diameter Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZCUSZS": #Sales company
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZHIEZU01": #CustomerHierarchy01
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZLABEL_ENVIR": #Label environment
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZLEADLVL": #Lead Time Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZLOADLVL": #Load Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZPLHGTLVL": #Pallet Height Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZREGION": #Region
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZRLDIALVL": #Reel Diameter Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZRLWIDLVL": #Reel Width Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZSHLENLVL": #Sheet Length Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZSHWIDLVL": #Sheet Width Level
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZVCPACKMTYP": #packing main type
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZVCPALLET_TYPE": #Pallet Type
			variableKey = variableKey + ""
		elif line.SAP_FIELD == "ZZVCSHREAMWRAP": #sheet ream wrapping
			variableKey = variableKey + ""
	return variableKey


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
		# check if attribute is empty, else assign 'X'
		sold2  			= "" if (soldTo is None or soldTo == "") else "X"
		shipTo2 		= "" if (shipTo is None or shipTo == "") else "X"
		endCust2 		= "" if (endCust is None or endCust == "") else "X"
		endUseObject2 	= "" if (endUseObject is None or endUseObject == "") else "X"

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

		# define surcharge container
		surchargeContainer		= Product.GetContainerByName('BO_SURCHARGE_CONT')
		surchargePriceRate 		= dict()
		surchargeList		   = list()

		# Loop in surcharge container to get values
		for row in surchargeContainer.Rows:
			for column in row.Columns:
				if column.Name == "BO_SCALE_MIN":
					# value  of Scale Min column
					scale_min = column.Value
				if column.Name == "BO_AMOUNT":
					# value  of Amount column
					rate = column.Value
				if column.Name == "BO_CODE":
					# value  of Code column
					surchargeCode = column.Value
					# Build Surcharge List
					surchargeList.append(surchargeCode)
					# Build surchargePriceRate dictionary of values {surchargeCode : [scale_min, rate]}
					surchargePriceRate[surchargeCode] = get_PriceRateList(scale_min, rate)

		# Define condition key list
		conditionKey = list()
		# initialize variable key
		varKey = ""
		# Build the Surcharge structure
		for matCode in pricingMatCodeList:
			# check if there are surcharges
			if surchargeList:
				for s in surchargeList:

					# get the amount for each surcharge
					scaleMin	= surchargePriceRate[s][0]
					# get the amount for each surcharge
					rate		= surchargePriceRate[s][1]

					try:
						# get values // sql select -> to optimise
						# if no corresponding condition is met in custom table, it will skip
						condType, priority, tableNum = get_Surcharge_Conditions(sold2, shipTo2, endCust2, endUseObject2, s)
#BUILDING VARIABLE KEY----------------------------------------------------------
						#get fields to build the access sequence
						erpTable = getErpTable(tableNum)

						# check if Sold-To list is not empty
						if allSoldToList:
							for soldTos in allSoldToList:
								# check if Ship-To list is not empty
								if allShipToList:
									for shipTos in allShipToList:
										varKey = getVarKey(varKey,
															erpTable,
															soldTos[4:], 	#Sold-to party
															shipTos[4:],	#Ship-to party
															sOrg,			#sales organisation
															distCh, 		#Distribution Channel
															matCode,		#Pricing Ref. Matl
															endCustCde,		#End user
															endObjCde		#end use object
															)
										conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))
								else:
									varKey = getVarKey(varKey,
														erpTable,
														soldTos[4:], 	#Sold-to party
														"",				#Ship-to party
														sOrg,			#sales organisation
														distCh, 		#Distribution Channel
														matCode,		#Pricing Ref. Matl
														endCust,		#End user
														endObjCde		#end use object
														)
									conditionKey.append(get_price_content(tableNum, condType, varKey, sOrg, distCh, divOrg))

					except Exception as eee:
						Trace.Write("Error in BO_SurchargeConditions_OnAddUpdate --> " +str(eee))
						Trace.Write("Surcharge code: " +str(s) + " error.")

					# # if not matching condType, break the loop
					# break

		# build pricing data
		pricingData	 = price_cond(conditionKey)
		# serialize the data
		priceDataJson   = RestClient.SerializeToJson(pricingData)

		# Compress the xml data
		import zlib
		compressedPayload = zlib.compress(priceDataJson)

		# assign the data to hidden attribute - BO_SURCHARGE_ECC
		Product.Attr('BO_SURCHARGE_ECC').AssignValue(compressedPayload)

except Exception as e:
	Trace.Write("Error in script BO_SurchargeConditions_OnAddUpdate--> "+str(e))
