"""
Description: OnCellChanged Event scripts for BO_SURCHARGE_CONT container
			#1520 - Show warning message if surcharge amount is changed
			#2342 - Internal controls for overlapping scales
Input:
		EventArgs (For BO_SURCHARGE_CONT in => FOLDING BOXBOARD, FOOD SERVICE BOARD, WHITE KRAFTLINER, CIGARETTE BOARD)
		Product   (FOLDING BOXBOARD, FOOD SERVICE BOARD, WHITE KRAFTLINER, CIGARETTE BOARD)
Output:
		#1520 - Show warning message if surcharge amount is changed
		#2342 - Resets scale to previous value in case of overlapping

Dev:
		Rookayya Choolun, 14/07/2021 US 1520
		Brian Luk Tong, 14/07/2021 US 2342,1520
"""
try:
    if Param is not None:
        #R.CHOOLUN #1520-------------------------S T A R T------------------------------------------------------------
        EventArgs = Param.EventArgs
        Product = Param.Product
        if EventArgs.ChangedCell.ColumnName == "BO_AMOUNT":
            #Get container
            cont = EventArgs.Container
            #Reset as False until all surcharges are checked
            Product.SelectAttrValues('BO_HIDDEN_ATTRIBUTE_SURCHARGE', 'FALSE')
            Trace.Write(cont.Rows.Count)
            #Check all surcharges
            for row in cont.Rows:
                #Get hidden amount
            	hiddn_amount = float(row.Columns["BO_HIDDN_AMOUNT"].Value) if row.Columns["BO_HIDDN_AMOUNT"].Value != "" else float()
            	#Get amount
            	amount = float(row.Columns["BO_AMOUNT"].Value) if row.Columns["BO_AMOUNT"].Value != "" else float()
    			#Check if surcharge is different from default
				#If different set BO_HIDDEN_ATTRIBUTE_SURCHARGE --> True. To show warning message
                if hiddn_amount != amount:
                    Product.SelectAttrValues('BO_HIDDEN_ATTRIBUTE_SURCHARGE', 'TRUE')
        #R.CHOOLUN #1520-------------------------E   N   D------------------------------------------------------------
        #BRIAN #2342-------------------------S T A R T------------------------------------------------------------
        elif EventArgs.ChangedCell.ColumnName == "BO_SCALE_MIN" or EventArgs.ChangedCell.ColumnName == "BO_SCALE_MAX":
            #Get new value
            NewValue = float(EventArgs.ChangedCell.NewValue) if EventArgs.ChangedCell.NewValue != "" else float()
            #Get container
            cont = EventArgs.Container
            #Get rowindex
            rowindex = EventArgs.ChangedCell.RowIndex
            #Internal contol - Check if value is not negative
            if NewValue >= 0.00:
                #Controls when Scale Min is being changed by the user
                if EventArgs.ChangedCell.ColumnName == "BO_SCALE_MIN":
                    #Control - Scale Min cannot be greater than Scale Max
                    if NewValue >= float(cont.Rows[rowindex].Columns["BO_SCALE_MAX"].Value):
                        #Reset
                        #Trace.Write("Control - Scale Min cannot be greater than Scale Max")
                        cont.Rows[rowindex].Columns["BO_SCALE_MIN"].Value = str(EventArgs.ChangedCell.OldValue)
                    #Control - Scale Min cannot be lower than Scale Max of previous row
                    #Check if previous row is of the same Surcharge type
                    if rowindex-1 >= 0:
                        if cont.Rows[rowindex-1].Columns["BO_SURCHARGE_TYPE"].Value == cont.Rows[rowindex].Columns["BO_SURCHARGE_TYPE"].Value:
                            #Get Scale Max of previous row
                            prevScaleMax = float(cont.Rows[rowindex-1].Columns["BO_SCALE_MAX"].Value) if cont.Rows[rowindex-1].Columns["BO_SCALE_MAX"].Value != "" else float()
                            if prevScaleMax >= NewValue:
                                #Reset
                                #Trace.Write("PrevMax - "+str(prevScaleMax)+" ValMin -"+str(NewValue))
                                cont.Rows[rowindex].Columns["BO_SCALE_MIN"].Value = str(EventArgs.ChangedCell.OldValue)
                #Controls when Scale Max is being changed by the user
                if EventArgs.ChangedCell.ColumnName == "BO_SCALE_MAX":
                    #Control - Scale Max cannot be less than Scale Min
                    if NewValue <= float(cont.Rows[rowindex].Columns["BO_SCALE_MIN"].Value):
                        #Reset
                        cont.Rows[rowindex].Columns["BO_SCALE_MAX"].Value = str(EventArgs.ChangedCell.OldValue)
                    #Control - Scale Max cannot be greater than Scale Min of next row
                    #Check if next row is still within the container rows
                    #Trace.Write("next index - "+ str(rowindex+1) +" number indexes - "+str(cont.Rows.Count-1))
                    if rowindex+1 <= cont.Rows.Count-1:
                        #Check if next row concerns the same surcharge type
                        if cont.Rows[rowindex+1].Columns["BO_SURCHARGE_TYPE"].Value == cont.Rows[rowindex].Columns["BO_SURCHARGE_TYPE"].Value:
                            #Get Scale Min of next row
                            nextScaleMin = float(cont.Rows[rowindex+1].Columns["BO_SCALE_MIN"].Value) if cont.Rows[rowindex+1].Columns["BO_SCALE_MIN"].Value != "" else float()
                            #Trace.Write("nextScaleMin - "+ str(nextScaleMin))
                            if nextScaleMin <= NewValue:
                                #Reset
                                cont.Rows[rowindex].Columns["BO_SCALE_MAX"].Value = str(EventArgs.ChangedCell.OldValue)
            #Internal contol - Check if value is negative, reset value
            else:
                cont.Rows[rowindex].Columns[EventArgs.ChangedCell.ColumnName].Value = str(EventArgs.ChangedCell.OldValue)
        #BRIAN #2342-------------------------E   N   D------------------------------------------------------------
except Exception as e:
    Trace.Write("Error in script BO_SURCHARGE_CONT_OnCellChanged --> " + str(e))
