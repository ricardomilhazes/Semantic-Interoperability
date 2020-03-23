import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mysql.connector
import seaborn as sns

sns.set()


# FETCH DATA FROM TABLE
def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="requests"
    )
    return db


def get_ids():
    db = init_db()
    cursor = db.cursor()
    sql = "SELECT idMessageHL7 FROM MessageHL7"
    cursor.execute(sql)
    return [i[0] for i in cursor.fetchall()]


def get_creation():
    db = init_db()
    cursor = db.cursor()
    sql = "SELECT CreationTime FROM MessageHL7"
    cursor.execute(sql)
    return [i[0] for i in cursor.fetchall()]


def get_elapsed():
    db = init_db()
    cursor = db.cursor()
    sql = "SELECT ElapsedTime FROM MessageHL7"
    cursor.execute(sql)
    return [i[0] for i in cursor.fetchall()]


ids = get_ids()
creation_times = get_creation()
elapsed_times = get_elapsed()

mu = np.mean(creation_times)
median = np.median(creation_times)
sigma = np.std(creation_times)
max_val = np.amax(creation_times)
min_val = np.amin(creation_times)
creation_stats = '\n'.join((
    r'$\mu=%.2f$s' % (mu, ),
    r'$\mathrm{median}=%.2f$s' % (median, ),
    r'$\sigma=%.2f$s' % (sigma, ),
    r'$max=%.2f$s' % (max_val, ),
    r'$min=%.2f$s' % (min_val, )))

mu = np.mean(elapsed_times)
median = np.median(elapsed_times)
sigma = np.std(elapsed_times)
max_val = np.amax(elapsed_times)
min_val = np.amin(elapsed_times)
elapsed_stats = '\n'.join((
    r'$\mu=%.2f$s' % (mu, ),
    r'$\mathrm{median}=%.2f$s' % (median, ),
    r'$\sigma=%.2f$s' % (sigma, ),
    r'$max=%.2f$s' % (max_val, ),
    r'$min=%.2f$s' % (min_val, )))


df = pd.DataFrame(
    {'x': ids,
     'y': creation_times,
     'z': elapsed_times
     }
)

# multiple line plot
# TODO: change linewidth to 1 if there are too many rows (e.g. 10000)
plt.plot('x', 'y', data=df, marker='',
         color='blue', linewidth=2, label='Creation Time')
plt.plot('x', 'z', data=df, marker='',
         color='red', linewidth=2, label='Elapsed Time')

plt.xlabel('Message ID')
plt.ylabel('Time (s)')

props_1 = dict(boxstyle='round', facecolor='red', alpha=0.5)
props_2 = dict(boxstyle='round', facecolor='blue', alpha=0.5)

# TODO: change positioning regarding the number of rows in the table
plt.text(0.05, 2, elapsed_stats, fontsize=10,
         verticalalignment='top', bbox=props_1)
plt.text(1300, 2, creation_stats, fontsize=10,
         verticalalignment='top', bbox=props_2)

plt.legend()
plt.show()
