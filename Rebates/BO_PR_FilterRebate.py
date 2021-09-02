"""
Description:
			#1987 - Set up internal control for Rebate type selection inside Appendix #3s
					Control - Cannot select a rebate type which has already been selected within the same Appendix #3

Input:
		Quote
Output:
		SQL Pre-selection filter for attribute BO_REBATE_TYPE

Dev: Shawn Yong, 31/08/2021

"""
#get rebates quote table
quoteTbl = Quote.QuoteTables['BO_REBATES']
#Initiate rebate types list
mylist = list()
#get rebate type already used
for row in quoteTbl.Rows:
	if not row["REBATE_TYPE"]:
		mylist.append(row["REBATE_TYPE"])

if len(mylist) > 0:
	#Get all active rebate types that havent been selected yet
	Result = "ACTIVE ='X' AND TYPE NOT IN({list})".format(list= str(mylist)[1:-1])
else: #Get all active rebate types
	Result = "ACTIVE ='X'"
