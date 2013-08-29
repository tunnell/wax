__author__ = 'tunnell'

import block_operations as bo


def break_up(filename):
    print(filename)
    f = open(filename, 'rb')
    data = f.read()

    for i in range(10000):
        word = bo.get_word_by_index(data, i)
        if(word >> 20 == 0xA00):
            print(i)
            break
        else:
            print(i, word, hex(word))


if __name__ == "__main__":
    filename = '/tmp/xe100_110319_0948_000000.xed'
    break_up(filename)
