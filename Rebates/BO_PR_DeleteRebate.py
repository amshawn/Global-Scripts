#get rebate table
quoteTbl = Quote.QuoteTables['BO_REBATES']

for row in quoteTbl.Table.Rows:
	if row["IS_SELECTED"]:#selected row
		row["IS_DELETED"] = True #mark row as deleted
		row["IS_SELECTED"] = False #unselect row
		break
