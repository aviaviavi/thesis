from cache import *
import matplotlib.pyplot as plt
import pdb


def make_hist_array(d):
    output = []
    for key in d.keys():
        for i in range(d[key]):
            output.append(key)
    return output


def aggregate(keys_in, values_in, num_divisions=4):
    """
    The anderson stats need to be grouped into buckets, metrics like recency are generally almost unique.
    """
    new_keys = []
    new_values = []
    block_size = len(keys_in) / num_divisions
    for i in range(num_divisions):
        start = i * block_size
        end = (i + 1) * block_size
        new_keys.append(sum(keys_in[start:end]) / block_size)
        new_values.append(sum(values_in[start:end]) / block_size)
    print new_keys, new_values
    return new_keys, new_values

nytimes = open("nytimes.txt", "r").read().split()

powers_of_2 = [2 ** x for x in range(8, 9)]
lru = []
lfu = []
lru2 = []
twoq = []
arc = []
lrfu = []
random = []
anderson = []
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

trans_dates = ["860411", "860720", "861028", "870205", "870516", "870824", "871202"]
used_trans_dates = defaultdict(int)

for word in nytimes:
    #if its a date, just continue, unless its the start of a 101st day
    if len(word) == 6 and word.isdigit():
        if word in trans_dates and not used_trans_dates[word]:
            used_trans_dates[word] += 1
            all_words.append("ENDOF100DAYS")
        all_words.append(word)
        continue
    if word:
        word = word.strip().lower()
        #clean punctuation
        if word[0] in "<([{":
            word = word[1:]
        try:
            while word[-1] in ")}]>?!.,":
                word = word[:-1]
        except IndexError:  # word will be empty if it was just punctuation, just move on
            continue
        all_words.append(word)

and_stats = Stats()
stats_100_days = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

for cache_size in powers_of_2:
    cache = LRUCache(cache_size)
    cache2 = LFUCache(cache_size)
    cache3 = LRU2Cache(cache_size)
    cache4 = TwoQCache(cache_size)
    cache5 = ARCCache(cache_size)
    cache6 = LRFUCache(cache_size, .001)
    cache7 = RandomCache(cache_size)
    cache8 = AndersonCache(cache_size)
    #if cache_size == 4:
    #    cache7 = BeladysCache(cache_size, all_words)
    #else:
    #    cache7.clear(cache_size)
    total_length = 0
    caches = [cache, cache2, cache3, cache4, cache5, cache6, cache7, cache8]

    for word in all_words:
        if word:
            if word == "ENDOF100DAYS":
                for c in caches:
                    # practice
                    for item in set(and_stats.items):
                        practice = and_stats.get_practice(item)
                        recency = and_stats.get_recency(item)
                        spacing = and_stats.get_spacing(item)
                        if item in c.get_cache():
                            hit_or_miss = "hits"
                        else:
                            hit_or_miss = "misses"
                        stats_100_days[c.policy_name]["practice"][practice][hit_or_miss] += 1
                        stats_100_days[c.policy_name]["recency"][recency][hit_or_miss] += 1
                        if spacing:
                            stats_100_days[c.policy_name]["spacing"][spacing][hit_or_miss] += 1
                and_stats.clear()
            else:
                and_stats.add_item(word)
                if not (len(word) == 6 and word.isdigit()):
                    for c in caches:
                        evicted = c.get_item(word)
                total_length += 1

    lru.append(float(cache.misses) / float(cache.hits))
    lfu.append(float(cache2.misses) / float(cache2.hits))
    lru2.append(float(cache3.misses) / float(cache3.hits))
    twoq.append(float(cache4.misses) / float(cache4.hits))
    arc.append(float(cache5.misses) / float(cache5.hits))
    lrfu.append(float(cache6.misses) / float(cache6.hits))
    anderson.append(float(cache8.misses) / float(cache8.hits))
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
ax.plot(powers_of_2, anderson, 'p', label=cache8.policy_name)
#ax.plot(powers_of_2, beladys, "p", label="beladys")
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("miss/hit ratio")
plt.xlabel("cache size (items)")
plt.show()

# anderson stats, just use one cache size and uncomment
caches = [cache, cache2, cache3, cache4, cache5, cache6, cache8]

fig, ax = plt.subplots()
plt.ylabel("hits")
plt.xlabel("number of items seen since last occurrence")
#plt.ion()
for c in caches:
    keys = stats_100_days[c.policy_name]['recency'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['recency'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values)
    ax.plot(keys, values, "-", label=c.policy_name)
    #plt.draw()
    #pdb.set_trace()
legend = ax.legend(loc='upper right', shadow=True)
plt.show()
#plt.ioff()
#plt.close()


fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['practice'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['practice'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values)
    ax.plot(keys, values, '-', label=c.policy_name)
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("hits rate")
plt.xlabel("number of times seen")
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values)
    ax.plot(keys, values, '-', label=c.policy_name)
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("hit rate")
plt.xlabel("number of items between occurrences")
plt.show()

#if you want a shell after it runs
#
import readline # optional, will allow Up/Down/History in the console
#import code
#
#vars = globals().copy()
#vars.update(locals())
#shell = code.InteractiveConsole(vars)
#shell.interact()


