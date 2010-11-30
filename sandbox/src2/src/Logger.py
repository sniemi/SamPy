import time

class Logger:
    #this one use run when the class is initialized
    def __init__(self, filename):
        self.filename = filename
    #what should we do when the instance is called
    def __call__(self, string):
        file = open(self.filename, 'a')
        #creates a time stamp
        file.write('[' + time.asctime() + '] ')
        #writes the string
        file.write(string + '\n')
        file.close()

if __name__ == '__main__':
    #This is just for demoing:
    log = Logger('mylogfile.txt')
    log('Starting logging')
    #Here I could do calculations and looping
    log('My second loging entry...')
    #and then just before exit
    log('Program terminates, everything went fine...')
