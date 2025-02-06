import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
mix_outputs = "output"

base_results = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
}

rta_results = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
}

rwopt_results = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
}

for i in range(1, 11):

    with open(f'{mix_outputs}/mix{i}/base-runmix{i}') as f:
        traces = []
        for line in f:
            if 'Input trace file' in line:
                traces.append(line.split()[5].split('/')[-1][:-1])
            if 'Done:' in line:
                end = line.split()[-1]
                base_results[i].append((int(end), traces[0]))
                traces = traces[1::]


    with open(f'{mix_outputs}/mix{i}/rta-runmix{i}') as f:
        traces = []
        for line in f:
            if 'Input trace file' in line:
                traces.append(line.split()[5].split('/')[-1][:-1])
            if 'Done:' in line:
                end = line.split()[-1]
                rta_results[i].append((int(end), traces[0]))
                traces = traces[1::]


    with open(f'{mix_outputs}/mix{i}/rwopt-runmix{i}') as f:
        traces = []
        for line in f:
            if 'Input trace file' in line:
                traces.append(line.split()[5].split('/')[-1][:-1])
            if 'Done:' in line:
                end = line.split()[-1]
                rwopt_results[i].append((int(end), traces[0]))
                traces = traces[1::]


normalized_data = []

# Normalize rta_results and rwopt_results with respect to base_results
for key in base_results:
    base_cycles = [x[0] for x in base_results[key]]
    rta_cycles = [x[0] for x in rta_results[key]]
    rwopt_cycles = [x[0] for x in rwopt_results[key]]
    
    # Compute normalized values
    rta_normalized = [base_cycles[i] / rta_cycles[i] for i in range(len(base_cycles))]
    rwopt_normalized = [base_cycles[i] / rwopt_cycles[i] for i in range(len(base_cycles))]
    rwopt_speedup = [rta_cycles[i] / rwopt_cycles[i] for i in range(len(base_cycles))]
    
    # Append data to the list
    for i in range(len(base_cycles)):
        normalized_data.append({
            'Mix': key,
            'Benchmark': base_results[key][i][1],
            'FlexProf Speedup': rwopt_speedup[i]
            # 'RTA Normalized': rta_normalized[i],
            # 'FlexProf Normalized': rwopt_normalized[i]
        })

df = pd.DataFrame(normalized_data)
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Create a PDF file
pdf_filename = 'normalized_data_table.pdf'

# with PdfPages(pdf_filename) as pdf:
#     # Get unique 'Mix' values
#     mixes = df['Mix'].unique()

#     for mix in mixes:
#         # Filter DataFrame for the current 'Mix'
#         filtered_df = df[df['Mix'] == mix]
        
#         fig, ax = plt.subplots(figsize=(12, 4))  # Set the size of the figure
#         ax.axis('tight')
#         ax.axis('off')

#         # Create a table and plot it
#         table = ax.table(cellText=filtered_df.values,
#                          colLabels=filtered_df.columns,
#                          cellLoc='center',
#                          loc='center',
#                          rowLabels=filtered_df.index)

#         # Style the table
#         table.auto_set_font_size(False)
#         table.set_fontsize(10)
#         table.auto_set_column_width([0, 1, 2])
        
#         # Add a title for the current 'Mix'
#         plt.title(f'Data for {mix}')

#         # Save the table to a new page in the PDF
#         pdf.savefig(fig, bbox_inches='tight')

# print(f"PDF saved as {pdf_filename}")
# Assuming 'df' is your DataFrame and 'mixes' has been defined as you indicated
mixes = df['Mix'].unique()

# Create a bar plot for each mix on the same graph
baseline = 1.0
colors = plt.colormaps['tab10']

# Create figure
plt.figure(figsize=(20, 3.75))

# Plot bars for each mix
for i, mix in enumerate(mixes):
    # Filter data for the current mix and use .copy() to avoid chained assignment issues
    mix_data = df[df['Mix'] == mix].copy()

    # Calculate deviations from the baseline using .assign() to create a new column
    mix_data = mix_data.assign(Deviation=mix_data['FlexProf Speedup'] - baseline)

    # Plot bars (using positions shifted by 'mix' to differentiate bars of different mixes)
    plt.bar(mix_data['Benchmark'] + f'_{mix}', mix_data['Deviation'], 
            color=colors(i), label=f'Mix {mix}')

    # Calculate and print the geometric mean of FlexProf Speedup for the current mix
geom_mean_all = np.exp(np.log(df['FlexProf Speedup']).mean())
# print(f'Geometric mean for all workloads: {geom_mean_all:.4f}')

plt.axhline(y=geom_mean_all - baseline, color='r', linestyle='--', label='GMEAN All')
# Add baseline line
plt.axhline(y=0, color='black', linewidth=0.8)

# Set labels and title
plt.ylabel('Relative Speedup from RQA', fontsize=17)
plt.xlabel('Benchmark', fontsize=17)
plt.title('FlexProf Speedup from RQA for Benchmarks  (All 2%)', fontsize=17)
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))  # Format y-ticks as percentages

# Set y-axis limits
plt.ylim(-.2, .40)

# Rotate x-axis labels for better readability
plt.xticks(rotation=90,fontsize=17)
plt.yticks(fontsize=17)
plt.grid(True, which='both', linestyle='--', linewidth=0.7)
# Add legend outside to the right
plt.legend(title='', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=17)
# plt.figure(figsize=(18, 6))  # Wider and shorter
# Adjust layout to make room for the legend
# plt.tight_layout()
# Show the plot
plt.savefig("fig9.png", bbox_inches='tight', format="png")