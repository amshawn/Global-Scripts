"""
Description: Changes the visibility of rebate scale and rebate amount based on rebate types user choice.

Input:
Custom field 'Rebate Types'

Output:
Changes the behaviour and visibility of columns in the quote table 'Rebate Scale'
Changes the visibility of custom field 'Rebate Amount'

Dev: Rowyn Chengalanee, 08/06/2021, US 1537
	 Shawn Yong, 30/08/2021, US 2215

"""
#2215 Shawn---------------------------------------------------------------------
def getDescription(rebateType):
    table = SqlHelper.GetFirst("""
    SELECT *
    FROM BO_REBATE_TYPE
    WHERE KEY_COMBO = '{type}'
    """.format(type=rebateType))
    return table.DESCRIPTION if table else ""
#2215 End-----------------------------------------------------------------------
try:

    from BO_Rebates_Module import rebateScaleVisibility, rebateMsg

    # define quote table
    rebateScaleTable 	= Quote.QuoteTables['BO_REBATE_SCALE']
    rebateType 			= Quote.GetCustomField('BO_CF_REBATE_TYPE').Content
    # Display message
    rebateMsg(rebateType, Quote)
    # call function to control visibility behaviour
    rebateScaleVisibility(rebateScaleTable, rebateType, Quote)
#2215 Shawn---------------------------------------------------------------------
    Quote.CustomFields.AssignValue('BO_CF_NAME_OUTPUT', getDescription(rebateType))
#2215 End-----------------------------------------------------------------------
except Exception as e:
    Trace.Write('BO_CF_REBATE_TYPE ' + str(e))
