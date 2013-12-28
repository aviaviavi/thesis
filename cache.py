from Queue import Queue, PriorityQueue
from collections import Counter, defaultdict
from heapq import *
import time
import pdb

class CachePolicy(object):
    """
    Our partially abstract cache policy class. We just call get item on a sequence of data (one part at a time for now) and it keeps track of
    cache hits and misses given the policy.
    """

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

    def print_stats(self):
        print self.policy_name, "hits: " + str(self.get_hits()), "misses: " + str(self.get_misses())


class LRUCache(CachePolicy):
    """
    Evict the least recently used item
    """

    policy_name = "LRU"

    def __init__(self, cache_size):
        super(LRUCache, self).__init__(cache_size)
        self.cache = [] 
    
    def get_item(self, item):
        if item in self.cache:
            self.hits += 1
            self.cache.remove(item)
            self.cache.append(item)
        else:
            self.misses += 1
            if not self.is_full():
                self.cache.append(item)
            else:
                self.cache.pop(0)
                self.cache.append(item)

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
        try:
            current_q = [x[2] for x in self.cache]
            index = current_q.index(item)
        except ValueError:
            index = None
        if item in current_q:
            self.hits += 1
            self.cache[index] = [self.cache[index][1], time.time(), item] #[0] is 2nd use, [1] is this use
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
        self.counts[item] += 1
        current_q = [x[1] for x in self.cache]
        self.cache.sort()
        if item in current_q:
            self.hits += 1
            index = self.cache.index([self.counts[item]-1, item])
            self.cache[index][0] += 1
        else:
            self.misses += 1
            if not self.is_full():
                self.cache.append([self.counts[item], item])
            else:
                #evitc lfu and replace
                self.cache.pop(0)
                self.cache.append([self.counts[item], item])

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
        self.k_out = cache_size * 2 #TODO verify this is kosher

    def is_full(self):
        return len(self.q0) + len(self.q1) == self.cache_size

    def get_item(self, item):
        if item in self.q1:
            self.hits += 1
            self.q1.remove(item)
            self.q1.append(item)
        elif item in self.q_out:
            self.hits += 1 #TODO is this actually a hit?
            self.reclaim_for(item)
            self.q1.append(item)
        elif item in self.q0:
            self.hits += 1
            pass
        else: #cache miss
            self.misses += 1
            self.reclaim_for(item)
            self.q0.append(item)

    def reclaim_for(self, item):
        if not self.is_full():
            pass
        elif len(self.q0) > self.k_in:
            self.q_out.append(self.q0.pop(0)) #evict from q0, store 'address' in q_out
            if len(self.q_out) > self.k_out:
                self.q_out.pop(0)
        else:
            self.q1.pop(0)


class ARCCache(CachePolicy):
    """
    Adaptive Replacement Cache Policy
    """ 
    
    policy_name = "ARC"

    def __init__(self, cache_size):
        super(ARCCache, self).__init__(cache_size)
        self.t1 = []
        self.b1 = []
        self.t2 = []
        self.b2 = []
        self.p = 0
 
    def total_length(self):
        return len(self.t1) + len(self.b1) + len(self.t2) + len(self.b2)

    def get_item(self, item):

        def replace(p):
            if self.t1 and (item in self.b2 and len(self.t1) == p or len(self.t1) == p):
                self.b1.append(self.t1.pop(0))
            else:
                self.b2.append(self.t2.pop(0))
                
        if item in self.t1:
            self.hits += 1
            self.t1.remove(item)
            self.t2.append(item)
        elif item in self.t2:
            self.hits += 1
            self.t2.remove(item)
            self.t2.append(item)
        elif item in self.b1:
            self.misses += 1
            self.p = min(self.cache_size, self.p + max(len(self.b2) / len(self.b1), 1))
            replace(self.p)
            self.t2.append(item)
        elif item in self.b2:
            self.misses += 1
            self.p = max(self.cache_size, self.p - max(len(self.b1) / len(self.b2), 1))
            replace(self.p)
            self.t2.append(item)
        else:
            self.misses += 1
            if len(self.t1) + len(self.b1) == self.cache_size:
                if len(self.t1) < self.cache_size:
                    self.b1.pop(0)
                    replace(self.p)
                else:
                    self.t1.pop(0)
            elif len(self.t1) + len(self.b1) < self.cache_size and self.total_length() >= self.cache_size:
                if self.total_length() == 2 * self.cache_size:
                    try:
                        self.b2.pop(0)
                    except:
                        pass
                    replace(self.p)
            self.t1.append(item)


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

    def get_item(self, item):
        items = [i[1] for i in self.cache]
        if item in items:
            self.hits += 1
            self.crf[item] = self.val_funt(0) + self.crf_curr(item) 
            self.last_t[item] = self.time
            #self.quick_heapify(item)
        else:
            self.cache.sort()
            self.misses += 1
            self.crf[item] = self.val_funt(0)
            self.last_t[item] = self.time
            if self.is_full():
                victim = self.cache.pop(0)
            self.cache.append([self.crf[item], item])
            #self.quick_heapify(item)
        self.cache.sort()
        self.cache = [[self.crf_curr(i[1]), i[1]] for i in self.cache]
        self.time += 1

    def is_full(self):
        return len(self.cache) == self.cache_size

    def val_funt(self, x):
        #this is the function that computes the decay an item had for a given amount of time
        return (.5) ** (self.lam * x)  

    def crf_curr(self, b):
        return self.val_funt(self.time - self.last_t[b]) * self.crf[b]

    #no longer calling this as of now
    #i suspect this function might be messing things up
    def quick_heapify(self, item):
        if self.cache and item != self.cache[0]:
            try:
                index = self.cache.index(item)
            except ValueError: #not in list
                return
            #find the last item with a bigger crf than item
            tmp_index = index - 1
            while tmp_index != -1:
                tmp_item = self.cache[tmp_index]
                if self.crf_curr(tmp_item) > self.crf_curr(item):
                    self.cache[tmp_index], self.cache[index] = item, tmp_item
                    #recurslively call quick_heapify on the item we just swapped, so we can put it in the right spot
                    self.quick_heapify(tmp_item)
                    return
                tmp_index -= 1

class BeladysCache(CachePolicy):
    """
    Cache policy where we discard the item that will be used in the most distant future.
    Requires peaking at what memory accesses will happen next. Our comparison for the optimal policy.
    """

    policy_name = "belady's"

    def __init__(self, cache_size, accesses):
        super(BeladysCache, self).__init__(cache_size)
        self.cache_size = cache_size
        self.accesses = accesses

    





