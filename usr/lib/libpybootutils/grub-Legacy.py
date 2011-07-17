import os, re, sys

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

        contents = contents.replace("\t", " ")
        splitted = contents.split("title ")

        i=0

        for entry in splitted:
            if i == 0:
                i=i+1
                continue

            end = entry.split("\n\n")
            lines = end[0].split("\n")
            chainloader = False

            Title = lines[0] # title is always at first line
            Variables = dict()

            for Line in lines:
                syntax = re.findall("([A-Za-z]+)([ ]+)(.*)", Line)

                if len(syntax) == 1:
                    if len(syntax[0]) == 3:
                        Variables[syntax[0][0]] = syntax[0][2]

            # reference to other bootloader (eg. windows bootloader)
            if Variables.has_key("chainloader"):
                chainloader = Variables['chainloader']
                kernel, kernelCmdLine = False, False
                initrd = False
                osType = "Other/Bootloader"
            else:
                if Variables.has_key("kernel"):
                    kernelTMP = re.findall("([A-Za-z0-9\/]+)([ ]+)(.*)", Variables['kernel'])

                    if len(kernelTMP) == 1:
                        if len(kernelTMP[0]) == 3:
                            osType = "Linux"
                            kernel = kernelTMP[0][0]
                            kernelCmdLine = kernelTMP[0][2]
                        else:
                            continue            
                    else:
                        continue

                    # adds initrd if present
                    if Variables.has_key("initrd"):
                        initrd = Variables['initrd']

            # get partition adress in Linux format
            if Variables.has_key("root"):
                partitionTMP = re.findall("\(hd([0-9]+),([0-9]+)\)", Variables['root'])
            elif Variables.has_key("rootnoverify"):
                partitionTMP = re.findall("\(hd([0-9]+),([0-9]+)\)", Variables['rootnoverify'])
            else:
                continue

            partition = '/dev/sd'+chr(int(partitionTMP[0][0])+97)+str(int(partitionTMP[0][1])+1)
            
            i=i+1
            self.results.append({'title': Title, 'partition': partition, 'kernel': kernel, 'kernel_params': kernelCmdLine, 'kernel_type': osType, 'chainloader': chainloader, 'initrd': initrd, 'id': i})


# TEST         
List = BootLoaderParser()
List.loadFile("../../../grub-legacy-test.lst")
print List.results
