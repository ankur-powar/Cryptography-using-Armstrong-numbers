import os
import threading

class ChunkProcessor:
    def __init__(self, src_file_name, trgt_file_name, start_pos, end_pos):
        #input data
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name
        self.start_pos = start_pos
        self.end_pos = end_pos

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
            1024 * 1024 * 7.1
            buff = src_handle.read(1)
            trgt_handle.write(buff)
            x+=1

        #close
        trgt_handle.close()
        src_handle.close()



class FileProcessor:
    def __init__(self, src_file_name, trgt_file_name):
        if not os.path.exists(src_file_name): #checks whether the file exists  or not
            raise Exception(src_file_name + ' doesnt exist!')
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name

    def process(self):
        n = 4 #number of chunks
        chunks = self.divide_into_chunks(n)
        cps = []
        for ch in chunks:
            cps.append(ChunkProcessor(self.src_file_name, ch[0], ch[1], ch[2]))


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
        for i in range(n-1):
            start = end #0,31,62
            end = start + size_of_chunk  #31,62,93
            chunks.append( (tup[0] + str(i) + tup[1], start, end) )

        #nth chunk
        chunks.append((tup[0] + str(i+1) + tup[1], end, src_file_size))
        return chunks


def main():
    #sfname = 'd:/mydocs/aa.txt'
    #tfname = 'd:/mydocs/bb.txt'
    #sfname = 'd:/images/kids.jpg'
    #tfname = 'd:/images/school_kids.jpg'

    fp = FileProcessor(sfname, tfname)
    fp.process()

    #print(os.path.exists(fname))
    #print(os.path.split(fname)) #returns a tuple of (parent_dir, file)



main()
