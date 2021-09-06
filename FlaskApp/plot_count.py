import collections
import matplotlib.pyplot as plt

path = './app.log'
data = []
with open(path) as f:
    s = f.read()
    data.append(s)

data_str = data[0].split('\n')
top_date = []
for x in data_str:
    if 'GET /top/ HTTP/1.1' in x:
        top_date.append(x[0:10])
c = collections.Counter(top_date)
dct = sorted(c.items())
x = [x[0] for x in dct]
y = [x[1] for x in dct]


print(y)
plt.title('Strengths Finder App PV count')
plt.xticks(rotation=90)
plt.ylabel('PV')
plt.xlabel('date')
plt.plot(x, y)
plt.tight_layout()
plt.savefig('./plot_count.png')
plt.close()
