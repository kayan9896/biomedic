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



self.model.success=null

def _process_loop(self):
    self.scn = 'init'
    while self.is_running:
        frame = update_backendstates()
        newscn = self.eval_modelscnario()
        if newscn == self.scn continue
        dataforsave, dataforvm = self.model.exec(self.scn, frame)
        self.scn = newscn[:-3] + 'end'
        self.viewmodel.update(dataforsave)
        self.exam.save(dataforsave)

def eval_modelscnario(self):
    match self.scn:
        case 'init':
            if self.frame_grabber._is_new_frame_available:
                if self.imuonap:
                    return 'frm:hp1-ap:bgn'
                if self.imuonob:
                    return 'frm:hp1-ob:bgn' 
            return self.scn

        case 'frm:hp1-ap:end', 'frm:hp1-ob:end':
            if self.model.data.hp1-ap.success and self.model.data.hp1-ob.success:
                return 'rcn:hmplv1:bgn'
            else:
                if self.frame_grabber._is_new_frame_available:
                    if self.imuonap:
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob:
                        return 'frm:hp1-ob:bgn'
                return self.scn

        case 'frm:hp2-ap:end', 'frm:hp2-ob:end':
            if self.model.data.hp2-ap.success and self.model.data.hp2-ob.success:
                return 'rcn:hmplv2:bgn'
            else:
                if self.frame_grabber._is_new_frame_available:
                    if self.imuonap:
                        return 'frm:hp2-ap:bgn'
                    if self.imuonob:
                        return 'frm:hp2-ob:bgn'
                return self.scn

        case 'rcn:hmplv1:end':
            if self.model.data.hmplv1.success:
                #user goes next
                if self.uistates == 'next':
                    self.uistates = None
                    if self.frame_grabber._is_new_frame_available:
                        if self.imuonap:
                            return 'frm:hp2-ap:bgn'
                        if self.imuonob:
                            return 'frm:hp2-ob:bgn'
                
                #user submits landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:hmplv1:bgn'

                #user does nothing/ editing
                #they can retake
                if self.frame_grabber._is_new_frame_available:
                    if self.imuonap:
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob:
                        return 'frm:hp1-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn
            
            else:
                #fail, redo or retake, similar to success redo/retake
        
        case 'rcn:hmplv2:end':
            #if success, start reg immediately
            if self.model.data.hmplv2.success:
                return 'reg:pelvis:bgn'
                
            else:
                #fail, redo recon or retake, similar to hmplv1
        
        case 'reg:pelvis:end':
            if self.model.data.pelvis.success:
                #user goes next to cup
                if self.uistates == 'next':
                    if self.frame_grabber._is_new_frame_available:
                        if self.imuonap:
                            return 'frm:cup-ap:bgn'
                        if self.imuonob:
                            return 'frm:cup-ob:bgn' 
                    return self.scn
            
            else:
                #fail, redo reg/recon or retake hp1/hp2, similar to hmplv2        

        case 'frm:cup-ap:end':
            #take ob or retake ap, no recon
            if self.frame_grabber._is_new_frame_available:
                if self.imuonap:
                    return 'frm:cup-ap:bgn'
                if self.imuonob:
                    return 'frm:cup-ob:bgn'
            return self.scn
        
        case 'frm:cup-ob:end':
            if self.model.data.cup-ap.success and self.model.data.cup-ob.success:
                return 'rcn:acecup:bgn'
            else:
                if self.frame_grabber._is_new_frame_available:
                    if self.imuonap:
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob:
                        return 'frm:hp1-ob:bgn'
                return self.scn

        case 'rcn:acecup:end':
            if self.model.data.reccup.success:
                #start analyzecup
                return 'reg:acecup:bgn'
                
            else:
                #redo recon or retake
        
        case 'reg:acecup:end':
            if self.model.data.regcup.success:
                #user goes next to tri
                if self.uistates == 'next':
                    if self.frame_grabber._is_new_frame_available:
                        if self.imuonap:
                            return 'frm:tri-ap:bgn'
                        if self.imuonob:
                            return 'frm:tri-ob:bgn' 
                    
                #user submits landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:acecup:bgn'

                #user does nothing/ editing
                #they can retake
                if self.frame_grabber._is_new_frame_available:
                    if self.imuonap:
                        return 'frm:cup-oa:bgn'
                    if self.imuonob:
                        return 'frm:cup-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn
            else:
                #fail
                
