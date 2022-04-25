import collections
import struct
import sys
import time


class Node:
    def __init__(self, byte=None, number=0, children=None):
        self.byte = byte
        self.number = number
        self.children = children or []

    def __lt__(self, second):
        if self.byte and second.byte:
            return (self.number, self.byte) < (second.number, second.byte)
        else:
            return self.number < second.number

    def __eq__(self, second):
        return (self.number, self.byte) == (second.number, second.byte)


def encoding(top : Node, code = '') -> dict:
    if top.byte is None:
        byte2code = {}
        byte2code.update(encoding(top.children[0],code + '0'))
        byte2code.update(encoding(top.children[1],code + '1'))
        return byte2code
    else:
        return {top.byte: code}


def huffman_encode(byte2prob : dict) -> dict:
    nodes = [Node(byte, number) for byte, number in byte2prob.items()]
    nodes.sort()
    while len(nodes) > 1:
        number = nodes[0].number + nodes[1].number
        min_number = min(nodes)
        nodes.remove(min_number)
        min_number2 = min(nodes)
        nodes.remove(min_number2)
        list_children = [min_number, min_number2]
        node = Node(None, number, list_children)
        nodes.insert(0, node)
    root = nodes[0]
    codes = encoding(root)
    return codes


def substitution_enc(file : str, byte2code : dict) -> str:
    new_text = ''
    for old in file:
        new_text += str(byte2code.get(hex(old)))
    return new_text

        

def write_in_file(byte2code : dict, text : str, path_file : str):
    dote = path_file.rfind('.')
    if dote != -1:
        path_file = path_file[:dote]
    path_file += '.zmh'
    new_file = open(path_file, 'wb')
    new_file.write((str(len(byte2code))+'\n').encode())
    last_byte = len(text) % 16
    if int(last_byte) == 0:
        last_byte = 16
    new_file.write((str(last_byte)+'\n').encode())
    for byte in byte2code:
        new_file.write((str(byte)+'\n').encode())
        new_file.write((str(byte2code.get(byte))+'\n').encode())
    while text != '':
        if len(text) <= 16:
            # print(text)
            new_file.write((struct.pack("<H", int(text[0:16],2))))
            break
        #print(struct.pack("<H", int(text[0:16],2)))  
        new_file.write((struct.pack("<H", int(text[0:16],2))))
        text = text[16:]
    return


def substitution_dec(text : str, code2byte : dict):
    buf = b''
    len_key = 0
    for key in code2byte.keys():
        if len(key) > len_key:
            len_key = len(key)
    while text != '': 
        tmp = ''
        while (tmp not in code2byte.keys()) and (len(tmp) <= len_key):
            if text == '':
                sys.exit('Archive is damaged (dict error)')
            tmp += text[0]
            text = text[1:]
        if len(tmp) > len_key:
            sys.exit('Archive is damaged (dict error)')
        if (len(code2byte[tmp]) == 3):
            code2byte[tmp] = code2byte[tmp][0:2] + "0" + code2byte[tmp][2]
        buf += bytes.fromhex(code2byte[tmp][2:])       
    return buf


def mode1(path_file):
    file_open = open(path_file, 'rb')
    file = file_open.read()
    file_open.close()
    list_byte = list()
    for i in file:
        list_byte.append(hex(i))
    byte2prob = collections.Counter(list_byte)
    byte2code = huffman_encode(byte2prob)
    new_text = substitution_enc(file,byte2code)
    write_in_file(byte2code, new_text, path_file)


def mode2(path_file):
    file_open = open(path_file, 'rb')
    number_key = file_open.readline()
    number_key = (number_key.decode())[:-1]
    last_byte = file_open.readline()
    last_byte = (last_byte.decode())[:-1]
    if (not number_key.isdigit()) or (not last_byte.isdigit()):
        sys.exit('Archive is damaged (incorrect archive format)')
    if (int(number_key) > 256) or (int(last_byte) > 16):
        sys.exit('Archive is damaged (incorrect archive format)')
    code2byte = {}
    for i in range(int(number_key)):
        byte = file_open.readline()
        code = file_open.readline()
        byte = (byte.decode())[:-1]
        code = (code.decode())[:-1]
        pair = {byte: code}
        code2byte.update({code: byte})
    text = file_open.read()
    file_open.close()
    txt = ''
    while len(text) >= 2:   
        text1 = text[0:2]
        if len(text) == 2:
            res = str(bin(struct.unpack('<H',text1)[0])[2:])
            txt += (int(last_byte) - len(res))*'0' + res
            break
        res = str(bin(struct.unpack('<H',text1)[0])[2:])
        if len(res) <= 15:
            res = (16 - len(res)) * '0' + res
        txt += res
        text = text[2:]
    new_text = substitution_dec(txt, code2byte)
    dote = path_file.rfind('.')
    if dote != -1:
        path_file = path_file[:dote]
    new_file = open(path_file, 'wb')
    new_file.write(new_text)

start_time = time.time()
flag = True
if len(sys.argv) > 1: 
    mode = sys.argv[1]
else:
    mode = input("Select the operating mode: enc, dec ")

while (flag == True):
    if __name__ == "__main__":
        if mode == "enc":
            if len(sys.argv) > 2:
                mode1(sys.argv[2])
            else:
                file = input("Input path to file ")
                mode1(file)
            flag = False
        elif mode == "dec":
            if len(sys.argv) > 2:
                mode2(sys.argv[2])
            else:
                file = input("Input path to file ")
                mode2(file)
            flag = False
        else:
            mode = input("unknown command, repeat input ")
print('___%s seconds ___' % (time.time() - start_time))