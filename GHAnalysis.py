import os
import argparse
import pickle
import re
from concurrent.futures import ThreadPoolExecutor

typeS = ("Pushtype", "IssueCommenttype", "Issuestype", "PullRequesttype", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?name.*?"name":"(\S+?)"')

class Data:
    def __init__(self):
        self.login_type = {}
        self.name_type = {}
        self.get_tot_ans = {}

    def count_ans(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                res = pattern.search(line)
                if res is None or res[1] not in typeS:
                    continue

        type, login, name = res.groups()
        self.login_type.setdefault(login, {})
        self.get_tot_ans.setdefault(login, {})
        self.name_type.setdefault(name, {})
        self.get_tot_ans[login].setdefault(name, {})
        self.login_type[login][type] = self.login_type[login].get(type, 0)+1
        self.name_type[name][type] = self.name_type[name].get(type, 0)+1
        self.get_tot_ans[login][name][type] = self.get_tot_ans[login][name].get(type, 0)+1

    def init(self, dir_path: str):
        pool = ThreadPoolExecutor()
        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                pool.submit(self.count_ans, f'{cur_dir}/{name}')
        pool.shutdown()

        with open('1.json', 'wb') as f:
            pickle.dump(self.login_type, f)
        with open('2.json', 'wb') as f:
            pickle.dump(self.name_type, f)
        with open('3.json', 'wb') as f:
            pickle.dump(self.get_tot_ans, f)

    def load(self):
        with open('1.json', 'rb') as f:
            self.login_type = pickle.load(f)
        with open('2.json', 'rb') as f:
            self.name_type = pickle.load(f)
        with open('3.json', 'rb') as f:
            self.get_tot_ans = pickle.load(f)


class Run:
    def __init__(self):
        self.data = Data()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--init', type=str)
        self.parser.add_argument('-u', '--login', type=str)
        self.parser.add_argument('-r', '--name', type=str)
        self.parser.add_argument('-e', '--type', type=str)
        print(self.analyse())

    def analyse(self):
        args = self.parser.parse_args()
        type, login, name = args.type, args.login, args.name

        if args.init:
            self.data.init(args.init)
        self.data.load()

        if login and name:
            res = self.data.get_tot_ans.get(login, {}).get(name, {}).get(type, 0)
        elif login:
            res = self.data.login_type.get(login, {}).get(type, 0)
        else:
            res = self.data.name_type.get(name, {}).get(type, 0)
        return res

if __name__ == '__main__':
    run = Run()