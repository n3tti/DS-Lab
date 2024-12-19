
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

count_pdf = {"3000": 4729, "11500": 908, "1500": 10530, "4500": 2810, "500": 29379, "0": 28336, "20000": 16453, "17000": 640, "14500": 792, "6500": 1978, "5500": 2228, "1000": 18012, "13000": 786, "2000": 7925, "6000": 1998, "12500": 979, "7000": 1699, "2500": 6269, "8000": 1671, "12000": 892, "7500": 1544, "9000": 1421, "4000": 3075, "5000": 2595, "15000": 628, "18000": 593, "3500": 3992, "9500": 1553, "15500": 660, "19000": 618, "10000": 1129, "16500": 601, "18500": 814, "14000": 686, "11000": 945, "19500": 495, "8500": 1234, "13500": 812, "17500": 637, "10500": 1037, "16000": 879}
count_html = {"500": 78170, "0": 121202, "1000": 35802, "1500": 34600, "2000": 13739, "6000": 213, "4000": 455, "4500": 437, "2500": 4173, "20000": 33, "3000": 2431, "7000": 72, "13500": 5, "16500": 3, "6500": 64, "11500": 12, "3500": 2068, "5500": 434, "5000": 169, "7500": 54, "15000": 2, "14500": 12, "15500": 6, "19000": 2, "8000": 44, "9500": 14, "9000": 4, "18500": 3, "17500": 1, "8500": 25, "11000": 1, "10500": 3, "16000": 5, "13000": 4, "10000": 5, "14000": 1, "12000": 3, "12500": 2}
data = []
for key, value in count_pdf.items():
    data.extend([[int(key)/1000, "PDF"]] * value)
for key, value in count_html.items():
    data.extend([[int(key)/1000, "HTML"]] * value)

df = pd.DataFrame(data, columns=["word_count", "Source"])

custom_palette = {"PDF": "#3512ff", "HTML": "#fc288f"} 

plot = sns.displot(df, x="word_count", hue="Source", bins=21, stat="density", palette=custom_palette)
#for ax in plot.axes.flat: 
#    ax.set_yscale("log")
# Add labels and title
plt.xlabel("Word Count (k)")
plt.ylabel("Density")
plt.title("Word Count Distribution (HTML and PDF)")
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
#plt.show()
plt.savefig("./wcount_distribution.png")
