from Queue import Queue, PriorityQueue
from collections import Counter, defaultdict, deque
from copy import copy
from heapq import *
import time
import pdb
import random
import math


class CachePolicy(object):
    """
    Our partially abstract cache policy class. We just call get item on a sequence of data (one part at a time for now) and it keeps track of
    cache hits and misses given the policy.
    """

    policy_name = "abstract"

    def __init__(self, cache_size):
        self.hits = 0
        self.misses = 0
        self.cache_size = cache_size

    def get_item(self, item):
        abstract

    def get_misses(self):
        return self.misses

    def get_hits(self):
        return self.hits

    def is_full(self):
        abstract

    def place_sorted(self, entry):
        count = entry[0]
        item = entry[1]
        for i in range(len(self.cache)):
            if self.cache[i][0] > count:
                self.cache.insert(i, entry)
                return
        self.cache.append(entry)

    def print_stats(self):
        print self.policy_name, "hits: " + str(self.get_hits()), "misses: " + str(self.get_misses())

    def cache_list(self, l=None):
        if not l:
            l = "a b rockets and stars and rockets all fly through the sky as we all watch asdf asdf asdf asdf watch chair".split()
        for item in l:
            self.get_item(item)
            print item
            self.print_cache()
            print "================"

    def print_cache(self):
        print self.cache

    def get_cache(self):
        return self.cache


class LRUCache(CachePolicy):
    """
    Evict the least recently used item
    """

    policy_name = "LRU"

    def __init__(self, cache_size):
        super(LRUCache, self).__init__(cache_size)
        self.cache = []

    def get_item(self, item):
        evicted = None
        if item in self.cache:
            self.hits += 1
            self.cache.remove(item)
            self.cache.append(item)
        else:
            self.misses += 1
            if not self.is_full():
                self.cache.append(item)
            else:
                evicted = self.cache.pop(0)
                self.cache.append(item)
        return evicted

    def is_full(self):
        return len(self.cache) == self.cache_size


class LRU2Cache(LRUCache):
    """
    Evict the item with the least recent penultimate use
    """

    policy_name = "LRU2"

    def __init__(self, cache_size):
        super(LRU2Cache, self).__init__(cache_size)
        self.timing = defaultdict(list)

    def get_item(self, item):
        #get index we are editing
        evicted = None
        try:
            current_q = [x[2] for x in self.cache]
            index = current_q.index(item)
        except ValueError:
            index = None
        if item in current_q:
            self.hits += 1
            self.cache[index] = [self.cache[index][1], time.time(), item]  # [0] is 2nd use, [1] is this use
        else:
            self.misses += 1
            # make the new item to put into cache
            if self.timing[item]:
                new_entry = [self.timing[item][1], time.time(), item]
            else:
                new_entry = [0, time.time(), item]
                #either add it, or evict and add
            if not self.is_full():
                self.cache.append(new_entry)
            else:
                self.cache.sort()
                evicted = heapreplace(self.cache, new_entry)
                self.timing[evicted[2]] = evicted
                return evicted

    def get_cache(self):
        return [x[2] for x in self.cache]


class RandomCache(CachePolicy):
    """
    Evict a random item
    """

    policy_name = "random"

    def __init__(self, cache_size):
        super(RandomCache, self).__init__(cache_size)
        self.cache = []

    def is_full(self):
        return len(self.cache) == self.cache_size

    def get_item(self, item):
        if item in self.cache:
            self.hits += 1
        else:
            self.misses += 1
            if self.is_full():
                self.cache.remove(random.choice(self.cache))
            self.cache.append(item)


class LFUCache(CachePolicy):
    """
    Evict the least frequently used item
    """

    policy_name = "LFU"

    def __init__(self, cache_size):
        super(LFUCache, self).__init__(cache_size)
        self.cache = []
        self.counts = Counter()

    def is_full(self):
        return len(self.cache) == self.cache_size

    def get_item(self, item):
        self.counts[item] += 1.0
        current_q = [x[1] for x in self.cache]
        if item in current_q:
            self.hits += 1
            index = self.cache.index([self.counts[item] - 1, item])
            self.cache[index][0] += 1.0
            self.place_sorted(self.cache.pop(index))
        else:
            self.misses += 1
            if not self.is_full():
                self.place_sorted([self.counts[item], item])
            else:
                #evitc lfu and replace
                evicted = self.cache.pop(0)
                self.place_sorted([self.counts[item], item])
                return evicted

    def get_cache(self):
        return [x[1] for x in self.cache]


class TwoQCache(CachePolicy):
    """
    A 2 Queue eviction policy. Just worked off of the paper by Johnson and Sasha
    """

    policy_name = "2Q"

    def __init__(self, cache_size):
        super(TwoQCache, self).__init__(cache_size)
        self.q0 = []
        self.q1 = []
        self.q_out = []
        self.k_in = cache_size / 4
        self.k_out = cache_size * 2  # TODO verify this is kosher

    def is_full(self):
        return len(self.q0) + len(self.q1) == self.cache_size

    def get_item(self, item):
        if item in self.q1:
            self.hits += 1
            self.q1.remove(item)
            self.q1.append(item)
        elif item in self.q_out:
            self.misses += 1  # TODO is this actually a hit?
            self.reclaim_for(item)
            self.q1.append(item)
        elif item in self.q0:
            self.hits += 1
            pass
        else:  # cache miss
            self.misses += 1
            evicted = self.reclaim_for(item)
            self.q0.append(item)
            return evicted

    def reclaim_for(self, item):
        if not self.is_full():
            pass
        elif len(self.q0) > self.k_in:
            self.q_out.append(self.q0.pop(0))  # evict from q0, store 'address' in q_out
            if len(self.q_out) > self.k_out:
                return self.q_out.pop(0)
        else:
            return self.q1.pop(0)

    def get_cache(self):
        return self.q0 + self.q1


class ARCCache(CachePolicy):
    """
    Adaptive Replacement Cache Policy
    """

    policy_name = "ARC"

    def __init__(self, size):
        super(ARCCache, self).__init__(size)
        self.c = size
        self.p = 0
        self.t1 = deque()
        self.t2 = deque()
        self.b1 = deque()
        self.b2 = deque()

    def replace(self, args):
        evicted = None
        if self.t1 and (
            (args in self.b2 and len(self.t1) == self.p) or
            (len(self.t1) > self.p)):
            evicted = old = self.t1.pop()
            self.b1.appendleft(old)
        else:
            evicted = old = self.t2.pop()
            self.b2.appendleft(old)
        return evicted

    def get_item(self, item):
        # i got this code off the internet. changed it around a little bit to fit into this class.
        evicted = None
        hit = False
        if item in self.t1:
            hit = True
            self.hits += 1
            self.t1.remove(item)
            self.t2.appendleft(item)
        if item in self.t2:
            hit = True
            self.hits += 1
            self.t2.remove(item)
            self.t2.appendleft(item)
        if item in self.b1:
            self.p = min(self.c, self.p + max(len(self.b2) / len(self.b1), 1))
            evicted = self.replace(item)
            self.b1.remove(item)
            self.t2.appendleft(item)
            #print "%s:: t1:%s b1:%s t2:%s b2:%s p:%s" % (
            #    repr(func)[10:30], len(self.t1),len(self.b1),len(self.t2),
            #    len(self.b2), self.p)
        if item in self.b2:
            self.p = max(0, self.p - max(len(self.b1) / len(self.b2), 1))
            evicted = self.replace(item)
            self.b2.remove(item)
            self.t2.appendleft(item)
            #print "%s:: t1:%s b1:%s t2:%s b2:%s p:%s" % (
            #   repr(func)[10:30], len(self.t1),len(self.b1),len(self.t2),
            #   len(self.b2), self.p)
        if len(self.t1) + len(self.b1) == self.c:
            if len(self.t1) < self.c:
                self.b1.pop()
                evicted = self.replace(item)
            else:
                evicted = self.t1.pop()
        else:
            total = len(self.t1) + len(self.b1) + len(
                self.t2) + len(self.b2)
            if total >= self.c:
                if total == (2 * self.c):
                    self.b2.pop()
                evicted = self.replace(item)
        self.t1.appendleft(item)
        if not hit:
            self.misses += 1
        return evicted

    def print_cache(self):
        print "t1: {0}, b1: {1}, t2: {2}, b2: {3}, p: {4}".format(self.t1, self.b1, self.t2, self.b2, self.p)

    def get_cache(self):
        return list(self.t1) + list(self.t2)


class LRFUCache(CachePolicy):
    """
    Keep track of both recency and frequency
    """

    policy_name = "LRFU"

    def __init__(self, cache_size, lam):
        super(LRFUCache, self).__init__(cache_size)
        self.cache = []
        #lambda
        self.lam = lam
        #combined recency frequency vals
        self.crf = defaultdict(float)
        #last accesses of all items
        self.last_t = defaultdict(int)
        self.time = 0
        self.policy_name += "-" + str(self.lam)

    def get_item(self, item):
        items = [i[1] for i in self.cache]
        victim = None
        if item in items:
            self.hits += 1
            self.crf[item] = self.val_funt(0) + self.crf_curr(item)
            self.last_t[item] = self.time
            self.cache[self.index_of(item)][0] = self.crf[item]
            self.place_sorted(self.cache.pop(self.index_of(item)))
        else:
            self.misses += 1
            self.crf[item] = self.val_funt(0) + self.crf_curr(item)
            self.last_t[item] = self.time
            if self.is_full():
                victim = self.cache.pop(0)
                self.crf[victim[1]] = victim[0]
            self.place_sorted([self.crf[item], item])
            #update every other item in cache
        self.cache = [[self.crf_curr(i[1]), i[1]] if i[1] != item else [self.crf[item], item] for i in self.cache]
        self.time += 1
        return victim

    def is_full(self):
        return len(self.cache) == self.cache_size

    def val_funt(self, t):
        #this is the function that computes the decay an item had for a given amount of time
        return (.5) ** (self.lam * t)

    def crf_curr(self, b):
        return self.val_funt(self.time - self.last_t[b]) * self.crf[b]

    def index_of(self, item):
        for i in range(0, len(self.cache)):
            if self.cache[i][1] == item:
                return i

    def get_cache(self):
        return [x[1] for x in self.cache]


class BeladysCache(CachePolicy):
    """
    Cache policy where we discard the item that will be used in the most distant future.
    Requires peaking at what memory accesses will happen next. Our comparison for the optimal policy.
    """

    policy_name = "belady's"

    def cache_input(self):
        for t in range(len(self.accesses)):
            word = self.accesses[t]
            if word in self.cache:
                self.hits += 1
            else:
                self.misses += 1
                if self.is_full():
                    # figure out which item to evict
                    max_next_access = 0
                    evict_index = 0
                    for j in range(len(self.cache)):
                        curr_word = self.cache[j]
                        curr_word_accesses = self.access_of[curr_word]
                        try:
                            temp = min(self.remove_old_access(curr_word_accesses, t))
                            if temp > max_next_access:
                                evict_index = j
                                max_next_access = temp
                        except ValueError:  # word has no next uses, get rid of it
                            evict_index = j
                            break
                    # remove it
                    self.cache.pop(evict_index)
                # append new word to cache
                self.cache.append(word)

    def __init__(self, cache_size, accesses):
        super(BeladysCache, self).__init__(cache_size)
        self.cache_size = cache_size
        self.cache = []
        self.accesses = accesses
        #build accesses
        self.access_of = defaultdict(list)
        for t in range(len(self.accesses)):
            self.access_of[self.accesses[t]].append(t)
        #start caching
        self.cache_input()

    def is_full(self):
        return len(self.cache) == self.cache_size

    @staticmethod
    def remove_old_access(l, t):
        l = filter(lambda x: x > t, l)
        return l

    def clear(self, size):
        self.cache = []
        self.hits = 0
        self.misses = 0
        self.cache_size = size
        self.cache_input()


class AndersonCache(CachePolicy):
    """
    Cache based on memory model of Anderson and Schooler 1991
    """
    policy_name = "Anderson"

    def __init__(self, cache_size):
        super(AndersonCache, self).__init__(cache_size)
        self.cache = []
        self.history = []
        self.item_history = defaultdict(list)
        self.t = 1

    def is_full(self):
        return len(self.cache) == self.cache_size

    def get_item(self, item):
        self.history.append(item)
        self.item_history[item].append(self.t)
        if item in self.cache:
            self.hits += 1
            return
        self.misses += 1
        if self.is_full():
            victim = None
            min_prob = 0
            for word in self.cache:
                tmp = self.need_prob(item)
                if not victim or tmp <= min_prob:
                    victim = word
                    min_prob = tmp
            self.cache.remove(victim)
        self.cache.append(item)
        self.t += 1

    def need_prob(self, item):
        need = 0
        power1 = power = 2
        a = 1
        b = .61  # magic value from anderson paper
        for access in self.item_history[item]:
            need += a * (math.log(access) ** math.log(power))
            power = max(power1, b * ((self.t - access) ** power1))
        return need


class Stats(object):

    def __init__(self):
        self.items = []
        self.counts = Counter()

    def add_item(self, item):
        self.items.append(item)
        self.counts[item] += 1

    def get_practice(self, word):
        return self.counts[word]

    def get_recency(self, word):
        index = len(self.items) - 1
        while self.items[index] != word:
            index -= 1
        return self.num_days(index, len(self.items) - 1)

    def get_spacing(self, word):
        if self.counts[word] != 2:
            return None
        first_use = self.items.index(word)
        last_use = self.items.index(word, first_use + 1)
        out = self.num_days(first_use, last_use)
        return out

    def clear(self):
        self.items = []
        self.counts = Counter()

    def num_days(self, start, end):
        total = 0
        last_day = None
        for i in range(start, end):
            item = self.items[i]
            if len(item) == 6 and item.isdigit() and item != last_day:
                total += 1
                last_day = item
        return total


