from __future__ import print_function
import httplib2
import os

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from SQL import add_event, add_member, show_members, patch_EandM, find_event, is_event, fullfill, init_tables
from credentials import cid, c_i
import datetime

_mod = 0

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Occupancy'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def init(credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def api_import_events(max_eve, service, month, day, mod=_mod):
    storage = dict()
    if int(month) < 10:
        month = '0'+str(month)
    else:
       month = str(month)
    if int(day) < 10:
        day = '0'+str(day)
    else:
        day = str(day)
    now = datetime.datetime.now().date().isoformat() + 'T00:00:00.000000Z'
    enn = datetime.datetime.now().date().isoformat() + 'T23:01:00.000000Z'
    d = str(now)
    now = d[:5] + month[-2:]+ '-' + day[-2:] + d[10:]
    d = str(enn)
    enn = d[:5] + month[-2:]+ '-' + day[-2:] + d[10:]

    message = f"На {day} записались: \n"
    try:
        eventsResult = service.events().list(
          calendarId=cid[mod], timeMin=now, timeMax=enn, maxResults=max_eve, singleEvents=True,
          orderBy='startTime').execute()
        events = eventsResult.get('items', [])
    except BaseException as be:
        print("gc.a_i_e import error: ", type(be), be)

    if not events:
        return 'Ан-нет, никто не записался.'
    total = 0
    d = now.split('-')
    y = int(d[0])
    m = int(d[1])
    d = int(d[2][:2])

    for event in events:
        count = 0
        e_i = event['id']
        row = ""
        start = event['start'].get('dateTime', event['start'].get('date'))
        try:
           st = int(start[11:13])
        except ValueError:
            break
        if int(start[8:10]) > int(day):
            break
        elif int(start[5:7]) != m:
            break

        add_event(event['id'], y, m, d, int(start[11:13]))

        archers = event['summary'].split(',')
        a_o = 0
        for archer in archers:
            archer = archer.strip()
            archer = archer.capitalize()
            storage[archer] = storage.get(archer, 0) + 1
            add_member(e_i, archer, a_o)
            a_o += 1
            row += archer
            row += ", "
            total += count
        message += f"В {start[11:16]} - {row[:-2]}.\n"
    return message

def api_update_event(service, month, day, time, text, description="", year=datetime.date.today().year, mod = _mod):
#    print(mod)
    text = text.capitalize()
    e_i = find_event(year,month,day,time)
    var = -1
    if not e_i:
        create_event(service, int(month), int(day), int(time), text, description)
        var = 0
    else:
        eventsResult = service.events().get(
          calendarId=cid[mod], eventId = e_i).execute()
        old_desc = eventsResult.get('description')
        description = old_desc + description
        try:
            service.events().delete(calendarId=c_i[mod], eventId = e_i).execute()
        except BaseException as be:
                print("While event deleting Error raised:",type(be), be)
        archers = ''
        members = show_members(year, month, day, time)
        if  not members:
            print("Update:\n\tMember addition:\n\t\tnot_members ERROR")
            pass
        else:
            for member in members:
                a = str(member)
                archers += a[2:-3]
                archers += ", "
            try:
                print(text)
                patch_EandM(str(e_i))
                archers += text.capitalize()
                lei = create_event(service, int(month), int(day), int(time), str(archers), description)
            except BaseException as be:
                print("Update:\n\tPatching error:\n\t\t",type(be), be)
            var = 1
    return var

def del_from_event(service, month, day, time, name, description="", year=datetime.date.today().year, mod = _mod):
    var = -1
    members = show_members(year,month,day,time)
    n = (str(name).capitalize(),)
    if n in members:
        members.remove(n)
    else:
        print(f"no {name} has been found")
        return var
    if len(members) == 1:
        if(members[0] == ('',)):
            var = 0
    else:
        var = 1
    try:
        e_i = find_event(year,month,day,time)
        print("try to delete", e_i)
        service.events().delete(calendarId=c_i[mod], eventId = e_i).execute()
        if var == 0:
            return var
    except BaseException as be:
        print("While event deleting Error raised:",type(be), be)
    archers = ''
    for member in members:
        a = str(member).capitalize()
        archers += a[2:-3].capitalize()
        archers += ", "
    try:
        patch_EandM(str(e_i))
        lei = create_event(service, int(month), int(day), int(time), str(archers), description)
    except BaseException as be:
        print("GC.Update:\n\tPatching error:\n\t\t", type(be), be)
        var = -1
    return var



def create_event(service, month, day, time, summary, description = "", year=datetime.date.today().year, mod=_mod):
   if month < 10:
      month = '0'+str(month)
   else:
       month = str(month)
   if day < 10:
      day = '0'+str(day)
   else:
       day = str(day)
   if time < 10:
       tim1 = '0'+str(time)
   else:
        tim1 = str(time)
   if time + 1 < 10:
       tim2 = '0'+str(time+1)
   else:
       tim2 = str(time+1)
   dts = f'{year}-' + str(month) +'-'+day +'T'+ str(tim1)+':00:00'
   dte = f'{year}-' + str(month) +'-'+day +'T'+ str(tim2)+':00:00'
   event = {
  'summary': summary,
  'description': description,
  'start': {
    #'dateTime': '2017-12-03T09:00:00-07:00',
    'dateTime': dts,
    'timeZone': 'Europe/Moscow',
  },
  'end': {
    'dateTime': dte,
    'timeZone': 'Europe/Moscow',
  },
  'recurrence': [
 #    'RRULE:FREQ=DAILY;COUNT=1'
  ],
  'attendees': [],
  'reminders': {
    'useDefault': False,
    'overrides': [
#      {'method': 'email', 'minutes': 24 * 60},
  #    {'method': 'popup', 'minutes': 10},
    ],
  },
}

   event = service.events().insert(calendarId=c_i[mod], body=event).execute()
   members = summary.split(',')
   id = event['id']
   add_event(id, int(year),int(month),int(day), int(time))
   a_o = 0
   for member in members:
       add_member(id, member.strip().capitalize(), a_o)
       a_o +=1
   return id
