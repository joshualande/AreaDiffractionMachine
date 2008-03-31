#/*##########################################################################
# Copyright (C) 2004-2006 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem to you.
#############################################################################*/
"""
    EdfFile.py
    Generic class for Edf files manipulation.    

    Interface:
    ===========================
    class EdfFile:          
        __init__(self,FileName)	
        GetNumImages(self)
        def GetData(self,Index, DataType="",Pos=None,Size=None):
        GetPixel(self,Index,Position)
        GetHeader(self,Index)
        GetStaticHeader(self,Index)
        WriteImage (self,Header,Data,Append=1,DataType="",WriteAsUnsigened=0,ByteOrder="")


    Edf format assumptions:
    ===========================
    The following details were assumed for this implementation:
    - Each Edf file contains a certain number of data blocks.
    - Each data block represents data stored in an one, two or three-dimensional array.
    - Each data block contains a header section, written in ASCII, and a data section of
      binary information.
    - The size of the header section in bytes is a multiple of 1024. The header is
      padded with spaces (0x20). If the header is not padded to a multiple of 1024,
      the file is recognized, but the output is always made in this format.
    - The header section starts by '{' and finishes by '}'. It is composed by several
      pairs 'keyword = value;'. The keywords are case insensitive, but the values are case
      sensitive. Each pair is put in a new line (they are separeted by 0x0A). In the
      end of each line, a semicolon (;) separes the pair of a comment, not interpreted.
      Exemple:
        {
        ; Exemple Header
        HeaderID = EH:000001:000000:000000    ; automatically generated
        ByteOrder = LowByteFirst              ; 
        DataType = FloatValue                 ; 4 bytes per pixel
        Size = 4000000                        ; size of data section
        Dim_1= 1000                           ; x coordinates
        Dim_2 = 1000                          ; y coordinates
        
        (padded with spaces to complete 1024 bytes)
        }
    - There are some fields in the header that are required for this implementation. If any of
      these is missing, or inconsistent, it will be generated an error:
        Size: Represents size of data block
        Dim_1: size of x coordinates (Dim_2 for 2-dimentional images, and also Dim_3 for 3d)
        DataType
        ByteOrder
    - For the written images, these fields are automatically genereted:
        Size,Dim_1 (Dim_2 and Dim_3, if necessary), Byte Order, DataType, HeaderID and Image
      These fields are called here "static header", and can be retrieved by the method
      GetStaticHeader. Other header components are taken by GetHeader. Both methods returns
      a dictionary in which the key is the keyword of the pair. When writting an image through
      WriteImage method, the Header parameter should not contain the static header information,
      which is automatically generated.
    - The indexing of images through these functions is based just on the 0-based position in
      the file, the header items HeaderID and Image are not considered for referencing the
      images.
    - The data section contais a number of bytes equal to the value of Size keyword. Data
      section is going to be translated into an 1D, 2D or 3D Numaric Array, and accessed
      through GetData method call.      


    IMPORTANT - READ THIS
    ===========================
    If you are going to use EdfFile, you have to care about the type of your data.
    The EdfFile class stores data in a Numeric Python array, very efficient
    way for doing matrix operations.

    However, for an unknow reason (to us), Numeric Python doesn't handle the following
    types:
    - unsigned short
    - unsigned integer
    - unsigned long
    Which are supported by Edf file specification.
    So if you use these formats, pay attention to the type parameters when reading
    from or writing to a file (when using other Edf types, the convertions are direct,
    and you don't need to mention the type, unless you really want to change it).

    By default, if no type is mentioned, the EdfFile class stores, when reading a file:
    - UnsignedShort data into an short array
    - UnsignedInteger data into an integer array
    - UnsignedLong data into a long array

    This keeps the size of storage in memory, but can imply in loss of information.

    Taking "unsigned short" as an exemple:
    1) Supposing you get data with: "array=obj.GetData(0)", this array is going to be
       created as signed short. If you write it then as: 'obj2.WriteImage({},array)',
       the edf image created is going to be of signed short type, different from the
       original. To save in the same way as the former image, you must be explicit
       about the data type: 'obj2.WriteImage({},array,DataType="UnsignedShort")'
    2) If you intend to make operations, or even just read properly the values of an
       image, you should read this image as 'array=obj.GetData(0),DataType="Long")'.
       This will require two times the storage space but will assure correct values.
       If you intend to save it again, you should include the correct data type you
       are saving to.
    3) When you are saving an unsigned short array into a long, float or double
       format, you should be explicit to the fact you want this array to be
       considered a signed or unsigned (through the parameter WriteAsUnsigened).
       Suppose an hexa value of FFFF in this array. This means -1 if the array
       comes from signed data, or 65535 if it cames from unsigned data. If you save
       the array as this: 'obj2.WriteImage({},array,DataType="FloatValue")' it is
       going to be considered unsigned, and a value of FFFF is going to be
       translated into a float -1. If you want to consider the array as unsigned
       you should do:
       'obj2.WriteImage({},array,DataType="FloatValue", WriteAsUnsigened=1 )'
       In this way, a FFFF value is going to be translated into a float 65535.


"""

__author__ =  'Alexandre Gobbo (gobbo@esrf.fr)'
__version__=  '$Revision: 1.5 $'

################################################################################  
import sys, string
import Numeric
import os.path , tempfile, shutil
try:
    from FastEdf import extended_fread
    CAN_USE_FASTEDF = 1
except:
    CAN_USE_FASTEDF = 0

################################################################################
# constants
HEADER_BLOCK_SIZE = 1024
STATIC_HEADER_ELEMENTS=("HeaderID","Image","ByteOrder","DataType",
                        "Dim_1","Dim_2","Dim_3",
                        "Offset_1","Offset_2","Offset_3",
                        "Size")
STATIC_HEADER_ELEMENTS_CAPS=("HEADERID","IMAGE","BYTEORDER","DATATYPE",
                             "DIM_1","DIM_2","DIM_3",
                             "OFFSET_1","OFFSET_2","OFFSET_3",
                             "SIZE")

LOWER_CASE=0
UPPER_CASE=1

KEYS=1
VALUES=2

###############################################################################
class Image:
    """
    """
    def __init__(self):
        """ Constructor
        """
        self.Header={}
        self.StaticHeader={}
        self.HeaderPosition=0
        self.DataPosition=0
        self.Size=0
        self.NumDim=1
        self.Dim1=0
        self.Dim2=0
        self.Dim3=0
        self.DataType=""
        #for i in STATIC_HEADER_ELEMENTS: self.StaticHeader[i]=""
   
################################################################################

class  EdfFile:    
    """
    """
    ############################################################################
    #Interface
    def __init__(self,FileName,fastedf=None):
        """ Constructor
            FileName:   Name of the file (either existing or to be created)  
        """
        self.Images=[]
        self.NumImages=0
        self.FileName=FileName
        self.File = 0
        if fastedf is None:fastedf=0
        self.fastedf=fastedf
        
        if sys.byteorder=="big": self.SysByteOrder="HighByteFirst"
        else: self.SysByteOrder="LowByteFirst"
        
        try:
            if os.path.isfile(self.FileName)==0:                
                self.File = open(self.FileName, "wb")
                self.File.close()    

            if (os.access(self.FileName,os.W_OK)):
                self.File=open(self.FileName, "r+b")
            else : 
                self.File=open(self.FileName, "rb")

            self.File.seek(0, 0)
        except:
            try:
                self.File.close()
            except:
                pass
            raise "EdfFile: Error opening file"

        self.File.seek(0, 0)
        
        Index=0
        line = self.File.readline()        
        while line != "":            
            if string.count(line, "{\n") >= 1 or string.count(line, "{\r\n")>=1:
                Index=self.NumImages
                self.NumImages = self.NumImages + 1                
                self.Images.append(Image())
                self.Images[Index].HeaderPosition=self.File.tell()    
                
            if string.count(line, "=") >= 1:
                listItems = string.split(line, "=", 1)
                typeItem = string.strip(listItems[0])
                listItems = string.split(listItems[1], ";", 1)
                valueItem = string.strip(listItems[0])

                #if typeItem in self.Images[Index].StaticHeader.keys():          
                if (string.upper(typeItem)) in STATIC_HEADER_ELEMENTS_CAPS:          
                    self.Images[Index].StaticHeader[typeItem]=valueItem                    
                else:
                    self.Images[Index].Header[typeItem]=valueItem
            if string.count(line, "}\n") >= 1:
                #for i in STATIC_HEADER_ELEMENTS_CAPS:
                #    if self.Images[Index].StaticHeader[i]=="":
                #        raise "Bad File Format"
                self.Images[Index].DataPosition=self.File.tell()
                #self.File.seek(string.atoi(self.Images[Index].StaticHeader["Size"]), 1)
                StaticPar = SetDictCase(self.Images[Index].StaticHeader,UPPER_CASE,KEYS)
                if "SIZE" in StaticPar.keys():
                    self.Images[Index].Size = string.atoi(StaticPar["SIZE"])
                    if self.Images[Index].Size <= 0:
                        self.NumImages = Index
                        line = self.File.readline()
                        continue
                else:
                    raise "EdfFile: Image doesn't have size information"                
                if "DIM_1" in StaticPar.keys():
                    self.Images[Index].Dim1 = string.atoi(StaticPar["DIM_1"])
                    self.Images[Index].Offset1 = string.atoi(\
                                            StaticPar.get("Offset_1","0"))
                else:
                    raise "EdfFile: Image doesn't have dimension information"
                if "DIM_2" in StaticPar.keys():
                    self.Images[Index].NumDim=2
                    self.Images[Index].Dim2 = string.atoi(StaticPar["DIM_2"])
                    self.Images[Index].Offset2 = string.atoi(\
                                            StaticPar.get("Offset_2","0"))
                if "DIM_3" in StaticPar.keys():
                    self.Images[Index].NumDim=3
                    self.Images[Index].Dim3 = string.atoi(StaticPar["DIM_3"])
                    self.Images[Index].Offset3 = string.atoi(\
                                            StaticPar.get("Offset_3","0"))
                if "DATATYPE" in StaticPar.keys():
                    self.Images[Index].DataType=StaticPar["DATATYPE"]
                else:
                    raise "EdfFile: Image doesn't have datatype information"
                if "BYTEORDER" in StaticPar.keys():
                    self.Images[Index].ByteOrder=StaticPar["BYTEORDER"]
                else:
                    raise "EdfFile: Image doesn't have byteorder information"
                    

                                
                self.File.seek(self.Images[Index].Size, 1)
                
            line = self.File.readline()
    
        
    def GetNumImages(self):
        """ Returns number of images of the object (and associated file)
        """
        return self.NumImages

        
    
    def GetData(self,Index, DataType="",Pos=None,Size=None):
        """ Returns numeric array with image data
            Index:          The zero-based index of the image in the file
            DataType:       The edf type of the array to be returnd
                            If ommited, it is used the default one for the type
                            indicated in the image header
                            Attention to the absence of UnsignedShort,
                            UnsignedInteger and UnsignedLong types in
                            Numeric Python
                            Default relation between Edf types and NumPy's typecodes:
                                SignedByte          1
                                UnsignedByte        b       
                                SignedShort         s
                                UnsignedShort       w
                                SignedInteger       i
                                UnsignedInteger     u
                                SignedLong          l
                                UnsignedLong        u
                                FloatValue          f
                                DoubleValue         d
            Pos:            Tuple (x) or (x,y) or (x,y,z) that indicates the begining
                            of data to be read. If ommited, set to the origin (0),
                            (0,0) or (0,0,0)
            Size:           Tuple, size of the data to be returned as x) or (x,y) or
                            (x,y,z) if ommited, is the distance from Pos to the end.

            If Pos and Size not mentioned, returns the whole data.                         
        """
        fastedf = self.fastedf
        if Index < 0 or Index >= self.NumImages: raise "EdfFile: Index out of limit"
        if fastedf is None:fastedf = 0
        if Pos is None and Size is None:
            self.File.seek(self.Images[Index].DataPosition,0)
            datatype = self.__GetDefaultNumericType__(self.Images[Index].DataType)
            if   datatype in [1, "1", "b"]:         datasize = 1
            elif datatype in ["s", "w"]:            datasize = 2
            elif datatype in ["i", "u", "l", "f"]:
                #I assume 32 bit because longs are 8 bit in 64 bit machines  
                datasize = 4
            else:datasize = 8
            if self.Images[Index].NumDim==3:
                sizeToRead = self.Images[Index].Dim1 * \
                             self.Images[Index].Dim2 * \
                             self.Images[Index].Dim3 * datasize
                Data = Numeric.fromstring(self.File.read(sizeToRead),
                            datatype)
                Data = Numeric.reshape(Data, (self.Images[Index].Dim3,self.Images[Index].Dim2, self.Images[Index].Dim1))
            elif self.Images[Index].NumDim==2:
                sizeToRead = self.Images[Index].Dim1 * \
                             self.Images[Index].Dim2 * datasize
                Data = Numeric.fromstring(self.File.read(sizeToRead),
                            datatype)
                #print "Data.type = ", Data.typecode()
                #print "self.Images[Index].DataType ", self.Images[Index].DataType
                #print Data.shape
                #print sizeToRead
                #print len(Data)
                Data = Numeric.reshape(Data, (self.Images[Index].Dim2, self.Images[Index].Dim1))
        elif fastedf and CAN_USE_FASTEDF:
            type= self.__GetDefaultNumericType__(self.Images[Index].DataType)
            size_pixel=self.__GetSizeNumericType__(type)
            Data=Numeric.array([],type)
            if self.Images[Index].NumDim==1:
                if Pos==None: Pos=(0,)
                if Size==None: Size=(0,)
                sizex=self.Images[Index].Dim1
                Size=list(Size)                
                if Size[0]==0:Size[0]=sizex-Pos[0]
                self.File.seek((Pos[0]*size_pixel)+self.Images[Index].DataPosition,0)
                Data = Numeric.fromstring(self.File.read(Size[0]*size_pixel), type)
            elif self.Images[Index].NumDim==2:                
                if Pos==None: Pos=(0,0)
                if Size==None: Size=(0,0)
                Size=list(Size)
                sizex,sizey=self.Images[Index].Dim1,self.Images[Index].Dim2
                if Size[0]==0:Size[0]=sizex-Pos[0]
                if Size[1]==0:Size[1]=sizey-Pos[1]
                Data=Numeric.zeros([Size[1],Size[0]],type)
                self.File.seek((((Pos[1]*sizex)+Pos[0])*size_pixel)+self.Images[Index].DataPosition,0)
                extended_fread(Data, Size[0]*size_pixel , Numeric.array([Size[1]]), Numeric.array([sizex*size_pixel]) ,self.File)

            elif self.Images[Index].NumDim==3:
                if Pos==None: Pos=(0,0,0)
                if Size==None: Size=(0,0,0)
                Size=list(Size)
                sizex,sizey,sizez=self.Images[Index].Dim1,self.Images[Index].Dim2,self.Images[Index].Dim3
                if Size[0]==0:Size[0]=sizex-Pos[0]
                if Size[1]==0:Size[1]=sizey-Pos[1]
                if Size[2]==0:Size[2]=sizez-Pos[2]
                Data=Numeric.zeros([Size[2],Size[1],Size[0]],type)
                self.File.seek(((((Pos[2]*sizey+Pos[1])*sizex)+Pos[0])*size_pixel)+self.Images[Index].DataPosition,0)
                extended_fread(Data, Size[0]*size_pixel , Numeric.array([Size[2],Size[1]]),
                        Numeric.array([ sizey*sizex*size_pixel , sizex*size_pixel]) ,self.File)

        else:
            if fastedf:print "I could not use fast routines"
            type= self.__GetDefaultNumericType__(self.Images[Index].DataType)
            size_pixel=self.__GetSizeNumericType__(type)
            Data=Numeric.array([],type)
            if self.Images[Index].NumDim==1:
                if Pos==None: Pos=(0,)
                if Size==None: Size=(0,)
                sizex=self.Images[Index].Dim1
                Size=list(Size)                
                if Size[0]==0:Size[0]=sizex-Pos[0]
                self.File.seek((Pos[0]*size_pixel)+self.Images[Index].DataPosition,0)
                Data = Numeric.fromstring(self.File.read(Size[0]*size_pixel), type)
            elif self.Images[Index].NumDim==2:                
                if Pos==None: Pos=(0,0)
                if Size==None: Size=(0,0)
                Size=list(Size)
                sizex,sizey=self.Images[Index].Dim1,self.Images[Index].Dim2
                if Size[0]==0:Size[0]=sizex-Pos[0]
                if Size[1]==0:Size[1]=sizey-Pos[1]
                #print len(range(Pos[1],Pos[1]+Size[1])), "LECTURES OF ", Size[0], "POINTS"
                #print "sizex = ", sizex, "sizey = ", sizey
                Data = Numeric.zeros((Size[1],Size[0]), type)
                dataindex =0
                for y in range(Pos[1],Pos[1]+Size[1]):
                    self.File.seek((((y*sizex)+Pos[0])*size_pixel)+self.Images[Index].DataPosition,0)
                    line = Numeric.fromstring(self.File.read(Size[0]*size_pixel), type)
                    Data[dataindex,:] =  line[:]
                    #Data=Numeric.concatenate((Data,line))
                    dataindex += 1
                #print "DataSize = ",Data.shape
                #print "Requested reshape = ",Size[1],'x',Size[0]
                #Data = Numeric.reshape(Data, (Size[1],Size[0]))                            
            elif self.Images[Index].NumDim==3:
                if Pos==None: Pos=(0,0,0)
                if Size==None: Size=(0,0,0)
                Size=list(Size)
                sizex,sizey,sizez=self.Images[Index].Dim1,self.Images[Index].Dim2,self.Images[Index].Dim3
                if Size[0]==0:Size[0]=sizex-Pos[0]
                if Size[1]==0:Size[1]=sizey-Pos[1]
                if Size[2]==0:Size[2]=sizez-Pos[2]
                for z in range(Pos[2],Pos[2]+Size[2]):
                    for y in range(Pos[1],Pos[1]+Size[1]):
                        self.File.seek(((((z*sizey+y)*sizex)+Pos[0])*size_pixel)+self.Images[Index].DataPosition,0)
                        line = Numeric.fromstring(self.File.read(Size[0]*size_pixel), type)
                        Data=Numeric.concatenate((Data,line))                
                Data = Numeric.reshape(Data, (Size[2],Size[1],Size[0]))

        if string.upper(self.SysByteOrder)!=string.upper(self.Images[Index].ByteOrder):
            Data=Data.byteswapped()
        if DataType != "":
            Data=self.__SetDataType__ (Data,DataType)
        return Data



    def GetPixel(self,Index, Position):
        """ Returns double value of the pixel, regardless the format of the array
            Index:      The zero-based index of the image in the file
            Position:   Tuple with the coordinete (x), (x,y) or (x,y,z)
        """
        if Index < 0 or Index >= self.NumImages: raise "EdfFile: Index out of limit"
        if len(Position)!= self.Images[Index].NumDim: raise "EdfFile: coordinate with wrong dimension "
        
        size_pixel=self.__GetSizeNumericType__(self.__GetDefaultNumericType__(self.Images[Index].DataType))
        offset=Position[0]*size_pixel
        if self.Images[Index].NumDim>1:
            size_row=size_pixel * self.Images[Index].Dim1
            offset=offset+ (Position[1]* size_row)
            if self.Images[Index].NumDim==3:
                size_img=size_row * self.Images[Index].Dim2
                offset=offset+ (Position[2]* size_img)
        self.File.seek(self.Images[Index].DataPosition + offset,0)
        Data = Numeric.fromstring(self.File.read(size_pixel), self.__GetDefaultNumericType__(self.Images[Index].DataType))
        if string.upper(self.SysByteOrder)!=string.upper(self.Images[Index].ByteOrder):
            Data=Data.byteswapped() 
        Data=self.__SetDataType__ (Data,"DoubleValue")
        return Data[0]
         
        
    def GetHeader(self,Index):
        """ Returns dictionary with image header fields.
            Does not include the basic fields (static) defined by data shape, 
            type and file position. These are get with GetStaticHeader
            method.
            Index:          The zero-based index of the image in the file
        """
        if Index < 0 or Index >= self.NumImages: raise "Index out of limit"
        #return self.Images[Index].Header
        ret={}
        for i in self.Images[Index].Header.keys():
            ret[i]=self.Images[Index].Header[i]        
        return ret

        
    def GetStaticHeader(self,Index):
        """ Returns dictionary with static parameters
            Data format and file position dependent information
            (dim1,dim2,size,datatype,byteorder,headerId,Image)
            Index:          The zero-based index of the image in the file
        """ 
        if Index < 0 or Index >= self.NumImages: raise "Index out of limit"
        #return self.Images[Index].StaticHeader
        ret={}
        for i in self.Images[Index].StaticHeader.keys():
            ret[i]=self.Images[Index].StaticHeader[i]        
        return ret


    def WriteImage (self,Header,Data,Append=1,DataType="",ByteOrder=""):
        """ Writes image to the file. 
            Header:         Dictionary containing the non-static header
                            information (static information is generated
                            according to position of image and data format
            Append:         If equals to 0, overwrites the file. Otherwise, appends
                            to the end of the file
            DataType:       The data type to be saved to the file:
                                SignedByte          
                                UnsignedByte               
                                SignedShort         
                                UnsignedShort       
                                SignedInteger       
                                UnsignedInteger     
                                SignedLong          
                                UnsignedLong        
                                FloatValue          
                                DoubleValue         
                            Default: according to Data array typecode:
                                    1:  SignedByte
                                    b:  UnsignedByte
                                    s:  SignedShort       
				    w:  UnsignedShort
                                    i:  SignedInteger
                                    l:  SignedLong          
				    u:  UnsignedLong
                                    f:  FloatValue       
                                    d:  DoubleValue
            ByteOrder:      Byte order of the data in file:
                                HighByteFirst
                                LowByteFirst
                            Default: system's byte order
        """
        if Append==0:
            self.File.truncate(0)
            self.Images=[]
            self.NumImages=0
        Index=self.NumImages
        self.NumImages = self.NumImages + 1                
        self.Images.append(Image())

        #self.Images[Index].StaticHeader["Dim_1"] = "%d" % Data.shape[1]
        #self.Images[Index].StaticHeader["Dim_2"] = "%d" % Data.shape[0]
        if len(Data.shape)==1:
            self.Images[Index].Dim1=Data.shape[0]
            self.Images[Index].StaticHeader["Dim_1"] = "%d" % self.Images[Index].Dim1
            self.Images[Index].Size=(Data.shape[0]*self.__GetSizeNumericType__(Data.typecode()))
        elif len(Data.shape)==2:
            self.Images[Index].Dim1=Data.shape[1]
            self.Images[Index].Dim2=Data.shape[0]
            self.Images[Index].StaticHeader["Dim_1"] = "%d" % self.Images[Index].Dim1
            self.Images[Index].StaticHeader["Dim_2"] = "%d" % self.Images[Index].Dim2
            self.Images[Index].Size=(Data.shape[0]*Data.shape[1]*self.__GetSizeNumericType__(Data.typecode()))
            self.Images[Index].NumDim=2
        elif len(Data.shape)==3:
            self.Images[Index].Dim1=Data.shape[2]
            self.Images[Index].Dim2=Data.shape[1]
            self.Images[Index].Dim3=Data.shape[0]
            self.Images[Index].StaticHeader["Dim_1"] = "%d" % self.Images[Index].Dim1
            self.Images[Index].StaticHeader["Dim_2"] = "%d" % self.Images[Index].Dim2
            self.Images[Index].StaticHeader["Dim_3"] = "%d" % self.Images[Index].Dim3
            self.Images[Index].Size=(Data.shape[0]*Data.shape[1]*Data.shape[2]*self.__GetSizeNumericType__(Data.typecode()))
            self.Images[Index].NumDim=3
        elif len(Data.shape)>3:
            raise "EdfFile: Data dimension not suported"
        

        if DataType=="":
            self.Images[Index].DataType=self.__GetDefaultEdfType__(Data.typecode())
        else:
            self.Images[Index].DataType=DataType
            Data=self.__SetDataType__ (Data,DataType)
                            
        if ByteOrder=="":
            self.Images[Index].ByteOrder=self.SysByteOrder
        else:
            self.Images[Index].ByteOrder=ByteOrder
                
        self.Images[Index].StaticHeader["Size"]  = "%d" % self.Images[Index].Size
        self.Images[Index].StaticHeader["Image"] = Index+1
        self.Images[Index].StaticHeader["HeaderID"] = "EH:%06d:000000:000000" % self.Images[Index].StaticHeader["Image"]
        self.Images[Index].StaticHeader["ByteOrder"]=self.Images[Index].ByteOrder
        self.Images[Index].StaticHeader["DataType"]=self.Images[Index].DataType

        
        self.Images[Index].Header={}            
        self.File.seek(0,2)
        StrHeader = "{\n"
        for i in STATIC_HEADER_ELEMENTS:
            if i in self.Images[Index].StaticHeader.keys():
                StrHeader = StrHeader + ("%s = %s ;\n" % (i , self.Images[Index].StaticHeader[i]))
        for i in Header.keys():
            StrHeader = StrHeader + ("%s = %s ;\n" % (i,Header[i]))
            self.Images[Index].Header[i]=Header[i]
        newsize=(((len(StrHeader)+1)/HEADER_BLOCK_SIZE)+1)*HEADER_BLOCK_SIZE -2                   
        StrHeader = string.ljust(StrHeader,newsize)
        StrHeader = StrHeader+"}\n"

        self.Images[Index].HeaderPosition=self.File.tell()    
        self.File.write(StrHeader)
        self.Images[Index].DataPosition=self.File.tell()

        #if self.Images[Index].StaticHeader["ByteOrder"] != self.SysByteOrder:
        if string.upper(self.Images[Index].ByteOrder) != string.upper(self.SysByteOrder):
            self.File.write((Data.byteswapped()).tostring())  
        else:
            self.File.write(Data.tostring())
        
        

    ############################################################################
    #Internal Methods
        
    def __GetDefaultNumericType__(self, EdfType):
        """ Internal method: returns NumPy type according to Edf type
        """
        return GetDefaultNumericType(EdfType)

    def __GetDefaultEdfType__(self, NumericType):
        """ Internal method: returns Edf type according Numpy type
        """
        if  NumericType  == "1":            return "SignedByte"
        elif NumericType == "b":            return "UnsignedByte"
        elif NumericType == "s":            return "SignedShort"          
        elif NumericType == "w":            return "UnsignedShort"          
        elif NumericType == "i":            return "SignedInteger"  
        elif NumericType == "l":            return "SignedLong"           
	elif NumericType == "u":	    return "UnsignedLong"
        elif NumericType == "f":            return "FloatValue"         
        elif NumericType == "d":            return "DoubleValue"
        else: raise "__GetDefaultEdfType__: unknown NumericType"


    def __GetSizeNumericType__(self, NumericType):
        """ Internal method: returns size of NumPy's Array Types
        """
        if  NumericType  == "1":            return 1
        elif NumericType == "b":            return 1
        elif NumericType == "s":            return 2         
	elif NumericType == "w":	    return 2
        elif NumericType == "i":            return 4  
        elif NumericType == "l":            return 4           
        elif NumericType == "u":	    return 4
        elif NumericType == "f":            return 4         
        elif NumericType == "d":            return 8
        else: raise "__GetSizeNumericType__: unknown NumericType"


    def __SetDataType__ (self,Array,DataType):
        """ Internal method: array type convertion
        """
        FromEdfType= Array.typecode()
        ToEdfType= self.__GetDefaultNumericType__(DataType)
        if ToEdfType != FromEdfType:
            aux=Array.astype(self.__GetDefaultNumericType__(DataType))    
            return aux
        return Array

    def __del__(self):
        try:
            self.File.close()
        except:
            pass
        

def GetDefaultNumericType(EdfType):
    """ Returns NumPy type according Edf type
    """
    EdfType=string.upper(EdfType)
    if   EdfType == "SIGNEDBYTE":       return "1"
    elif EdfType == "UNSIGNEDBYTE":     return "b"       
    elif EdfType == "SIGNEDSHORT":      return "s"
    elif EdfType == "UNSIGNEDSHORT":    return "w"
    elif EdfType == "SIGNEDINTEGER":    return "i"
    elif EdfType == "UNSIGNEDINTEGER":  return "u"
    elif EdfType == "SIGNEDLONG":       return "l"
    elif EdfType == "UNSIGNEDLONG":     return "u"
    elif EdfType == "FLOATVALUE":       return "f"
    elif EdfType == "FLOAT":            return "f"
    elif EdfType == "DOUBLEVALUE":      return "d"
    else: raise "__GetDefaultNumericType__: unknown EdfType"


def SetDictCase(Dict, Case, Flag):
    """ Returns dictionary with keys and/or values converted into upper or lowercase
        Dict:   input dictionary
        Case:   LOWER_CASE, UPPER_CASE
        Flag:   KEYS, VALUES or KEYS | VALUES        
    """
    newdict={}
    for i in Dict.keys():
        newkey=i
        newvalue=Dict[i]
        if Flag & KEYS:
            if Case == LOWER_CASE:  newkey = string.lower(newkey)
            else:                   newkey = string.upper(newkey)
        if Flag & VALUES:
            if Case == LOWER_CASE:  newvalue = string.lower(newvalue)
            else:                   newvalue = string.upper(newvalue)
        newdict[newkey]=newvalue
    return newdict    


def GetRegion(Arr,Pos,Size):
    """Returns array with refion of Arr.
       Arr must be 1d, 2d or 3d
       Pos and Size are tuples in the format (x) or (x,y) or (x,y,z)
       Both parameters must have the same size as the dimention of Arr
    """
    Dim=len(Arr.shape)
    if len(Pos) != Dim:  return None
    if len(Size) != Dim: return None
    
    if (Dim==1):
        SizeX=Size[0]
        if SizeX==0: SizeX=Arr.shape[0]-Pos[0]
        ArrRet=Numeric.take(Arr, range(Pos[0],Pos[0]+SizeX))
    elif (Dim==2):
        SizeX=Size[0]
        SizeY=Size[1]
        if SizeX==0: SizeX=Arr.shape[1]-Pos[0]
        if SizeY==0: SizeY=Arr.shape[0]-Pos[1]
        ArrRet=Numeric.take(Arr, range(Pos[1],Pos[1]+SizeY))
        ArrRet=Numeric.take(ArrRet, range(Pos[0],Pos[0]+SizeX),1)
    elif (Dim==3):
        SizeX=Size[0]
        SizeY=Size[1]
        SizeZ=Size[2]
        if SizeX==0: SizeX=Arr.shape[2]-Pos[0]
        if SizeY==0: SizeX=Arr.shape[1]-Pos[1]
        if SizeZ==0: SizeZ=Arr.shape[0]-Pos[2]
        ArrRet=Numeric.take(Arr, range(Pos[2],Pos[2]+SizeZ))
        ArrRet=Numeric.take(ArrRet, range(Pos[1],Pos[1]+SizeY),1)
        ArrRet=Numeric.take(ArrRet, range(Pos[0],Pos[0]+SizeX),2)
    else:
        ArrRet=None
    return ArrRet

#EXEMPLE CODE:        
if __name__ == "__main__":
    if 1:
        a = Numeric.zeros((5, 10))
        for i in range(5):
            for j in range(10):
                 a[i,j] = 10*i + j 
        edf = EdfFile("armando.edf")
        edf.WriteImage({},a)
        del edf #force to close the file
        inp = EdfFile("armando.edf")
        b = inp.GetData(0)
        out = EdfFile("armando2.edf")
        out.WriteImage({}, b)
        del out #force to close the file
        inp2 = EdfFile("armando2.edf")
        c = inp2.GetData(0)
        print "A SHAPE = ", a.shape
        print "B SHAPE = ", b.shape
        print "C SHAPE = ", c.shape
        for i in range(5):
            print "A", a[i,:]
            print "B", b[i,:]
            print "C", c[i,:]
        sys.exit(0)
    
    #Creates object based on file exe.edf
    exe=EdfFile("images/test_image.edf")
    x=EdfFile("images/test_getdata.edf")
    #Gets unsigned short data, storing in an signed long
    arr=exe.GetData(0,Pos=(100,200),Size=(200,400))
    x.WriteImage({},arr,0)

    arr=exe.GetData(0,Pos=(100,200))
    x.WriteImage({},arr)

    arr=exe.GetData(0,Size=(200,400))
    x.WriteImage({},arr)

    arr=exe.GetData(0)
    x.WriteImage({},arr)
    
    sys.exit()
        
    #Creates object based on file exe.edf
    exe=EdfFile("images/.edf")

    #Creates long array , filled with 0xFFFFFFFF(-1)
    la=Numeric.zeros((100,100))
    la=la-1
    
    #Creates a short array, filled with 0xFFFF
    sa=Numeric.zeros((100,100))
    sa=sa+0xFFFF
    sa=sa.astype("s")

    #Writes long array, initializing file (append=0)
    exe.WriteImage({},la,0,"")
    
    #Appends short array with new header items
    exe.WriteImage({'Name': 'Alexandre', 'Date': '16/07/2001'},sa)    

    #Appends short array, in Edf type unsigned
    exe.WriteImage({},sa,DataType="UnsignedShort")    

    #Appends short array, in Edf type unsigned
    exe.WriteImage({},sa,DataType="UnsignedLong")    

    #Appends long array as a double, considering unsigned
    exe.WriteImage({},la,DataType="DoubleValue",WriteAsUnsigened=1)

    #Gets unsigned short data, storing in an signed long
    ushort=exe.GetData(2,"SignedLong")

    #Makes an operation
    ushort=ushort-0x10

    #Saves Result as signed long
    exe.WriteImage({},ushort)

    #Saves in the original format (unsigned short)
    OldHeader=exe.GetStaticHeader(2)
    exe.WriteImage({},ushort,1,OldHeader["DataType"] )

