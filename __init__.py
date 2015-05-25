import ConfigParser
import os, sys, time, subprocess,re

CONFIG_FILE = "CtsConfig"
CTS_SECTION = "CTS"
CTS_ROOT_PATH = "ctsroot"
CTS_LOG_PATH = "ctslogpath"


class Configrations(dict):
    def __init__(self,config_file = CONFIG_FILE):
        self.config_file = os.path.abspath(os.path.join(os.path.split(__file__)[0],config_file))
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        for s in self.config.sections():
            self[s] = {}
            for k,v in self.config.items(s):
                self[s][k] = v



class CTS:
    def __init__(self,config = Configrations()):
        self.config = config[CTS_SECTION]
        self.cts_root_path = CTS_ROOT_PATH
        self.cts_log_path = CTS_LOG_PATH
    @property
    def root_path(self):
        return os.path.abspath(self.config[self.cts_root_path])
    @property
    def tradefed_path(self):
        return os.path.join(self.root_path,"tools","cts-tradefed")
    @property
    def result_log_root_folder(self):
        return os.path.join(self.root_path,"repository","logs")
    @property
    def result_root_folder(self):
        return os.path.join(self.root_path,"repository","results")
    @property
    def trace_log_folder(self):
        return self.config[self.cts_log_path]
    @property
    def version(self):
        string =  self.run('')
        regexp = "\AAndroid CTS \S*"
        m = re.match(regexp, string)
        return m.group()
    @property
    def results(self):
        ret = []
        string = self.run("l r")
        regexp = "(?P<session>\d*)\s*(?P<passed>\d*)\s*(?P<failed>\d*)\s*(?P<notExecuted>\d*)\s*(?P<start_time>[\d\.]{10}\_[\d\.]{8})\s*(?P<plan>[\S]*)\s*(?P<serials>[\S]*)\s*"
        for line in string.split("\n"):
            m = re.match(regexp,line)
            if m:
                r = m.groupdict()
                r["session"] = int(r["session"])
                ret.append(r)
        return ret
    def get_last_result(self):
        return self.results[-1]
    def get_last_logs(self):
        s = self.results[-1]["session"]
        return self.get_logs(session = s)
    def get_result(self,session = None,start_time = None):
        rt = None
        rs = self.results
        if session is not None:
            rt = [_ for _ in rs if _["session"] == session]
        elif start_time:
            rt = [_ for _ in rs if _["start_time"] == start_time]
        if not rt:
            raise Exception("Can't find result by info Session %d, Start_time %s"%(session,start_time))
        return rt[0]
    def get_logs(self,session = None, start_time = None):
        result = self.get_result(session = session, start_time = start_time)
        result_zip = os.path.join(self.result_root_folder,result["start_time"]+".zip")
        result_logs = os.path.join(self.result_log_root_folder,result["start_time"])
        return result_zip, result_logs
    def run(self,cmd):
        ctstalk = CtsTalk(self)
        return ctstalk(cmd)


class CtsTalk(object):
    def __init__(self, cts_config):
        self.config = cts_config
        self.tradefed = self.config.tradefed_path
        self.trace_log = os.path.join(self.config.trace_log_folder,"trace_log.txt")
        self.cmd = "exit| exec bash %s"%self.tradefed

    def __call__(self, cmd):
        if cmd.strip().startswith("run"):
            return self.run_tradefed(cmd)
        else:
            return self.short_tradefed(cmd)
    def short_tradefed(self,cmd):
        return os.popen(self.cmd+" "+cmd).read().strip()
    def run_tradefed(self,cmd):
        #cmd = [self.tradefed] + cmd.split()
        cmd = self.cmd + " "+ cmd
        result = None
        #regexp = "(?P<start_time>[\d\.]{10}\_[\d\.]{8}).\s+Passed\s+(?P<passed>\d+),\s+Failed\s+(?P<failed>\d+),\s+Not\s+Executed\s+(?P<notExecuted>\d+)"
        regexp = "XML\s+test\s+result\s+file\s+generated\s+at\s+(?P<start_time>[\d\.]{10}\_[\d\.]{8})."
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if line:
                m = re.search(regexp, line)
                if m:
                    result = m.groupdict()
                sys.stdout.write(line)
                sys.stdout.flush()
            if "All done" in line:
                time.sleep(5)
                p.terminate()
                print "Done!"
                break
        #return "start_time: %s\npassed: %s\nfailed: %s\nnotexecuted: %s"%(result["start_time"],result["passed"],result["failed"],result["notExecuted"])
        return result["start_time"]

cts = CTS()
