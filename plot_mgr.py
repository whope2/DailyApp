#import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') #prevent 'no display error' while plotting on AWS EC2 isntance.  Enbale this line and comment out plt.show()
import matplotlib.pyplot as plt
import file_mgr
import datetime

accumulated_y = 0
def plot(x,y,accu):
    plot_file = "static/plot.png"

    #x_list
    x_type_test = x.split(',')
    if( x_type_test[0].isnumeric() == True ):
        x_is_date = False
    else:
        x_is_date = True

    if( x_is_date == True ):        
        x_list = [datetime.datetime.strptime(d,"%m/%d/%Y").date() for d in x.split(',')]
    else:
        x_list = [float(i) for i in x.split(',')]

    #y_list    
    if( accu == True ):
        global accumulated_y
        accumulated_y = 0
        y_list = [add_y(float(i)) for i in y.split(',')]
    else:
        y_list = [float(i) for i in y.split(',')]

    plt.figure(figsize=(14, 5))
    plt.plot(x_list,y_list)
    plt.ylabel('Y')
    plt.xlabel('X')
    if(x_is_date==True):
        x_list = x.split(',') #convert to string from Datetime for saving
    file_mgr.save_plot_data(x_list,y_list)
    plt.savefig(plot_file)
    #plt.show()
    return(plot_file)

def add_y(y):
    global accumulated_y
    accumulated_y = y + accumulated_y
    return accumulated_y

'''
dates = [
    "04/28/2020", 
    "05/01/2020", 
    "05/05/2020",
    "05/08/2020", 
    "05/11/2020",
    "05/15/2020", 
    "05/18/2020",
    "05/22/2020", 
    "05/25/2020",
    "05/29/2020", 
    "06/01/2020",
    "06/05/2020", 
    "06/12/2020",
    "06/16/2020", 
    "06/23/2020",
    "06/29/2020"
    ]
frames = [
    50,
    54,
    76,
    64,
    86,
    96,
    84,
    100,
    68,
    102,
    68,
    72,
    132,
    90,
    150,
    130
    ]


x = [datetime.datetime.strptime(d,"%m/%d/%Y").date() for d in dates]

accumulated_f = 0
y = [add_frames(f) for f in frames]

#plot("1.2,2,3,4","1.9,4,8,20")

plt.figure(figsize=(14, 5))
plt.plot(x,y)
plt.show()
plt.pause(0.001)

'''

#plot("1/2/2020,1/3/2020,1/5/2020","1,2,3",True)