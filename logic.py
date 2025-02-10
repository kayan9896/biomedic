class frame:
    def __init__(self):
    	self.hasimage: bool = False
		self.hasdata: bool = False
		self.validated: bool = False
		self.reconstructed: bool = False
		self.errorcode: int = 0
		
class pair: 
    def __init__(self):
        self.frame1: frame = frame()
	    self.frame2: frame = frame()
	    self.reconstructed: bool = False
	    self.errorcode: int = 0
	  
hp1=pair()
hp2=pair()

class pelvis: 
    def __init__(self, hp1, hp2):
        self.hp1:pair = hp1
		self.hp2:pair = hp2
		
class cup: 
    def __init__(self, angle1, angle2):
        self.pair:pair = pair()
	    self.measures: List[int] = [angle1, angle2]

class trial: 
    def __init__(self, length1, length2):
        self.pair:pair = pair()
	    self.measures: List[int] = [length1, length2]

class session: 
    def __init__(self):
        self.pelvis=None
		self.cup=None
		self.trial=None

def get_scn():
    stage = states[0]
    frame = states[1]
    match scn:
        case 1:
            #ini:imgrdy:bgn
            if not states._is_new_frame_available:
                #no new frames, return 1 to wait for new frames
                return 1
            #get the frame, return 2, ini:imgrdy:end
            return 2
        case 2:
            #at ini:imgrdy:end, return 3 to analyze frame for hp1 frame 1
            if session.pelvis.hp1.frame1.hasimage:
                return 3
            else:

        case 3:
            #hp1-ap:bgn
            if session.pelvis.hp1.frame1.validated:
                #validated, go to hp1-ap:end
                return 4
            else:
                #fail, return 1 to redo
                errorcode='000'
                return 1
            


    

def updatestates(res, scn, session):
    if scn == 1:
        if res:
            session.pelvis.hp1.frame1.hasimage = True
    if scn == 2:
        if res:
            session.pelvis.hp1.frame1.validated = True

