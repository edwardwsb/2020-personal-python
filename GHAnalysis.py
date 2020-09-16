import os
import argparse
import pickle
import re
from concurrent.futures import ThreadPoolExecutor

EVENTS = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')

class Data:
    def __init__(self):
        self.login_type = {}
        self.name_type = {}
        self.get_tot_ans = {}

    def count_ans(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                res = pattern.search(line)
                if res is None or res[1] not in EVENTS:
                    continue

                event, user, repo = res.groups()
                self.login_type.setdefault(user, {})
                self.get_tot_ans.setdefault(user, {})
                self.name_type.setdefault(repo, {})
                self.get_tot_ans[user].setdefault(repo, {})

                self.login_type[user][event] = self.login_type[user].get(event, 0)+1
                self.name_type[repo][event] = self.name_type[repo].get(event, 0)+1
                self.get_tot_ans[user][repo][event] = self.get_tot_ans[user][repo].get(event, 0)+1

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
        if not any((os.path.exists(f'{i}.json') for i in range(1, 4))):
            raise RuntimeError('error: data file not found')

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
        self.parser.add_argument('-u', '--user', type=str)
        self.parser.add_argument('-r', '--repo', type=str)
        self.parser.add_argument('-e', '--event', type=str)
        print(self.analyse())

    def analyse(self):
        args = self.parser.parse_args()
        event, user, repo = args.event, args.user, args.repo

        if args.init:
            self.data.init(args.init)
            return 'init done'
        self.data.load()

        if user and repo:
            res = self.data.get_tot_ans.get(user, {}).get(repo, {}).get(event, 0)
        elif user:
            res = self.data.login_type.get(user, {}).get(event, 0)
        else:
            res = self.data.name_type.get(repo, {}).get(event, 0)
        return res


if __name__ == '__main__':
    run = Run()