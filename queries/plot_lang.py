import matplotlib.pyplot as plt
import numpy as np

lang_html = {'EN': 81606, 'DE': 171841, 'FR': 230900, 'IT': 198512, 'RM': 728, 'Other': 4787, '?': 274771}
lang_pdf = {'EN': 53788, 'DE': 199991, 'FR': 428609, 'IT': 245291, 'RM': 532, 'Other': 3508, '?': 35512}

languages = list(lang_html.keys())
counts1 = list(lang_html.values())
counts2 = list(lang_pdf.values())

bar_width = 0.35
x = np.arange(len(languages))

plt.figure(figsize=(10, 6))
plt.bar(x - bar_width / 2, counts1, width=bar_width, color='#89CFF0', label='HTML')
plt.bar(x + bar_width / 2, counts2, width=bar_width, color='#3512ff', label='PDF')

plt.xlabel("Languages", fontsize=14)  # Larger x-axis label
plt.ylabel("Counts", fontsize=14)     # Larger y-axis label
plt.title("Language Distribution", fontsize=18)  # Larger title
plt.xticks(x, languages, fontsize=23)  # Larger x-tick labels
plt.yticks(fontsize=15)                # Larger y-tick labels
plt.legend(fontsize=25) 

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
#plt.show()
plt.savefig("./language_distribution.png")



