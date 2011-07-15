import os, re

class BootLoaderParser():
    """GRUB 2 operating systems list parser"""

    def __init__(self):
        self.results = list()

    def loadFile(self, fileName):
         """Checking and reading the file specified by input fileName"""

         if not os.path.isfile(fileName) or not os.access(fileName, os.R_OK):
            print fileName
            return os.EX_OSFILE

         # Read and close file
         fileHandler = open(fileName, "rb")
         contents = fileHandler.read()
         fileHandler.close()


         self.parseMenuList(contents)
         return self.results
        
    def parseMenuList(self, contents):
        """OS Menu parser. Always returns list even if no results."""

# There is need to implement FreeBSD, OpenBSD and NetBSD
#menuentry "Install OpenBSD from RAM disk" {
#    set root=(hd0,1)
#    kopenbsd /openbsd.rd
#  }
#
#menuentry "freebsd 8.0" {
#	set root=(hd0,2,a)
#    (freebsd|kfreebsd)	/boot/loader 
#
#    kfreebsd_loadenv         /boot/device.hints
#	set kFreeBSD.vfs.root.mountfrom=ufs:/dev/ad4s2a
#	set kFreeBSD.vfs.root.mountfrom.options=rw
#}

        contents = contents.replace("\n", "").replace("\t", " ")

        entries = re.findall("menuentry([ ]+)([\"')+])([A-Za-z0-9,\. \(\)\/_-]+)([\"')+])([A-Za-z_ 0-9\-]+){(.*?[}])", contents)
        i=0

        for entry in entries:
            if len(entry) < 2:
                continue

            Title = entry[2]

            linuxParams = re.findall('linux([ ]+)/([A-Za-z_\-0-9\./]+)([ ]+)([= A-Za-z/0-9\-]+)', entry[5])

            #freeBSDParams = re.findall('reebsd([ ]+)/([A-Za-z_\-0-9\./]+)([ ]+)([= A-Za-z0-9\-]+)', entry[5])

            if len(linuxParams) > 0:
                kernel = "/"+linuxParams[0][1] # kernel placement (example: /boot/kernel-3.0
                kernelCmdLine = linuxParams[0][3].replace(" echo ", "") # params to boot (example: root=/dev/sda1)
                osType = "Linux"
                chainloader = False
            else:
                chainloader = True # is this a redirection to another bootloader?
                kernel, kernelCmdLine = False, False
                osType = "Other/Bootloader"

            # check where is root partition containing boot image
            setRoot = re.findall('set root(.*)(/dev/|hd)([a-z0-9]+)(.*)msdos([0-9]+)', entry[5])
            if len(setRoot) == 0:
                continue

            # not a valid entry?
            if len(setRoot[0]) < 4:
                continue

            if setRoot[0][1] == "/dev/":
                partition = "/dev/"+setRoot[0][2]+str(setRoot[0][4])
            else:
                partition = "/dev/sd"+chr(int(setRoot[0][2])+97)+str(setRoot[0][4])


            # Linux's initrd
            _initrd = re.findall('initrd([ ]+)/([A-Za-z_\-0-9\./]+)', entry[5])
            if len(_initrd) > 0:
                initrd = "/"+_initrd[0][1]
            else:
                initrd = False

            i=i+1
            self.results.append({'title': Title, 'partition': partition, 'kernel': kernel, 'kernel_params': kernelCmdLine, 'kernel_type': osType, 'chainloader': chainloader, 'initrd': initrd, 'id': i})


# TEST         
#List = BootLoaderParser()
#List.loadFile("../../../grub-test.cfg")
#print List.results
