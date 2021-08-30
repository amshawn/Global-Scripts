for attr in sender.AttributeValues:
	if attr.DisplayValue == sender.Content:
		if attr.ValueCode == "1":#1 sold-to
			#hide rebate recipient = sold-to
			Quote.CustomFields.Allow("BO_CF_REBATE_RECIPIENT")
		elif attr.ValueCode == "ALL": #all sold-to
			#show rebate recipient = sold-to
			Quote.CustomFields.Disallow("BO_CF_REBATE_RECIPIENT")
		break
