events_file = open('events.html', 'r')
print(events_file.readlines()[0:5])
events_file.close()

with open('events.html', 'r') as f:
  print(f.readlines()[0:5]) 
