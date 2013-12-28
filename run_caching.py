from cache import *
import matplotlib.pyplot as plt
import pdb

nytimes = open("nytimes.txt", "r").read().split("     ")
nytimes = filter(lambda x: x != "" and "\r\r\n" not in x, nytimes)

powers_of_2 = [2**x for x in range(2, 7)]
lru = []
lfu = []
lru2 = []
twoq = []
arc = []
lrfu = []

for cache_size in powers_of_2:
    cache = LRUCache(cache_size)
    cache2 = LFUCache(cache_size)
    cache3 = LRU2Cache(cache_size)
    cache4 = TwoQCache(cache_size)
    cache5 = ARCCache(cache_size)
    cache6 = LRFUCache(cache_size, 1)
    total_length = 0
    for string in nytimes:
        for word in string.split(" "):
            word = word.strip()
            if word:
                total_length += 1
                cache.get_item(word)
                cache2.get_item(word)
                cache3.get_item(word)
                cache4.get_item(word)
                cache5.get_item(word)
                cache6.get_item(word)
    lru.append(float(cache.hits) / float(cache.misses))
    lfu.append(float(cache2.hits) / float(cache2.misses))
    lru2.append(float(cache3.hits) / float(cache3.misses))
    twoq.append(float(cache4.hits) / float(cache4.misses))
    arc.append(float(cache5.hits) / float(cache5.misses))
    lrfu.append(float(cache6.hits) / float(cache6.misses))
    print cache_size, "done!"

cache.print_stats()
cache2.print_stats()
cache3.print_stats()
cache4.print_stats()
cache5.print_stats()
cache6.print_stats()
print total_length

fig, ax = plt.subplots()
ax.plot(powers_of_2, lru, "r", label="lru")
ax.plot(powers_of_2, lfu, "g", label="lfu")
ax.plot(powers_of_2, lru2, "b", label="lru2")
ax.plot(powers_of_2, twoq, "y", label="2q")
ax.plot(powers_of_2, arc, "k", label="arc")
ax.plot(powers_of_2, lrfu, "c", label="lrfu")
legend = ax.legend(loc='upper left', shadow=True)
plt.show()
