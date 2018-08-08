#-*-coding:utf-8-*-

class Check(object):

    def checkAwrite(self):
        readF = 'D:\\FutuCode\\api\\futuquant_v3.1\\evatest\log\\2018-06-28\\TickerTest.txt'
        writeF = 'D:\\FutuCode\\api\\futuquant_v3.1\\evatest\log\\2018-06-28\\TickerTest_00883.txt'
        w = open(writeF,'a')
        for line in open(readF):
            if line.__contains__('HK.00883'):
                w.write(line)

        print('done...')
        w.close()

if __name__ == '__main__':
    c = Check()
    c.checkAwrite()
