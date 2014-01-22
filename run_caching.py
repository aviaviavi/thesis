from cache import *
import matplotlib.pyplot as plt
import pdb
from matplotlib.font_manager import FontProperties


def make_hist_array(d):
    output = []
    for key in d.keys():
        for i in range(d[key]):
            output.append(key)
    return output


def is_day(word):
    return len(word) == 6 and word.isdigit()

def log_or_zero(x):
    if x == 0:
        x = .000000001
    return math.log(x)

def aggregate(keys_in, values_in, num_divisions=20):
    """
    The anderson stats need to be grouped into buckets, metrics like recency are generally almost unique.
    """
    if len(keys_in) <= 4:
        return keys_in, values_in 
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

def aggregate_log(keys_in, values_in, num_divisions=4):
    """
    Since the probabilities hit 0 and 1, we will cut out data after convergence. then
    aggrigate
    if 1.0 in values_in:
        convergence_index = values_in.index(1.0) 
    elif 0.0 in values_in:
        convergence_index = values_in.index(0.0)
    else:
        convergence_index = None
    if convergence_index:
        keys_in, values_in = keys_in[0:convergence_index-1], values_in[0:convergence_index-1]
    """

    print keys_in, values_in
    keys_in, values_in = aggregate(keys_in, values_in, num_divisions)
    return map(math.log, map(lambda x: x + .00001, keys_in)), map(math.log, map(lambda x: x + .00001, values_in))

def logify(list_in):
    return map(math.log, map(lambda x: x + .00001, list_in))

def set_axis_lines_bw(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be
    suitable for black and white viewing.
    """
    MARKERSIZE = 3

    COLORMAP = \
        {
            'b': {'marker': None, 'dash': (None, None)},
            'g': {'marker': None, 'dash': [5, 5]},
            'r': {'marker': None, 'dash': [5, 3, 1, 3]},
            'c': {'marker': None, 'dash': [1, 3]},
            'm': {'marker': None, 'dash': [5, 2, 5, 2, 5, 10]},
            'y': {'marker': None, 'dash': [5, 3, 1, 2, 1, 10]},
            'k': {'marker': 'o', 'dash': (None, None)}  # [1,2,1,10]}
        }

    for line in ax.get_lines() + ax.get_legend().get_lines():
        origColor = line.get_color()
        line.set_color('black')
        line.set_dashes(COLORMAP[origColor]['dash'])
        line.set_marker(COLORMAP[origColor]['marker'])
        line.set_markersize(MARKERSIZE)

def set_fig_lines_bw(fig):
    """
    Take each axes in the figure, and for each line in the axes, make the
    line viewable in black and white.
    """
    for ax in fig.get_axes():
        set_axis_lines_bw(ax)

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
beladys = []

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
    #if len(word) == 6 and word.isdigit():
    #    if word in trans_dates and not used_trans_dates[word]:
    #        used_trans_dates[word] += 1
    #        all_words.append("ENDOF100DAYS")
    #    all_words.append(word)
    #    if word == trans_dates[-1]:
    #        break
    #    continue
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
    cache8 = AndersonCache(cache_size, 1.5)
    cache9 = BeladysCache(cache_size, all_words)
    #if cache_size == 4:
    #    cache9 = BeladysCache(cache_size, all_words)
    #else:
    #    cache9.clear(cache_size)
    total_length = 0
    caches = [cache, cache2, cache3, cache4, cache5, cache6, cache7, cache8, cache9]
    current_day = None
    num_day = 0
    for word in all_words:
        if word:
            and_stats.add_item(word)
            # if its a day
            if and_stats.is_day(word):
                # and its the next day
                if word != current_day:
                    num_day += 1
                    print num_day
                    current_day = word
                    if num_day > 100:
                        and_stats.pop_day()
                        if num_day % 10 == 0:

                            for c in caches:
                                for item in set(filter(lambda i: not is_day(i), and_stats.items)):
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
                                        if spacing[1] < 10:
                                            spacing_block = "spacing_1"
                                        elif 10 <= spacing[1] < 30:
                                            spacing_block = "spacing_2"
                                        else:
                                            spacing_block = "spacing_3"
                                        stats_100_days[c.policy_name][spacing_block][spacing[0]][hit_or_miss] += 1
            else:
                for c in caches:
                    evicted = c.get_item(word)
                total_length += 1

    and_stats.clear()

    lru.append(float(cache.misses) / float(cache.hits))
    lfu.append(float(cache2.misses) / float(cache2.hits))
    lru2.append(float(cache3.misses) / float(cache3.hits))
    twoq.append(float(cache4.misses) / float(cache4.hits))
    arc.append(float(cache5.misses) / float(cache5.hits))
    lrfu.append(float(cache6.misses) / float(cache6.hits))
    anderson.append(float(cache8.misses) / float(cache8.hits))
    random.append(float(cache7.misses) / float(cache7.hits))
    #beladys.append(float(cache9.misses) / float(cache9.hits))
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
#ax.plot(powers_of_2, random, label="random")
ax.plot(powers_of_2, lrfu, label=cache6.policy_name)
ax.plot(powers_of_2, anderson, 's-', label=cache8.policy_name)
#ax.plot(powers_of_2, beladys, "p-", label="beladys")
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("miss/hit ratio")
plt.xlabel("cache size (items)")
set_fig_lines_bw(fig)
plt.show()

# =================================
# normal plots
# =================================

# anderson stats, just use one cache size and uncomment
caches = [cache, cache2, cache3, cache4, cache5, cache6, cache8, cache9]
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'gray']
fig, ax = plt.subplots()
#plt.ion()
for c in caches:
    keys = stats_100_days[c.policy_name]['recency'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['recency'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values)
    ax.plot(keys, values, label=c.policy_name)
    #plt.draw()
    #pdb.set_trace()
legend = ax.legend(loc='upper right', shadow=True)
plt.ylabel("hit percentage")
plt.xlabel("number of items seen since last occurrence")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
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
    ax.plot(keys, values, label=c.policy_name)
legend = ax.legend(loc='lower right', shadow=True)
plt.ylabel("hit percentage")
plt.xlabel("number of times seen")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_1'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_1'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values, 4)
    ax.plot(keys, values, label=c.policy_name)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.ylabel("hit percentage")
plt.xlabel("number of items between occurrences (0-9 recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_2'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_2'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values, 4)
    ax.plot(keys, values, label=c.policy_name)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.ylabel("hit percentage")
plt.xlabel("number of items between occurrences (10-30 recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_3'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_3'][k]
        values.append(float(curr_stats['hits']) / (curr_stats['hits'] + curr_stats['misses']))
    keys, values = aggregate(keys, values, 4)
    ax.plot(keys, values, label=c.policy_name)
legend = ax.legend(loc='center left', shadow=True)
plt.ylabel("hit percentage")
plt.xlabel("number of items between occurrences (31+ recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

# =================================
# log plots
# =================================

# anderson stats, just use one cache size and uncomment
caches = [cache, cache2, cache3, cache4, cache5, cache6, cache8, cache9]
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'gray']
fig, ax = plt.subplots()
plt.ylabel("log odds")
plt.xlabel("log number of items seen since last occurrence")
#plt.ion()
for c in caches:
    keys = stats_100_days[c.policy_name]['recency'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['recency'][k]
        try:
            values.append(float(curr_stats['hits']) / curr_stats['misses'])
        except:
            values.append(float(curr_stats['hits']) / .1)
    keys, values = aggregate(keys, values, 3)
    ax.plot(logify(keys), logify(values), label=c.policy_name)
    #plt.draw()
    #pdb.set_trace()
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
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
        values.append(1 / float(curr_stats['hits']))
    keys, values = aggregate(keys, values, 3)
    ax.plot(logify(keys), logify(values), label=c.policy_name)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.ylabel("log hit percentage")
plt.xlabel("log number of times seen")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_1'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_1'][k]
        try:
            values.append(float(curr_stats['hits']) / curr_stats['misses'])
        except:
            values.append(float(curr_stats['hits']) / .1)
    keys, values = aggregate(keys, values, 3)
    ax.plot(logify(keys), logify(values), label=c.policy_name)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.ylabel("log hit percentage")
plt.xlabel("log number of items between occurrences (0-9 recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_2'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_2'][k]
        try:
            values.append(float(curr_stats['hits']) / curr_stats['misses'])
        except:
            values.append(float(curr_stats['hits']) / .1)
    keys, values = aggregate(keys, values, 3)
    ax.plot(logify(keys), logify(values), label=c.policy_name)
ax.legend(loc='right center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.ylabel("log odss")
plt.xlabel("log number of items between occurrences (10-30 recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()

fig, ax = plt.subplots()
for c in caches:
    keys = stats_100_days[c.policy_name]['spacing_3'].keys()
    keys.sort()
    values = []
    for k in keys:
        curr_stats = stats_100_days[c.policy_name]['spacing_3'][k]
        try:
            values.append(float(curr_stats['hits']) / curr_stats['misses'])
        except:
            values.append(float(curr_stats['hits']) / .1)
    keys, values = aggregate(keys, values, 3)
    ax.plot(logify(keys), logify(values), label=c.policy_name)
legend = ax.legend(loc='center right', shadow=True)
plt.ylabel("log odds")
plt.xlabel("log number of items between occurrences (31+ recency)")
plt.rc('axes', color_cycle=colors)
#set_fig_lines_bw(fig)
plt.show()



#if you want a shell after it runs
#
import readline # optional, will allow Up/Down/History in the console
import code

vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()


