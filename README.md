autoIGV
=======

What is it?
-----------
AutoIGV is a python script that can take a list of target loci and BAM files and generate a folder of images based upon the target list.

How does it work?
-----------------
AutoIGV communicates with IGV over a network socket connection.  By default, IGV uses port 60151 for communication.  You may have to enable communication over this port in IGV by going to View>Preferences>Advanced and making sure that the box is checked next to Enable port and 60151 is set.

How do I create a list of targets?
----------------------------------
A target list is simply a tab-delimited text file with the first column containing some genomic locus formatted as chromosome:position (such as 1:39823765).  There can be an unlimited number of additional entries on the same line, with each additional entry containing the absolute path for a BAM file of interest.  AutoIGV will pull up that locus in the BAM file of interest and snap an image according to your settings (more on those settings in a later section).  For simplicity, it is allowed to have blank columns, and autoIGV will just skip over them (this is handy if you are creating your list using a spreadsheet editor and want to fill each column and then delete different columns on each line later).  If you are editing your sheet in Microsoft Excel, please ensure that the file is saved as tab-delimited text.

How do I get it working?
------------------------
This program is designed to run using python3.  It will generally not work using python2.  To begin using this program, copy the raw code for the most current version into a new folder (I will assume the name of the folder is autoIGV).  This is also a good opportunity to upgrade to the latest version of IGV, as some older versions of the program (versions from before 2015) may have a bug that prevents them from working with autoIGV.  Once the program is copied into that folder, you will need to create a target list as shown in the previous section.  **IGV must be opened before starting autoIGV** as autoIGV tests its connection to IGV before beginning its run and will quit if it cannot connect. 

With your initial run, you will also be required to set certain default options for the program.  This will allow you to keep your command lines short in the future.  Generally the default options should work "out of the box" with the exception of the genome (the default is hg19, and may be set to hg38 in a future release).  Your initial commandline should look like this:

     python3 autoIGV.py -f targetList.txt
 
The program will then ask you some questions to set your defaults.  Most of these settings will be the same for everybody, but be sure to pick the genome you intend to use the most often for your default.

**You should also ensure that your system is set to not sleep if your run might take more than a few minutes.**  This is because when your computer goes to sleep, it will suspend both autoIGV and IGV, breaking the communication between the two.  This will result in autoIGV quitting with a communication lost error and your run will be incomplete.

What are the command options for this program?
----------------------------------------------
There is only one non-optional parameter in autoIGV: you *absolutely* must pass it a list of targets with every run.  This argument is passed under the -f option (as shown above).  Here is a list of possible commandline options:

Option | Function
-------|---------
-f     | Target file
-d     | Output directory
-p     | Specify an alternate preference file
-g     | Specify a genome to use
-o     | Specify a host IP address
-r     | Specify a port to use
-m     | Specify imaging mode (see below)
--nocollapse | Do not collapse images

####Setting the imaging mode (useful in a bash script)####
Mode | Function
-----|----------
1    | Stack shot: Image the whole line's BAM files in a single shot
2    | Single shot: Image each BAM file on the line individually
3    | Both:  Generate both single and stack shots for each line

As mentioned above, only the -f option must be passed.  All other options can either be taken from the default preferences file or will can be set by the user during the run.

Common questions/problems
-------------------------
####It's just not working####
- Read your error messages to be sure that autoIGV is seeing a valid target list file

- If the program is quitting with a syntax error (especially one showing an error for a *print* statement with **end = ''** involved), you are most likely trying to run this through a python2 interpreter.  Please switch to a python3 interpreter and it should work.

- If the program is quitting due it being unable to connect to IGV, please be sure that IGV is currently running on your system.

- If the program is quitting due to being unable to connect to IGV, but IGV is currently running, please check the **View>Preferences>Advanced** menu and verify that the box next to the *Port* option is checked.  Also verify that it is currently set to **60151** in both your autoIGV options and in the IGV menu itself.  If you are using an alternative port, your port number will be different, but must be the same in both autoIGV and IGV.

- If you have checked all of that and still have communication errors, please ensure that you do not have any settings on your computer's firewall or iptables that might be interfering with traffic using the loopback interface (and that you have the loopback interface set correctly if you are using an IP address).

- If it is starting to run without trouble, but you are getting some unexpected behavior related to saving files, you may need to update to the most current version of IGV.  There is a known bug in older versions where it required a filename to be passed in quotes over the network port, but failed to strip off those quotes.  This can result in things such as files being saved with quotes in their name or the program returning an error that looks something like ** .png' is not a valid file format**.  If you get errors of this kind, please update to the latest version of IGV available from the Broad Institute. 

####It quit in the middle with a communication error####
This is generally caused by one of two things:
- IGV encoutered an error and froze/crashed/otherwise failed to respond to a request.  Is it overrunning its memory limit due to excessive data or being told to load corrupted data?

- The computer went into sleep mode and IGV stopped responding due to that.  Try adjusting your power settings.  On Apple systems, you can install an app called Caffeine from the app store (free as of this writing) that will allow you to set your system to not sleep.

####Can I do [something not currently supported] with this program?####
Obviously not right now :)

I will come back to this program and make updates when they are wanted or needed.  I would be happy to add your desired functionality, provided that IGV can support taking it as a command over the port (it cannot do this for every command).

####Can I control IGV on someone else's computer with autoIGV?###
In theory, yes.  If your network will allow the traffic between the two computers and their computer does not filter it out, you might be able to control IGV on someone else's computer.  I have not tested this functionality myself, so I cannot promise it works.  Also, I hope you have their permission to control their instance of IGV.

####The source code seems unusually long####
Along with serving as a potentially useful program, autoIGV is also sometimes used as a teaching program.  It is designed to teach students how to set up a low-level network socket connection.  It was not, however, designed with the assumption that the students are already comfortable with object-oriented python.  The result of avoiding the use of object-oriented python as much as possible (as well as adding copious comments) here is why it seems unusually long.

####I have other questions/requests####
Feel free to email me.  My email address is [my first name].[my last name]@ucla.edu.  If you don't already know my first name and last name, you should be able to figure it out from my github account.
