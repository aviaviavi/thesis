from cache import *
import matplotlib.pyplot as plt
import pdb


def make_hist_array(d):
    output = []
    for key in d.keys():
        for i in range(d[key]):
            output.append(key)
    return output

nytimes = open("nytimes.txt", "r").read().split("     ")
nytimes = filter(lambda x: x != "" and "\r\r\n" not in x, nytimes)

powers_of_2 = [2 ** x for x in range(2, 8)]
lru = []
lfu = []
lru2 = []
twoq = []
arc = []
lrfu = []
random = []
#belady's is really really slow so just uncomment when you actually want to see it
#beladys = []

lru_stats = []
lfu_stats = []
lru2_stats = []
twoq_stats = []
arc_stats = []
lrfu_stats = []

all_words = []
all_evictions = defaultdict(dict)
for string in nytimes:
    for word in string.split(" "):
        #clean punctuation
        if word:
            word = word.strip().lower()
            if word[0] in "<([{":
                word = word[1:]
            try:
                while word[-1] in ")}]>?!.,":
                    word = word[:-1]
            except IndexError:  # word will be empty if it was just punctuation, just move on
                continue
            all_words.append(word)
and_stats = Stats()

for cache_size in powers_of_2:
    cache = LRUCache(cache_size)
    cache2 = LFUCache(cache_size)
    cache3 = LRU2Cache(cache_size)
    cache4 = TwoQCache(cache_size)
    cache5 = ARCCache(cache_size)
    cache6 = LRFUCache(cache_size, .001)
    cache7 = RandomCache(cache_size)
    total_length = 0

    for word in all_words:
        if word:
            caches = [cache, cache2, cache3, cache4, cache5, cache6, cache7]
            stats = [lru_stats, lru2_stats, lfu_stats, twoq_stats, arc_stats, lrfu_stats, lrfu_stats]
            and_stats.add_item(word)
            for c, stat in zip(caches, stats):
                evicted = c.get_item(word)

                #this block runs the statistics from the anderson paper. uncomment here as well as the block at the
                #bottom. only do one cache size if you uncomment this

                #if evicted:
                #    if type(evicted) == list:
                #        evicted = evicted[-1]
                #    # anderson statistics
                #    recency = and_stats.get_recency(evicted)
                #    practice = and_stats.get_practice(evicted)
                #    spacing = and_stats.get_spacing(evicted)
                #    all_evictions[c.policy_name]['recency'][recency] += 1
                #    all_evictions[c.policy_name]['practice'][practice] += 1
                #    if spacing:
                #        all_evictions[c.policy_name]['spacing'][spacing] += 1
                #else:
                #    if c.policy_name in all_evictions:
                #        all_evictions[c.policy_name]['not_evicted'] += 1
                #    else:
                #        all_evictions[c.policy_name] = {'recency': defaultdict(int),
                #                                        'practice': defaultdict(int),
                #                                        'spacing': defaultdict(int),
                #                                        'not_evicted': 0}
            total_length += 1
    #if cache_size == 4:
    #    cache7 = BeladysCache(cache_size, all_words)
    #else:
    #    cache7.clear(cache_size)
    lru.append(float(cache.misses) / float(cache.hits))
    lfu.append(float(cache2.misses) / float(cache2.hits))
    lru2.append(float(cache3.misses) / float(cache3.hits))
    twoq.append(float(cache4.misses) / float(cache4.hits))
    arc.append(float(cache5.misses) / float(cache5.hits))
    lrfu.append(float(cache6.misses) / float(cache6.hits))
    try:
        random.append(float(cache7.misses) / float(cache7.hits))
    except:
        random.append(cache7.misses)
    #beladys.append(float(cache7.misses) / float(cache7.hits))
    print cache_size, "done!"

cache.print_stats()
cache2.print_stats()
cache3.print_stats()
cache4.print_stats()
cache5.print_stats()
cache6.print_stats()
print total_length

fig, ax = plt.subplots()
ax.plot(powers_of_2, lru, label="lru")
ax.plot(powers_of_2, lfu, label="lfu")
ax.plot(powers_of_2, lru2, label="lru2")
ax.plot(powers_of_2, twoq, label="2q")
ax.plot(powers_of_2, arc, label="arc")
ax.plot(powers_of_2, random, label="random")
ax.plot(powers_of_2, lrfu, label=cache6.policy_name)
#ax.plot(powers_of_2, beladys, "p", label="beladys")
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("miss/hit ratio")
plt.xlabel("cache size (items)")
plt.show()

# anderson stats, just use one cache size and uncomment
#caches = [cache, cache2, cache3, cache4, cache5, cache6]
#stats = [lru_stats, lru2_stats, lfu_stats, twoq_stats, arc_stats, lrfu_stats]
#
#fig, ax = plt.subplots()
#for c in caches:
#    keys = all_evictions[c.policy_name]['recency'].keys()
#    keys.sort()
#    values = []
#    for k in keys:
#        values.append(all_evictions[c.policy_name]['recency'][k])
#    ax.plot(keys, values, '-', label=c.policy_name)
#legend = ax.legend(loc='upper right', shadow=True)
#plt.ylabel("number of evictions")
#plt.xlabel("number of items seen since last occurrence")
#plt.show()
#
#fig, ax = plt.subplots()
#for c in caches:
#    keys = all_evictions[c.policy_name]['practice'].keys()
#    values = []
#    for k in keys:
#        values.append(all_evictions[c.policy_name]['practice'][k])
#    ax.plot(keys, values, '-', label=c.policy_name)
#legend = ax.legend(loc='upper right', shadow=True)
#plt.ylabel("number of evictions")
#plt.xlabel("number of times seen")
#plt.show()
#
#fig, ax = plt.subplots()
#for c in caches:
#    keys = all_evictions[c.policy_name]['spacing'].keys()
#    values = []
#    for k in keys:
#        values.append(all_evictions[c.policy_name]['spacing'][k])
#    ax.plot(keys, values, '-', label=c.policy_name)
#legend = ax.legend(loc='upper right', shadow=True)
#plt.ylabel("number of evictions")
#plt.xlabel("number of words in between occurrences")
#plt.show()

#if you want a shell after it runs
#
#import readline # optional, will allow Up/Down/History in the console
#import code
#vars = globals().copy()
#vars.update(locals())
#shell = code.InteractiveConsole(vars)
#shell.interact()

