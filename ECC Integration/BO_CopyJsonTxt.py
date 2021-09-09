#read all price sheets
for item in Quote.MainItems:
	#edit only price sheets
	if item.ParentRolledUpQuoteItem == "":
		#get product
		product = item.EditConfiguration()
		#copy json text for prices
		product.Attr("BO_PRICE_ECC_OLD").AssignValue(product.Attributes.GetByName("BO_PRICE_ECC").GetValue())
		#copy json text for surcharges
		product.Attr("BO_SURCHARGE_ECC_OLD").AssignValue(product.Attributes.GetByName("BO_SURCHARGE_ECC").GetValue())
		#copy json text for discounts
		product.Attr("BO_DISCOUNT_ECC_OLD").AssignValue(product.Attributes.GetByName("BO_DISCOUNT_ECC").GetValue())

		product.UpdateQuote()
