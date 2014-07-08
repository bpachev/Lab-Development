import itertools
from bisect import bisect_left

class Session(object):
    def __init__(self):
        self.channels = {}
        self.register_channel(0)
        self.sessionlog = []
        self.users = {}
        
    def register_channel(self, n, topic=None):
        #check if channel already exists
        if n in self.channels:
            raise KeyError("Channel already exists!")
        
        self.channels[n] = topic
    
    def get_channels(self):
        return self.channels
    
    def log_message(self, message):
        if message['content'].strip():
            self.sessionlog.append(message)
        self.__emergency_purge__()
        
    def retrieve_new(self, nick, channel=0):
        def binary_search(timestamp):
            '''return index of first element that is >= timestamp'''
            
            imin, imax = 0, len(self.sessionlog)
            while imin <= imax:
                imid = (imax+imin)//2
                elem = self.sessionlog[imid]['timestamp']
                if elem < timestamp:
                    imin = imid + 1
                elif elem > timestamp:
                    imax = imid
            if imin == imax and self.sessionlog[imin]['timestamp'] == timestamp:
                return imid
            
        def filter_channel(message):
            if message['channel'] == channel:
                return True
            return False
            
        t = self.users.get(nick, None)
        if t:
            i = binary_search(t)
            mfilter = itertools.ifilter(filter_channel, 
                                        itertools.islice(self.sessionlog, i))
            return list(mfilter)
        return []
    
    def update_user(self, user, timestamp):
        self.users[user] = timestamp
        
    def change_nick(self, old_nick, new_nick):
        if new_nick not in self.users:
            if old_nick is not None:
                self.users[new_nick] = self.users.pop(old_nick)
            else:
                self.users[new_nick] = None
        else:
            raise KeyError
        
    def __emergency_purge__(self):
        if len(self.sessionlog) > 10000000:
            self.sessionlog = []