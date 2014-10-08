#!/usr/bin/env python
'''
This program is a remote control for IGV.  If you supply a tab-delimited text table where the first column of each line specifies
a genomic locus and any additional columns on the line specify full paths for bam files, this program will take snapshots
of the each bam file on the line at the locus listed in the first column (images can be taken all together or individually or both)
Written and tested on a Mac.  Will likely also work on Linux.  Has not been tested yet on a PC.
Version 1.1 changes: improved handling of output directories, program now accepts a user defined directory as -d on the commandline
demarcated a group of default values that users may wish to change at the beginning of the main subroutine, set the new default
output directory to a subdirectory of where the script is being run.  Avoids pesky permission issues, especially on a shared
system or resource (previously required a directory in the root).  Improved exception/error handling.  Preferences are now stored
in their own file.  Multiple preference files can be maintained and the specific one to use can be passed on the command line by
the user.  Version 1.2 changes: Cleaned up error messages a bit, applied a (hopefully) temporary workaround for bam files with
spaces in their names (spaces will be changed to underscores in the saved image.
Copyright 2014, Michael Weinstein, Daniel Cohn laboratory
This program is free to use but if I don't know that you are using it, please e-mail me to let me know that you are.
My e-mail address: michael (dot) weinstein (at) ucla (dot) edu
'''
def checkargs():  #subroutine for validating commandline arguments
    import argparse #loads the required library for reading the commandline
    import os  #imports the library we will need to check if the file exists
    parser = argparse.ArgumentParser()
    parser.add_argument ("-f", "--file", help = "Specify the file containing the loci and bam file paths.")  #tells the parser to look for -f and stuff after it and call that the filename
    parser.add_argument ("-d", "--directory", help = "Specify the directory for output (a subdirectory will be created for this session)")
    parser.add_argument ("-p", "--prefsfile", help = "Specify an alternate default preferences file.")
    parser.add_argument ("-g", "--genome", help = "Specify the genome to use.")
    parser.add_argument ("-o", "--host", help = "Specify a host.")
    parser.add_argument ("-r", "--port", help = "Specify a port to use.")
    args = parser.parse_args()  #puts the arguments into the args object
    directory = args.directory
    genome = args.genome
    host = args.host
    port = args.port
    if not directory:
        directory = False   #not a strictly necessary statement, since returning a blank would evaluate to false, but explicit >>> implicit
    prefsfile = args.prefsfile
    if not prefsfile:
        prefsfile = False    #Like above, not strictly needed
    if not genome:
        genome = False
    if not host:
        host = False
    if not port:
        port = False
    if not args.file:  #if the args.file value is null, give an error message and quit the program
        usage("No file specified.") 
        quit()
    elif not os.path.isfile(args.file):  #if the file specified in the arguments doesn't exist, quit the program and give an error message
        usage("Could not locate " + args.file + "on this system.") 
        quit()
    else:
        return (args.file, directory, prefsfile, genome, host, port)  #returns the validated filename and directory to the main program
    
def filenamesfree(directory):  #this subroutine checks if the series of filenames we are likely to need is free
    import os  #imports the library we will need to check filenames in the directory
    if os.path.isdir(directory):  #checks each potential output filename as the loop iterates
        return False  #if it finds that a file by the current name being tested exists, exits the subroutine returning a false value
    return True  #if it finds none of the files exist, it returns a true value

def generatelist(file):
    listfile = open(file, 'r')  #opens the file containing the list of loci and bam files for reading
    line = listfile.readline()  #reads the first line of the locus file
    list = []  #initializes an empty list to contain one line in each element
    while line:  #this loop will iterate until the read is a null (end of file)
        list.append(line)  #adds the most recently read line to the list as the last element
        line = listfile.readline()  #reads the next line from the locus file (if it is a null due to reaching the end of file, it will cause the loop to end)
    listfile.close() #closes the locus file
    return list  #sends back a list where each element is a line from the file starting with a genomic locus and containing bam file paths with everything separated by tabs

def createsavedir(directory):
    import os  #we need this to look for and create a directory
    import datetime #we need this to get time and date info in order to name the directory
    now = datetime.datetime.now()  #stores the current date and time to the value "now"
    directory = directory + '/IGVimages.' + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + str(now.hour).zfill(2) + str(now.minute).zfill(2) #creates a working directory for this run (identified by date and time of the run)
    if not filenamesfree(directory):  #checks to see if the directory we want is already created (such as someone encountering an error and then quickly starting again) this avoids collisions of filename where data could be overwritten
        return False  #will cause this function to return the boolean value of False if the directory was already in existence
    else:
        try:
            os.makedirs(directory)  #actually creates the new directory
        except PermissionError:
            print ('\nPermission to create the directory ' + directory + ' was denied.  Please run this program with appropriate permissions or create it using your file manager.')
            return False
        except:
            print ('\nUnable to make the directory ' + directory + '.')
            return False
        return directory  #and returns the directory name to the main subroutine
    
def clean(line):  #this subroutine cleans up the line and makes sure it looks somewhat usable (starts with a genomic locus followed by a tab)
    import re  #we need this library to do a regex
    line = line.strip('\r\n\t ') #removes any leading or trailing endlines, spaces, and tabs
    line = re.sub('^chr', '', line) #removes a "chr" from the beginning of the line (before the chromosome number).  That will be added later and will prevent it from causing problems later
    if not re.match('1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|x|Y|y|mt|MT|Mt\:\d+?]+?\t.+$',line): #the actual regex looking to see if the line starts with a chromosome, then a colon, then a number, then a tab (which will begin the file path list)
        return False #if the line does not match that pattern, the subroutine returns the boolean value False to the main subroutine
    return line #otherwise it returns the cleaned line

def usage(sin):  #This subroutine prints directions
    print ('Error: ' + sin)
    print ('This script will take a tab-delimited list with the first column containing a genomic locus (formatted as ##:#######)')
    print ('You should have IGV running while using this script.  The default output directory for this session will be a subdirectory')
    print ('of the one containing this script called /autoIGVimages/IGVimages.YYYYMMDDHHMM (YearMonthDayHourMinue).')
    print ('Sample commandline:\npython3 autoIGV.py -f file.txt -d /directory/subdirectory')
    print ('The -f (file) is a necessary commandline argument.  The -d (directory) is optional, as this script has a default.')
    
def connect(host, port):  #this subroutine creates the connection between the script and IGV
    import socket  #the library needed for the low-level network connection
    igv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #creates a socket object called IGV
    igv.settimeout(20)  #sets IGV to give a timeout error if a command goes unresponded to for more than 20 seconds
    print('Attempting to establish a connecting with IGV...', end = '')  
    try:  #this statement contains an action that could cause a non-fatal exception to occur
        igv.connect((host, port))  #actually creates the connection with IGV on the local system
    except ConnectionRefusedError: #if the connection is refused (likely because IGV is not open or configured to allow connections).  This handles that exception mentioned above
        usage('Unable to connect to IGV.  Be sure that IGV is running and configured to accept connections on its default port (60151)')  #prints an error message
        quit() #and quits the program more gracefully than an unhandled exception
    except:
        usage('Unexpected error trying to connect with IGV.')
        quit()
    print('OK\nTesting connection...', end = '')
    try: #every time we send a command to IGV, we risk a BrokenPipeError if IGV stops functioning or the connection is otherwise broken.  This try/except statement will handle that more gracefully than simply having the program crash out with a long error message.
        igv.send(rawbytes('echo\n'))  #sends the command "echo" to IGV.  IGV should respond to this by repeating "echo" back to me
    except BrokenPipeError:  #what to do if this kind of error occurs (due to a failure to transmit the command to IGV successfully)
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending test message to IGV.')
    await(igv, 'echo')  #waits for and checks the IGV response
    print ('OK')
    return igv #returns the new and active socket connection

def cmdnew(igv):  #subroutine to tell IGV to clear its display and start a new session
    import socket
    try:
        igv.send(rawbytes('new\n')) #send IGV the "new" command
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending NEW command to IGV.')
    success = await(igv) #wait for acknowledgement from IGV that it is done and there were no errors returned
    if success:
        return True
    else:
        return False

def cookbytes(rawbytes):  #subroutine to take a utf-8 bytes input (such as what gets returned on a socket connection) and return a string from it.  The opposite of what the rawbytes function does.
    return str(rawbytes.decode('utf-8'))

def rawbytes(stringin):  #subroutine to take a string and make it into UTF-8 bytes, often for sending via socket connection
    return bytes(stringin, 'utf-8')

def cmdgenome(genomeid, igv): #tells IGV which genome to use
    import socket
    try:
        igv.send(rawbytes('genome ' + genomeid + '\n'))  #send the actual command to IGV to use a specific genome
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending GENOMEID command to IGV.')
    success = await(igv)  #wait for acknowledgement
    if success:
        return True
    else:
        return False

def cmdgotolocus(locus, igv):
    import socket
    try:
        igv.send (rawbytes('goto chr' + locus + '\n'))  #sends IGV a command to go to a specific locus
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending GOTO command to IGV.')
    success = await(igv) #wait for acknowledgement from IGV that it is done and there were no errors returned
    if success:
        return True
    else:
        return False

def cmdsaveimage(source, locus, igv):
    import socket
    import re
    import ntpath
    try:
        igv.send(rawbytes('collapse\n')) #tells IGV to collapse the image so we can fit it better in the photo
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending COLLAPSE command to IGV.')
    success = await(igv) #wait for acknowledgement from IGV that it is done and there were no errors returned
    if not success:
        return False
    cleansource = re.sub('\\ ', ' ', source)
    cleanlocus = re.sub('\:', 'c', locus)
    filename = ntpath.basename(cleansource)
    filename = cleanlocus + filename
    filename = re.sub(' ', '_', filename)  #NEWTEST  #uses a regex to change any " " into "_" (this was causing trouble with having IGV save the file)
    try:
        igv.send(rawbytes('snapshot ' + filename + '.png\n')) #the actual command telling IGV
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending SNAPSHOT command to IGV.')
    success = await(igv) #wait for acknowledgement from IGV that it is done and there were no errors returned
    if success:
        return True
    else:
        return False

def cmdloadfile(filename, igv):  #converts the filename to url format (easier for IGV to handle) and tells IGV to load it
    import socket
    import re
    urlfile = 'file://' + re.sub(' ', '%20', filename)  #uses a regex to change any "\ " into " " (this would be an issue with terminal-formatted paths)
    urlfile = re.sub(r'\\', '/', urlfile)  #uses a regex to change any other backslashes into forward slashes (this would be an issue with windows-formatted paths)
    try:
        igv.send(rawbytes('load ' + urlfile + '\n'))  #sends the command to IGV to open the file
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending LOAD command to IGV.')
    success = await(igv) #wait for acknowledgement from IGV that it is done and there were no errors returned
    if success:  #note that if IGV returns an error here opening the file, we will know it by this subroutine returning a "False" value.  If I wanted to make it slightly more efficient (but harder to understand), I could have replaced the 5 lines starting with "success = await(igv)" with the single line "return await(igv)"
        return True
    else:
        return False

def await(igv, expectedresponse = ''):  #the second argument here is optional, and is only going to be supplied if the goal is to get a specific response from IVG (probably echo).  IGV usually responds "OK" when a command is completed or with Error:(Message) when a command fails.
    import socket
    import re
    try:  #the following statement could generate an exception, so we are preparing to handle it
        response = cookbytes(igv.recv(4096))  #this is going to wait for and read the response from IGV.  The cookbytes function is the opposite of the rawbytes one and turns UTF-8 from a socket response into a string
        response = response.strip('\r\n\t')
    except socket.timeout:  #if we timeout waiting for a response (indicating something has gone wrong)
        usage('Timeout waiting for IGV to respond.  Has it locked up or been terminated or is another application already communicating with it on that port?')  #display an error message
        igv.close()
        quit()
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error awaiting response from IGV.')
    if expectedresponse == '':  #if there was no expected response provided
        if response == 'OK':
            return True
        if re.match('^ERROR\W*?Could not locate genome', response , re.IGNORECASE):
            quit('Fatal error: The genome requested is not valid.  If this was done using your default preferences, please delete the preferences file and restart the program.')
        if re.match('^ERROR\W*?directory.+?does not exist', response , re.IGNORECASE):
            errormessage = re.search('^ERROR\W*?(\w+?)', response, re.IGNORECASE)  #uses a regex to capture any error messages returned
            errormessage = errormessage.string.strip('\t\r\n')  #remove any leading or trailing tabs or end of lines
            quit('IGV is unable to save to the desired directory.  Check permissions or if the directory name is invalid.\nIGV response - ' + errormessage)
        if re.match('^ERROR\W*?\w+?', response, re.IGNORECASE):  #checks to see if the response was an error message (which will begin with "Error")
            errormessage = re.search('^ERROR\W*?(\w+?)', response, re.IGNORECASE)  #uses a regex to capture any error messages returned
            errormessage = errormessage.string.strip('\t\r\n')  #remove any leading or trailing tabs or end of lines
            print ('\nIGV returned the message:' + errormessage)
            return False
        else:
            print('Possible error: IGV says "' + response + '."')
            return True
    if expectedresponse != '':  #if an expected response was supplied (often testing the echo)
        if response == expectedresponse: #asks if IGV responded in the expected manner
            return True  #if so, returns true
        else:
            usage('IGV returned an unexpected response to a test command.')  #if not, displays an error message
            igv.close()
            quit()
                
def bamfile(filename): #checks the validity of the entered bam file
    import re
    if not fileexists(filename):  #checks to be sure the file exists
        return False  #if not, returns a false value
    return re.match('.*\.bam$', filename)  #checks to make sure that the filename ends in .bam

def fileexists(filename):  #subroutine to confirm that a file exists
    import os
    test = os.path.isfile(filename)  #sets test to the boolean of if the file exists 
    return test  #and returns that boolean value

def wellformed(locus):  #subroutine to make sure that the locus looks like a locus
    import re
    foundlocus = re.match('(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|x|Y|y|mt|MT|Mt)(\:\d+)', locus)  #a regex that will capture a cromosome (1-22 or X or Y or mt)
    if foundlocus:  #if it found something that looked like a locus
        return (True, foundlocus.group())  #returns true for a successful run and a string with the locus itself (now cleaned up)
    else:
        return (False, 'Malformed')

def multibamlist(list):  #function for looking through several lines to see if they have multiple bam files listed
    for line in list: #creates a loop throught he lines
        if multibam(line): #runs the multibam test for each line individually
            return True  #returns true if any of them are multibams
    else:
        return False #returns false if none of them are

def multibam(line):  #function for testing a single line to see if multiple valid bam files are listed
    bamfiles = 0  
    linearray = line.split('\t') #splits the line on each tab
    for i in range(0,len(linearray)):  #sets up a loop to iterate through the elements on the line
        if i == 0:  #if we are looking at the first element (should be a genomic locus)
            if clean(linearray[i]): #check to see if the locus is clean
                continue  #if so, move on to the next iteration to check bam file paths
            else:  #if the locus appears malformed or otherwise bogus
                bamfiles = 0  #sets the number of bamfiles for the line to zero (even if there are valid files listed, we have nothing to look at without a valid locus)
                break  #end this loop entirely and move on to the next block of code
        else:
            if bamfile(linearray[i]):  #checks to see if the file listed looks like a bam file and actually exists
                bamfiles += 1 #if so, adds 1 to the count of bamfiles
        if bamfiles > 1:  #after completing the loop through the elements on the line, if there is more than one valid file listed
            return True #send back a value of True
    return False  #otherwise we return a value of false (this line did not have multiple bam files)

def getphotoprefs():
    answer = False
    while not answer:  #enters the loop and stays in it until a valid answer is given
        print ('\nAt least one line has multiple BAM files listed.\nHow would you like your snapshots?\n\t1. All files at once for the line.\n\t2. One file at a time at each locus.\n\t3. Both.')
        answer = input('>>') #sets answer equal to some value input by the user
        answer = str(answer)
        if answer == '1' or answer == '2' or answer == '3':
            return answer
        else:
            print('Invalid response.')
            answer = False #set answer to false so the loop will continue until a satisfactory answer is given

def cmdsetimagedirectory(directory, igv):
    import socket
    import os
    if directory[0] != '/':  #checks if the directory being used is absolute (starts with a slash) or relative (does not)
        cwd = os.getcwd()  #if a relative directory is being used, this gets the current working directory (CWD)
        directory = cwd + '/' + directory  #and adds it to the relative directory we have been using because IGV does not know what the working directory is (and will become very cross with us for passing a bogus directory here)
    try:
        igv.send(rawbytes('snapshotDirectory ' + directory + '\n'))  #tells IGV where to save the snapshot  CAN THIS BE MOVED OUT OF THE LOOP AND SET ONCE FOR EFFICIENCY (DOES IGV REMEMBER THE DIRECTORY BETWEEN STEPS)?
    except BrokenPipeError:
        quit('Connection with IGV lost.  Please confirm that IGV is still running properly.')
    except:
        quit('Unexpected error sending SNAPSHOTDIRECTORY command to IGV.')
    return await(igv)  #this is another (more efficient) way of ending my subroutines.  Functionally, this is the same as my usual endings using the "success" variable

def yesanswer(question):  #asks the question passed in and returns True if the answer is yes, False if the answer is no, and keeps the user in a loop until one of those is given.  Also useful for walking students through basic logical python functions
    answer = False  #initializes the answer variable to false.  Not absolutely necessary, since it should be undefined at this point and test to false, but explicit is always better than implicit
    while not answer:  #enters the loop and stays in it until answer is equal to True
        print (question + ' (Y/N)')  #Asks the question contained in the argument passed into this subroutine
        answer = input('>>') #sets answer equal to some value input by the user
        if str(answer) == 'y' or str(answer) == 'Y':  #checks if the answer is a valid yes answer
            return True  #sends back a value of True because of the yes answer
        elif str(answer) == 'n' or str(answer) == 'N': #checks to see if the answer is a valid form of no
            return False  #sends back a value of False because it was not a yes answer
        else: #if the answer is not a value indicating a yes or no
            print ('Invalid response.')
            answer = False #set ansewr to false so the loop will continue until a satisfactory answer is given
    
def loadprefs(prefsfile): 
    import os
    if prefsfile:  #if a preferences file is already specified (because the user specified one on the command line)
        prefslist = parseprefs(prefsfile)  #try to load the user-specified prefs file
        if prefslist:  #if we could load it and generate a good preferences list from it
            return prefslist #return that list and go on with the program
        else:  #if we could not load a good list from it either due to the file not existing or not appearing to be a valid prefs list
            prefsfile = False  #tells the program we no longer have a prefsfile set
            print ('\nUnable to load user-specified preferences.')
            if not yesanswer('Proceed using default preferences?'):  #check if the user wants to go to the default file and keep going
                quit('OK.  Bye.')  #if not, we exit the program
    if not prefsfile: #by this point, we either got no user specified prefs file, or the one we got was bad and the user wants to use default.  Either way, it should be false at this point.
        prefsfile = 'autoIGVprefs.ini'  #this is the hard-coded name for the default prefs file
        prefslist = parseprefs(prefsfile)  #try to load the preferences from the default file
        if prefslist:  #if that was successful and we have a list (and not a False)
            return prefslist  #return the list to the program and get on with it
    if not prefslist:  #if the list was returned as False (becaue we could not load it from the default file or the file did not exist)
        if os.path.isfile(prefsfile):  #check if the default file even exists.  if so, we have the user delete it and rerun the program.  If not, we create it (the block of code under "else")
            print('\nUnable to load preferences from default file, the file might be corrupt.')
            quit('Please delete or repair the default preferences file (autoIGVprefs.ini) and restart this program.')  #other option would be to have the program delete the file and keep going, but it is safer to have the user delete the prefs file themselves
        else:  #if no default preferences file was found
            print('\nNo preferences file found.') 
            makeprefsfile(prefsfile)  #run the subroutine to make the preferences file
            prefslist = parseprefs(prefsfile)  #load the preferences from that file
            if prefslist:  #make sure we loaded a good list of preferences
                return prefslist  #and return them to the program
            else:  #if we are unable to read good preference settings from the file we are supposed to have just written, there must be a great disturbance in the force
                quit('Unexpected problem creating or reading new preferences file.')  #quitting for safety, as something must be wrong here
        
def parseprefs(prefsfile):  #this function does the actual reading of the preferences file
    import os
    if os.path.isfile(prefsfile):  #checks to make sure that the prefs file specified exists, otherwise skips directly to the final else statement and returns False (we read no prefs from no files)
        file = open(prefsfile, 'r')  #open the prefs file that we just checked to make sure is there.  Not going to put an error handler on this, as any error is something the user needs to see and should quit the program
        line = file.readline()  #reads the first line of the file
        line = line.strip('\r\n\t ')  #removes any unwanted characters from the start and end of the line
        if line != 'Order: host, port number, genome, default directory':  #checks to make sure that the line exactly matches how we set up a preferences file first line (if it does not, the file can't be trusted)
            return False  #and returns false if the first line doesn't pass the test
        prefslist = []  #initializes a blank list for the preferences
        while line:  #while we have some data that we read from the file (line will be blank after the end of the file and will exit the loop for us)
            line = file.readline()  #read the next line of the file in as line
            line = line.rstrip('\r\n\t ')  #remove unwanted characters from the ends
            if line:  #if line is not blank
                prefslist.append(line)  #add it to the list of preferences in order
        try:  #this is actually to perform another test of validity
            int(prefslist[1])  #try turning the value in the preferences file that was given as the port number into an integer
        except ValueError:  #if we get back a ValueError (because it was not something that could be turned into an integer type of variable)
            return False  #return False because something is wrong with the data in the file
        return prefslist  #otherwise return the validated list
    else:  #this is where we go if the file passed into this function did not exist
        return False  #skip everything above and just return false, there was nothing to read or test in the file
    
def makeprefsfile(prefsfile):  #makes a new preferences file if the old one was not found (the status of the old one was determined in a higher subroutine)
    import os
    if os.path.isfile(prefsfile):  #checks to make sure that no preferences file exists (this avoids risk of overwriting something unintentionally and forces the user to delete the old file themselves if there was one)
        quit('Default prefsfile already found.  Please delete this file and then start again.')
#begin default settings, only change if you know what you are doing
    host = 'localhost'  #you could possibly (I haven't tested this) control IGV on somebody else's computer.  I wouldn't recommend it.
    port = 60151 #this is the default port used by IGV.  If yours is set to something else, you will need to alter this either here or in the preferences file (the program will ask)
    genome = 'hg19'  #this is the hg version I am using at the time of writing this program
    defaultdirectory = 'autoIGVimages'  #this means that the default directory for saving images will be a subdirectory of the one in which this program is being run, with the actual directory being a function of date and time
#end default settings
    print('Creating default preferences file:')
    if not yesanswer('Default host = ' + host):  #the next several blocks are checking if the user wants to use the defaults or would rather set their own value
        host = False
        while not host:
            host = input('Please enter host identifier or IP address\n>>>')
            if not host:  #if nothing was entered we will display this error message.  Because the value will evaluate for false with nothign entered, the loop will continue asking for a value
                print('Host name required.')
    if not yesanswer('Default port = ' + str(port)):
        port = False
        while not port:
            port = input('Please enter a port number to use with IGV\n>>>')
            try:  #port gets a second test beyond just being blank or not
                int(port)  #check if the input value can be converted to an integer
            except ValueError:  #if not, we don't accept the answer and ask for another
                print('Port number must be an integer.')  
                port = False
    if not yesanswer('Default genome = ' + genome):
        genome = False
        while not genome:
            genome = input('Please enter a genome to use\n>>>')
            if not genome:
                print('Genome name required.')
    if not yesanswer('Default directory = ' + defaultdirectory):
        defaultdirectory = False
        while not defaultdirectory:
            defaultdirectory = input('Please enter a default directory for output\n>>>')
            if not defaultdirectory:
                print('Default directory required.')
    allprefs = 'Order: host, port number, genome, default directory\n' + str(host) + '\n' + str(port) + '\n' + str(genome) + '\n' + str(defaultdirectory)  #creates a string with the entire contents of the preferences file
    if os.path.isfile(prefsfile):  #checks to make sure that no preferences file exists.  There should not be one, as we checked at the beginning of this subroutine, but this quick check protects against issues related to time of validation vs. time of use
        quit('Default prefsfile already found.  Please delete this file and then start again.')
    output = open(prefsfile, 'w')  #creates and opens the preferences file for writing.  I could add error handling for this, but I would rather the user see any error messages that appear and the program quits
    output.write(allprefs)  #writes the already formed preferences string to the file
    output.close()  #closes the file  (because we did not set any different buffering for the file, Python does not purge the buffer and write the actual file until this step, I believe.  If we were writing a VCF with gigs of data, how would we want to do this differently?)
    
def main():
    stackshot = False #initializing a variable for how the user wants photographs taken
    singleshot = False #initializing another variable for another way the user might want photographs taken (at least one of these will be set to true before we start imaging)
    print ('\nInitializing:')
    import time  #this module lets us determine how long the run took (it is used only once at the very start and once at the very end of the program)
    starttime = time.time() #mark the start time
    args = checkargs() #get the list of loci and bam files from the commandline arguments, takes a user-specified directory as an optional argument (returned as False if none was given).  DOES NOT CHECK VALIDITY OF THE DIRECTORY, ONLY THE INPUT FILE.  Check the directory at time of creation.
    locusfile = args[0]
    directory = args[1]
    prefsfile = args[2]
    genome = args[3]
    host = args[4]
    port = args[5]
    print ('Loading preferences...', end = '')
    prefs = loadprefs(prefsfile)
    print('PREFERENCES LOADED')
    if not host:
        host = prefs[0]  #directs the socket to this system (I do not recommend setting this to run IGV on someone else's system unless you both know what you're doing.)
    if not port:
        port = int(prefs[1])  #sets the port number to use to the default port for IGV to accept remote commands.  Likely to be returned as a string, so need to convert here.
    if not genome:
        genome = prefs[2]  #sets the genome to use.  If you are using a different genome (either version of human or a different species), you will need to change this
    defaultdirectory = prefs[3]  #sets the default directory for dumping the IGV image captures
    igv = connect(host, port) #calls the subroutine to start a connection with IGV.  Will exit the program if connection is not successful
    print ('Getting list of targets...', end = '')
    locuslist = generatelist(locusfile)  #gets the file with the loci to image and which files to image from.  Lines should be formatted with the locus as the first item, then a tab, then a list of bam file paths separated by tabs
    print ('OK\nCreating directory for saving this session\'s images...', end = '')
    if directory:  #if the user specified a directory, this will execute.  If they did not, directory would be false from the value taken from the checkargs function
        directory = createsavedir(directory) #either gets the working directory name (the user specified one plus the subdirectory that is made up of the date and time of the run), or false if it failed
        if not directory:  #if we could not use the specified directory
            print ('Failed to create user-specified directory.')
            if not yesanswer('Do you want to switch to the default (' + defaultdirectory + ')?'):  #offer to use the default instead
                quit('OK.  Bye.')  #if they do not want this, quit
    if not directory:  #this will try to create a working directory using the default if either no directory was specified or the user specified one failed and the user wanted to continue
        directory = createsavedir(defaultdirectory)   #subdir for saving will be named with the date and time.  files within will be named ??chr??????.bamfilename.png
    if not directory:  #if no directory was returned (if we can't create a directory using even the default name, we end)
        usage('Output directory already appears to exist or could not be created.')
        igv.close()
        quit()
    print ('OK\nSetting the genome in IGV...', end = '')
    if not cmdgenome(genome, igv):  #tells IGV which genome to use (and checks for errors in execution of this command).  A connection should already be established, so a failure here would either mean trying to load an unavailable genome or loss of connection to IGV.  Either one means the program should stop.
        usage('Failed to communicate with IGV on "genome selection" command for line ' + linecount + '.')
        igv.close()
        quit()
    print ('OK\nSetting the snapshot save directory on IGV...', end = '')    
    if not cmdsetimagedirectory(directory, igv):  #sends the command to IGV to set the output directory for images to the appropriate one for this session
        usage('Failed to communicate with IGV when setting the snapshot directory.')
        igv.close()
        quit()
    print ('OK\nChecking the list of targets...', end = '')
    if multibamlist(locuslist): #checks to see if any of the lines in the locus list have multiple valid bam files listed.  If so, runs the next block to find out how the user wants them photographed
        photoprefs = getphotoprefs()  #runs a subroutine to ask the user what they want to do for photos of multiple BAM files at a single locus
        if photoprefs == '1':
            stackshot = True
        if photoprefs == '2':
            singleshot = True
        if photoprefs == '3':
            stackshot = True
            singleshot = True
        print ('\nInitialization complete.\nStarting the run: \n')
    else: #if the multibamlist function returns false because each line only has a single valid bam file listed, this will set it to just shoot single bams at each locus (this will be done silently as far as the user goes)
        singleshot = True
        print ('OK\nInitialization complete.\nStarting the run: \n')
    linecount = 0  #initializes a variable to count our line number (used for informing the user of progress)
    for locus in locuslist:
        linecount += 1  #increments the line counter
        if not locus: #if the line is blank, ignore it entirely 
            continue
        locus = locus.rstrip('\r\n\t') #removes any potentially troublesome characters (leading and trailing returns, tabs, and newlines) from the line
        locusarray = locus.split('\t') #splits the line into an array on each tab.  The first element should be the locus and any subsequent elements should be bam file paths
        locus = clean(locus)  #cleans up the line and verifies that it starts with a valid locus followed by a tab and then some additional characters (should be bam file paths).  Also removes a chr at the beginning of the locus (if there is one).  It will be added back in the process of sending it to IGV, as IGV seems to prefer it that way.
        if not locus:  #if clean returned a value of false due to a problem with the line
            print('Skipped line ' + str(linecount) + ': ' + locusarray[0] + ' as the line in ' + locusfile + ' appears to have formatting errors.')
            continue
        locusform = wellformed(locusarray[0])  #checks the locus itself to make sure it is properly formatted
        if not locusform[0]:  #if it returns a False due to a problem with the locus
            print('Skipped line ' + str(linecount) + ': ' + locusarray[0] + ' in file ' + locusarray[1] + ' as the locus appears to be malformed.')
            continue
        locusarray[0] = locusform[1]  #sets the locus value we will be using to the one returned by the form-checking function
        if not cmdgotolocus(locusarray[0], igv): #We can have this here because IGV will keep the previous locus after a "new" command.  If it stops doing this, we have to move this call inside the inner loop and use a "break" command instead of a "continue". This subroutine will return a value of True if it executes successfully and gets no error message from IGV
                print ('Error loading going to locus ' + locusarray[0] + ' see previous line for details.  Skipping to next locus.')  #so if false is returned, it will display an error message and try the next locus
                continue #moves on to the next locus by forcing the loop to iterate without doing anything more 
        if stackshot and (multibam(locus) or not singleshot):  #if the user selected to get group photos of multiple bam files at each locus it will do this (if the user selected both multi and single image outputs and the line only had a single valid bam file, this will be skipped as both the multi and single shots would look the same)
            print ('Processing locus ' + str(linecount) + ' of ' + str(len(locuslist)) + ' to take group photo.', end = ' \r')
            if not cmdnew(igv):  #clear the IGV screen
                usage('Failed to communicate with IGV on "new" command for line ' + linecount + '.')
                igv.close()
                quit()
            for i in range(1, len(locusarray)):
                if not locusarray[i]:  #if the element that should contain a bam file is just a blank 
                    continue #skip everything and go on to the next
                if not bamfile(locusarray[i]): #checks for a valid bamfile
                    print('Skipped ' + locusarray[i] + ' on line ' + str(linecount) + ' (locus: ' + locusarray[0] + ') in group photo due to it being missing or not a valid BAM file.')
                    continue
                if not cmdloadfile(locusarray[i], igv): #tells IGV to load the file
                    print ('Error loading file ' + locusarray[i] + ' in group photo; see previous line for details.  Skipping to next file.')
                    continue
            if not cmdsaveimage('all', locusarray[0], igv):  #tells IGV to shoot the image
                usage('Problem saving snapshot of ' + locusarray[0] + ' in ' + locusarray[i] + ' see previous line for details.\nPlease confirm that the directory /autoIGV/ exists and this script has access to write to it and create subdirectories.  Also try removing any non-word characters or whitespaces from your bam file name.')
                igv.close()
                quit()
        if singleshot:        
            for i in range(1, len(locusarray)):
                print ('Processing locus ' + str(linecount) + ' of ' + str(len(locuslist)) + ' file number ' + str(i) + ' of ' + str(len(locusarray)-1) + '.', end = ' \r')
                if not locusarray[i]:  #if the element that should contain a bam file is just a blank 
                    continue #skip everything and go on to the next
                if not bamfile(locusarray[i]):
                    print('Skipped ' + locusarray[i] + 'on line ' + str(linecount) + ' (locus: ' + locusarray[0] + ') due to it being missing or not a valid BAM file.')
                    continue
                if not cmdnew(igv):
                    usage('Failed to communicate with IGV on "new" command for line ' + linecount + '.')
                    igv.close()
                    quit()
                if not cmdloadfile(locusarray[i], igv):
                    print ('Error loading file ' + locusarray[i] + ' see previous line for details.  Skipping to next file.')
                    continue
                if not cmdsaveimage(locusarray[i], locusarray[0], igv):
                    usage('Problem saving snapshot of ' + locusarray[0] + ' in ' + locusarray[i] + ' see previous line for details.\nPlease confirm that the directory /autoIGV/ exists and this script has access to write to it and create subdirectories.')
                    igv.close()
                    quit()
    print ('Run completed successfully in ' + str(round(time.time() - starttime, 1)) + ' seconds.\nClosing connection with IGV...', end = '')
    igv.close()  #close the connection to IGV when done
    print ('OK\nImages saved to ' + directory + '\nGoodbye.')
    quit()
            
main()

