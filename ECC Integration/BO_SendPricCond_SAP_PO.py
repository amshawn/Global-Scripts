
"""
US 1513
Description: Loops in the quote table Pricing Conditions
For each row where status is 'Pending', execute the function "sendPayloadTo_SAP_PO"
Note that the data in quote table pricing - column 'XML' should be decompressed

Input:

Output:


Dev: 04/08/2021 - US 1513 - Rowyn
	 15/08/2021 - Rowyn - Updated script

"""
#get endpoints
def getEndpoints(domain, process):
	table = SqlHelper.GetFirst("""
	SELECT *
	FROM MG_ENDPOINT
	WHERE ENVIRONMENT = '{domain}'
	AND PROCESS = '{process}'
	""".format(domain = domain,
			   process = process))
	return table

# function to call SAP PO adn sent pricing conditions
def sendPayloadTo_SAP_PO(conditionsPayload, process):
	from System import Uri
	import System.Text
	#from System.Net import WebClient
	from System.Net import HttpWebRequest
	from System.Xml.Linq import XDocument
	from System import Convert


	# prepare the payload
	# using dummy data for 'root'
	# same data was tested on SOAP UI by Integratin team and action was successful
	env 	= """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">"""
	header 	= """<soapenv:Header/>"""
	body 	= """<soapenv:Body>"""
	root	= conditionsPayload
	body_e	= """</soapenv:Body>"""
	env_e	= """</soapenv:Envelope>"""

	# Payload
	pld = "<?xml version='1.0' encoding='UTF-8'?>" + \
	env + \
	header + \
	body + \
	root + \
	body_e + \
	env_e


	parse_pld 	= XDocument.Parse(pld)
	payload		= str(parse_pld)

	#get endpoints
	endpoint = getEndpoints(TagParserQuote.ParseString("<* DOMAIN *>"), process)
	# Encrypt user/pass
	encrypted_userpass 	= RestClient.GetBasicAuthenticationHeader(endpoint.CLIENT_ID, endpoint.CLIENT_SECRET)
	# create the request to send
	webRequest = HttpWebRequest.Create(Uri(endpoint.URL))
	# Modify the request values
	webRequest.ContentType 	= "text/xml;charset=\"utf-8\""
	webRequest.Accept 		= "text/xml"
	# Method
	webRequest.Method = "POST"
	# Headers
	webRequest.Headers.Add('SOAPAction', endpoint.SOAPACTION)
	webRequest.Headers.Add('Authorization', encrypted_userpass)
	# Encode the payload
	encoding 		= System.Text.UTF8Encoding()
	encodedPayload 	= encoding.GetBytes(payload)
	# check the response
	#write the bytes above to the request
	rqt = webRequest.GetRequestStream()
	rqt.Write(encodedPayload,0,encodedPayload.Length)

	hasSentToPo = False
	#get the response here
	try:
		rsp = webRequest.GetResponse()
		hasSentToPo = True
	except System.Net.WebException as we:
		Trace.Write("Error! --> "+str(we))

	return hasSentToPo

# Send conditions pending to SAP PO
try:
	import zlib

	# define quote table for pricing conditions
	pricQuoteTable 	= Quote.QuoteTables["BO_QTB_PRICING_COND"]
	rebateQt 		= Quote.QuoteTables["BO_REBATES"]
	# Loop in Pricing Conditions Quote Table
	for row in pricQuoteTable.Rows:
		if row["Status"] != "Sent to PO":
			# Get the payload
			valXML  = row.GetColumnValue('XML')
			# deccompress the payload
			payload = zlib.decompress(valXML)
						#defaulted to message not sent
			hasSentToPo = False
			# trigger function to send payload to SAP PO
			if row.GetColumnValue('CONDITION')[0] == "Z":
				hasSentToPo = sendPayloadTo_SAP_PO(payload, "REBATE")
#update records in rebate table-------------------------------------------------
				for line in rebateQt.Rows:
					if row.GetColumnValue('CONDITION') == line["REBATE_TYPE"]:
						#was rebate successfully sent to PO
						if hasSentToPo: #yes!
							line["SAP_SENDING"] = "Sent to PO"
							line["SAP_SENT_ON"] = Quote.DateCreated.Now
						else: #no!
							line["SAP_SENDING"] = "Sent to PO"
			else:
				hasSentToPo = sendPayloadTo_SAP_PO(payload, "PRICING")
			# set the column status to 'Sent'
			if hasSentToPo:
				row.SetColumnValue("SEND_COUNT", row["SEND_COUNT"] + 1)
				row.SetColumnValue("DATE_SENT", Quote.DateCreated.Now)
				row.SetColumnValue("Status", "Sent to PO")
			else:
				row.SetColumnValue("Status", "Failed")
				Quote.Messages.Add('Price conditions could not be sent.')
			Log.Write(payload)
except Exception as e:
	Trace.Write("Error in script BO_SendPricCond_SAP_PO --> "+str(e))
