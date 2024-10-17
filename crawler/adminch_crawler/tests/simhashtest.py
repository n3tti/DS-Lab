import re

from simhash import Simhash, SimhashIndex


def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r"[^\w]+", "", s)
    return [s[i : i + width] for i in range(max(len(s) - width + 1, 1))]


a = Simhash(get_features("How are you? I am fine. Thanks."))
b = Simhash(get_features("How are u? I am fine.     Thanks."))
c = Simhash(get_features("How r you?I    am fine. Thanks."))
d = Simhash("How are you? I am fine. Thanks.")
e = Simhash("How are u? I am fine.     Thanks.")
print("{}".format(a.value))
print("{}".format(b.value))
print("{}".format(c.value))
print("Distances")
print(a.distance(b))
print(a.distance(c))
print(c.distance(b))
print("Distance wout feature")
print(d.distance(e))
print(Simhash("aa").distance(Simhash("bb")))
print(Simhash("aa").distance(Simhash("aa")))


def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r"[^\w]+", "", s)
    return [s[i : i + width] for i in range(max(len(s) - width + 1, 1))]


data = {
    1: "How are you? I Am fine. blar blar blar blar blar Thanks.",
    2: "How are you i am fine. blar blar blar blar blar than",
    3: "This is simhash test.",
}
objs = [(str(k), Simhash(get_features(v))) for k, v in data.items()]
index = SimhashIndex(objs, k=3)

print(index.bucket_size())

s1 = Simhash(get_features("How are you i am fine. blar blar blar blar blar thank"))
print(index.get_near_dups(s1))

index.add("4", s1)
print(index.get_near_dups(s1))
