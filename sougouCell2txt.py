__author__ = 'wanghuafeng'
#coding:utf-8
import struct
import os, sys, glob

def read_utf16_str (f, offset=-1, len=2):
    if offset >= 0:
        f.seek(offset)
    str = f.read(len)
    return str.decode('UTF-16LE')

def read_uint16 (f):
    return struct.unpack ('<H', f.read(2))[0]

def get_word_from_sogou_cell_dict (fname):
    f = open (fname, 'rb')
    file_size = os.path.getsize (fname)

    hz_offset = 0
    mask = struct.unpack ('B', f.read(128)[4])[0]
    if mask == 0x44:
        hz_offset = 0x2628
    elif mask == 0x45:
        hz_offset = 0x26c4
    else:
        sys.exit(1)

    title   = read_utf16_str (f, 0x130, 0x338  - 0x130)
    type    = read_utf16_str (f, 0x338, 0x540  - 0x338)
    desc    = read_utf16_str (f, 0x540, 0xd40  - 0x540)
    samples = read_utf16_str (f, 0xd40, 0x1540 - 0xd40)

    py_map = {}
    f.seek(0x1540+4)

    while 1:
        py_code = read_uint16 (f)
        py_len  = read_uint16 (f)
        py_str  = read_utf16_str (f, -1, py_len)

        if py_code not in py_map:
            py_map[py_code] = py_str

        if py_str == 'zuo':
            break

    f.seek(hz_offset)
    while f.tell() != file_size:
        word_count   = read_uint16 (f)
        pinyin_count = read_uint16 (f) / 2

        py_set = []
        for i in range(pinyin_count):
            py_id = read_uint16(f)
            py_set.append(py_map[py_id])
        py_str = "'".join (py_set)

        for i in range(word_count):
            word_len = read_uint16(f)
            word_str = read_utf16_str (f, -1, word_len)
            f.read(12)
            yield py_str, word_str

    f.close()

def showtxt (records):
    for (pystr, utf8str) in records:
        print len(utf8str), utf8str

def store(records, f):
    for (pystr, utf8str) in records:
        # f.write("%s\t1\n" %(utf8str.encode("utf8")))
        #f.write("x:1\n")
        f.write("%s\n" %(utf8str.encode("utf8")))

def main ():
    if len (sys.argv) != 3:
        print "Unknown Option \n usage: python %s file.scel new.txt" %(sys.argv[0])
        exit (1)

    #Specify the param of scel path as a directory, you can place many scel file in this dirctory, the this process will combine the result in one txt file
    if os.path.isdir(sys.argv[1]):
        for fileName in glob.glob(sys.argv[1] + '*.scel'):
            print fileName
            generator = get_word_from_sogou_cell_dict(fileName)
            with open(sys.argv[2], "a") as f:
                store(generator, f)

    else:
        generator = get_word_from_sogou_cell_dict (sys.argv[1])
        with open(sys.argv[2], "w") as f:
            store(generator, f)
        #showtxt(generator)

def scel_pattern__to_txt():
    cell_pattern = 'sougou_cell_words\*.scel'
    file_list = glob.glob(cell_pattern)
    for filename in file_list:
        generator = get_word_from_sogou_cell_dict(filename)
        new_filename = os.path.splitext(filename)[0] + '.txt'
        with open(new_filename, "w") as f:
            store(generator, f)

def scel_file_to_txt(filename):
    assert isinstance(filename, unicode), 'filename should be unicode...'
    generator = get_word_from_sogou_cell_dict(filename)
    new_filename = os.path.splitext(filename)[0] + '.txt'
    with open(new_filename, 'w') as wf:
        store(generator, wf)

if __name__ == "__main__":
    # main()
    filename = u'sougou_cell_words\网络流行新词20150126.scel'
    scel_file_to_txt(filename)
