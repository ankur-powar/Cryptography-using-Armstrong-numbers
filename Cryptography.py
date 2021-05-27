import os
import threading
import abc

class ByteManager:
    @classmethod
    def byte_to_nibbles(cls, byte):
        lower_nibble = byte & 0xF
        higher_nibble = byte >> 4
        return (higher_nibble, lower_nibble)

    @classmethod
    def nibbles_to_byte(cls, nibbles):
        return (nibbles[0] <<4) | nibbles[1]

class Level2(abc.ABC):
    def __init__(self, color):
        self.index = 0
        self.size = len(color)
        self.color = color

    @abc.abstractmethod
    def process(self, data):
        pass

class Encoder_Level2 (Level2):
    def __init__(self, color):
        Level2.__init__(self, color)

    def process(self, data):
        row, col = ByteManager.byte_to_nibbles(data)
        encoded = (self.color[self.index] + row*16 + col) % 256
        self.index = (self.index+1) % self.size
        return encoded

class Decoder_Level2(Level2):
    def __init__(self, color):
        Level2.__init__(self, color)

    def process(self, encoded):
        temp = ( encoded - self.color[self.index] + 256) %256
        row =  temp // 16
        col = temp % 16
        self.index = (self.index + 1) % self.size
        return ByteManager.nibbles_to_byte((row,col))


class ChunkProcessor:
    def __init__(self, src_file_name, trgt_file_name, start_pos, end_pos, objLevel2):
        #input data
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.objLevel2 = objLevel2

        # a thread as a member of the class
        self.thrd = threading.Thread( target= self.process)
        #activate the thread
        self.thrd.start()

    def process(self):
        #open the source file for reading
        src_handle = open(self.src_file_name, 'rb') #must exist
        # open the target file for writing
        trgt_handle = open(self.trgt_file_name, 'wb') #is created/overwritten

        #ensure that chunk is read within the limits
        src_handle.seek(self.start_pos, 0)
        x = self.start_pos
        while x < self.end_pos:
            buff = int.from_bytes(src_handle.read(1), byteorder='big')
            buff = self.objLevel2.process(buff)
            trgt_handle.write(int.to_bytes(buff, length=1, byteorder='big'))
            x+=1

        #close
        trgt_handle.close()
        src_handle.close()



class FileProcessor:
    def __init__(self, src_file_name, trgt_file_name, action):
        if not os.path.exists(src_file_name): #checks whether the file exists  or not
            raise Exception(src_file_name + ' doesnt exist!')
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name
        self.action = action

    def process(self):
        n = 4 #number of chunks
        chunks = self.divide_into_chunks(n)
        cps = []
        for ch in chunks:
            if self.action == 'E':
                objE = Encoder_Level2((226, 123, 155))
                cps.append(ChunkProcessor(self.src_file_name, ch[0], ch[1], ch[2], objE))
            elif self.action == 'D':
                objD = Decoder_Level2((226, 123, 155))
                cps.append(ChunkProcessor(self.src_file_name, ch[0], ch[1], ch[2], objD))


        #suspend this thread until chunk processors are done
        for cp in cps:
            cp.thrd.join()

        #merge into the trgt_file_name
        trgt_handle = open(self.trgt_file_name, 'wb')
        for ch in chunks:
            ch_handle = open(ch[0], 'rb')
            while True:
                buff = ch_handle.read(2048)
                if not buff:
                    break
                trgt_handle.write(buff)
            ch_handle.close()

        trgt_handle.close()


    def divide_into_chunks(self, n):
        chunks = []

        #chunk boundaries
        src_file_size = os.path.getsize(self.src_file_name)  # returns size of file in bytes, raises FileNotFoundError if file doesnt exist.
        size_of_chunk = src_file_size //n
        end = 0

        #generate the names
        tup = os.path.splitext(self.src_file_name) # returns a tuple of (parent_dir_file_name, file_ext)

        #n-1 chunks
        i =-1
        for i in range(n-1):
            start = end #0,31,62
            end = start + size_of_chunk  #31,62,93
            chunks.append( (tup[0] + str(i) + tup[1], start, end) )

        #nth chunk
        chunks.append((tup[0] + str(i+1) + tup[1], end, src_file_size))
        return chunks


def main():
    sfname = 'd:/images/kids.jpg'
    efname = 'd:/images/e_kids.jpg'
    tfname = 'd:/images/school_kids.jpg'

    #sfname = 'd:/temp/a.txt'
    #efname = 'd:/temp/e_a.txt'
    #tfname = 'd:/temp/regained_a.txt'


    fp1 = FileProcessor(sfname, efname, 'E')
    fp1.process()

    print('-------------------------')
    fp2 = FileProcessor(efname, tfname, 'D')
    fp2.process()

    #x = "Where is my Laptop?"
    #enc = Encoder_Level2((226,123,155))
    #y = ''
    #for c in x:
    #    y = y + chr(enc.process(ord(c)))
    #print(y)

    #dec = Decoder_Level2((226, 123, 155))
    #z = ''
    #for c in y:
    #    z = z + chr(dec.process(ord(c)))

    #print(z)





main()
