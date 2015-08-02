import config
import oj
import random
import subprocess
import codecs
import os
import sys

class Judger:
    def __init__(self, client, sid, pid, lang):
        self.client = client
        self.sid = sid
        self.pid = pid
        self.lang = lang

    def compile(self, srcPath, outPath):
        cmd = config.langCompile[self.lang] % {'src': srcPath, 'target': outPath}
        p = subprocess.Popen(cmd, shell = True,
          stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.STDOUT)
        retval = p.wait()
        return (retval, p.stdout.read())

    def judge(self, srcPath, outPath, inFile, ansFile, memlimit, timelimit):
        cmd = "".join([sys.path[0], "/", config.langRun[self.lang] % {'src': srcPath, 'target': outPath}])
        p = subprocess.Popen(cmd, shell = True,
          stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        retVal = 9
        try:
            out, err = p.communicate(input = self.readData(inFile), timeout = int(timelimit) / 1000)
        except subprocess.TimeoutExpired:
            p.kill()
            retVal = 5
        if(retVal == 9):
            if(p.returncode != 0):
                retVal = 6
            else:
                retVal = 2
        return retVal

    def run(self):
        srcPath = "%s/%s_%d.code" % (config.dataPath["codePath"], self.sid, random.randint(0, 65536))
        outPath = "%s/%s_%d.exe" % (config.dataPath["execPath"], self.sid, random.randint(0, 65536))
        self.saveCode(srcPath)

        print("    Compiling...")
        retVal, retData = self.compile(srcPath, outPath)
        if(retVal != 0):
            self.putRet(retData)
            self.putStatus(7)
            return 0
        else:
            self.putStatus(8)

        print("    Getting Data...")

        prob_data = self.getDataList(self.pid)
        datalist = prob_data["datalist"]

        for key in datalist:
            if self.hasData(key, datalist[key], "in") == False:
                dat = self.getData(key, "in")
                self.saveData(key, datalist[key], "in", dat)
            if self.hasData(key, datalist[key], "out") == False:
                dat = self.getData(key, "out")
                self.saveData(key, datalist[key], "out", dat)

        print("    Judging...")
        retval = 2
        for key in datalist:
            retval = self.judge(srcPath, outPath, self.__getDataPath(key, datalist[key], "in"),
              self.__getDataPath(key, datalist[key], "out"), prob_data["memlimit"], prob_data["timelimit"])
            if(retval != 2):
                self.putStatus(retval)
                break
        if(retval == 2):
            self.putStatus(retval)
        return 0

    def saveCode(self, path):
        code = self.client.GetCode(self.sid)
        fp = codecs.open(path, 'a', 'utf-8')
        fp.write(code.decode('utf-8'))
        fp.close()

    def putRet(self, ret):
        self.client.PutRet(self.sid, ret)

    def putStatus(self, retcode):
        self.client.PutStatus(self.sid, retcode)

    def getDataList(self, pid):
        return self.client.GetDataList(pid)

    def getData(self, pdid, ext):
        return self.client.GetData(pdid, ext)

    def __getDataPath(self, pdid, name, ext):
        return "%s/%s_%s.%s" % (config.dataPath["probPath"], str(pdid), name, ext)

    def saveData(self, pdid, name, ext, data):
        fp = codecs.open(self.__getDataPath(pdid, name, ext), 'a', 'utf-8')
        fp.write(data.decode('utf-8'))
        fp.close()

    def hasData(self, pdid, name, ext):
        return os.path.exists(self.__getDataPath(pdid, name, ext))

    def readData(self, path):
        fp = codecs.open(path, 'r', 'utf-8')
        __dat = fp.read().encode('utf-8')
        fp.close()
        return __dat