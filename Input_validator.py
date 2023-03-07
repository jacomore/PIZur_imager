def input_new_scan_edges(self,scanedges,axisedges):
    """Asks for and returns new edges for the 1D scan
    """ 
    print(f"Invalid input: desired scan range [{scanedges[0]},{scanedges[1]}] is not within axis range: [{axisedges[0]},{axisedges[1]}]")
    while True: 
        try:
            neg = float(input("Please, type a new value for the negative edge: "))
            pos = float(input("Please, type a new value for the positive edge: "))
            new_scanedges = [neg,pos]
            new_scanedges.sort()
            break
        except ValueError:
            print("That was no valid number!")
    return new_scanedges

def target_within_axis_edges(self,scanedges,axisedges):
    """
    Sorts values of scanedges and, is they are not comprised in axis_edges,
    invokes input_new_edges to get new edges

    Arguments:
    --------
    device (str) : "master" or "servo", to identify the scan edges to which controller is referred
    """ 
    scanedges.sort()
    while (scanedges[0] < axisedges[0] or scanedges[1] > axisedges[1]):
        scanedges = self.input_new_scan_edges(scanedges,axisedges) 
    return scanedges
