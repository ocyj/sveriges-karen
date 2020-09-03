from os import listdir
from os.path import isfile, join
import csv
import matplotlib.pyplot as plt

se_data_path = r'_data\BE0001AN.csv'
us_data_path = r'_data\ssa_names'
us_file_names = [file_name for file_name in listdir(us_data_path) if isfile(join(us_data_path, file_name)) and file_name.endswith('.txt')]

# Swedish data is from 1920 (including) to 2019 (including)
# US data is from 1880 (including) to 2018 (including)

# Load Karen-data
def find_year_of_us_file(file_name: str) -> int:
    return int(file_name.replace('yob','').replace('.txt',''))

us_file_names = [file for file in us_file_names if 1920 <= find_year_of_us_file(file) <= 2018]

def extract_number_of_karens_from_file(file_name: str):
    year = find_year_of_us_file(file_name)
    with open(f'{us_data_path}\\{file_name}') as f:
        karens = [int(name.replace('Karen,F,','')) for name in f.readlines() if name.startswith('Karen,F,')][0]
        return (year, karens)

karen_stats = [(year, karens) for year, karens in map(extract_number_of_karens_from_file, us_file_names)]
karen_peak_year, karen_peak_number = max(karen_stats, key=lambda x: x[1])
print(f'Popularity of Karen peaked in {karen_peak_year} with {karen_peak_number} girls born.')

karen_stats_normalized = [(year, karens/karen_peak_number) for year, karens in karen_stats]
year, karens_normalized = zip(*karen_stats_normalized)

# Swedish data
with open(se_data_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    years = [int(fn) for fn in reader.fieldnames[1:]]
    swedish_names = []
    for name in reader:
        name_dict = {'name': name['tilltalsnamn']}
        name_dict['data'] = [(int(year), int(number) if number != '..' else None) for year, number in name.items() if year != 'tilltalsnamn']
        _, peak_number = max(name_dict['data'], key=lambda x: x[1] or 0)
        name_dict['normalized_data'] = [(year, (number_born or 0)/peak_number) for year, number_born in name_dict['data']]
        swedish_names.append(name_dict)


def karen_likeness(swedish_name):
    years, numbers = zip(*swedish_name['normalized_data'])
    return 1/sum([abs(karen_normalized - swedish_name_normalized)
                for (karen_normalized, swedish_name_normalized)
                in zip(karens_normalized, numbers[:-1])
                if swedish_name_normalized is not None])

swedish_names.sort(key=karen_likeness, reverse=True)
print('Top five Karen-like swedish names:')
print(*[f"{i+1}:\t{name['name']}\t({karen_likeness(name):.4f})" for i, name in enumerate(swedish_names[:5])], sep='\n')
print('\nTop five Karen-unlike swedish names:')
print(*[f"{i+1}:\t{name['name']}\t({karen_likeness(name):.4f})" for i, name in enumerate(swedish_names[:-6:-1])], sep='\n')

year, karens_normalized = zip(*karen_stats_normalized)

csfont = {'fontname':'Comic Sans MS'}

plt.title('Karen vs Lena (et al.)',**csfont)

plt.plot(year, [100*k for k in karens_normalized], linewidth=4)
plt.plot(year, [100*n for _,n in swedish_names[0]['normalized_data'][:-1]])

plt.legend(['Karen', 'Lena'])
plt.grid(color='grey', linestyle='dashed', linewidth=1, alpha=0.5)
plt.xlabel('Year', **csfont)
plt.xlabel('Year')
plt.xlim([1920, 2018])
plt.ylim([0, 110])
plt.ylabel('%', **csfont)
plt.ylabel('%')
plt.show()
