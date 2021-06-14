import sys
import logging
import local
import requests
import csv
import argparse
import collections

locations_and_number_residents={}
list_characters=[]


def location_and_residents(url=local.URL_LOCATIONS):
#creates a dictionary with the location and number of characters   
    
    req = requests.get(url)
    if req.status_code != 200:
        logging.error('Error calling episodes api')
        sys.exit()
    
    req = req.json()
    locations = req['results']
    info = req['info']
    
    for loc in locations:
        locations_and_number_residents[loc['name']] = len(loc['residents'])
    
    if info['next']:
        location_and_residents(info['next'])

    return locations_and_number_residents

            

def get_characters(url=local.URL_CHARACTER):
#Creates a dictionary with the main information of the characters
#And returns the dictionary ordered by the number of characters in the episode in which it appears
    
    req = requests.get(url)
    if req.status_code != 200:
        logging.error('Error calling characters api')
        sys.exit()
    
    req = req.json()
    characters = req['results']
    info = req['info']

    for character in characters:
        location = str(character.get('location').get('name', 'Unknow'))        
        c = {
            'name': character['name'],
            'status': character['status'],
            'gender': character['gender'],
            'episodes': len(character['episode']),
            'location': location,
        }
        
        if location != 'unknown':
            c['residents'] = locations_and_number_residents[location]
                
        
        list_characters.append(c)
    
    if info['next']:
        get_characters(info['next'])
    
    return sorted(list_characters, key=lambda k: k['episodes'], reverse=True)
    


def generate_characters_csv(list_characters):
#Generates a csv file with character information
    
    header = ['Name', 'Status', 'Gender', 'Number of episodes', 'Location', 'Number of residents',]
    try:
        with open('characters.csv', 'w', encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=';')

            writer.writerow(header)

            for c in list_characters:
                writer.writerow(c.values())
    except:
        logging.error('error creating csv')
def number_episodes(n, url=local.URL_EPISODES):
#method to obtain the number of episodes with the number of characters
#requested in the program call
    
    count = 0    
    req = requests.get(url)

    if req.status_code != 200:
        logging.error('Error calling characters api')
        sys.exit()
    
    req = req.json()
    episodes = req['results']
    info = req['info']

    for ep in episodes:
        if n == len(ep.get('characters')):
            count += 1
    
    print(count)

def main(n):    
    logging.basicConfig(filename=local.LOG_PATH,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        encoding='utf-8',
                        level=logging.DEBUG)

    logging.info('Start')
    
    location_and_residents()    
    list_characters = get_characters()    
    generate_characters_csv(list_characters)    
    number_episodes(n)
    
    logging.info('Finish')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, action = 'store', dest = 'n', required = True)
    args = parser.parse_args()
    main(args.n)