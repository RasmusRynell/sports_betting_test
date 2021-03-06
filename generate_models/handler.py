import requests
import json
import msgpack

class api:
    '''
        Handles all communication with nhl-api and caches information for future use.
    '''
    def __init__(self, base, load_from_file = False, save_cache = True):
        self.base = base
        self.cached_information = {}
        self.total_reqs = 0
        self.non_cached = 0
        self.cached_reqs = 0
        self.save_cache = save_cache

        # If we want to load in already saved cache, do so
        if load_from_file:
            self.read_saved_api_cache()

    def send_request(self, req, force_send = False):
        self.total_reqs +=1

        if req not in self.cached_information or force_send:
            response_json = requests.get(self.base + str(req)).json()
            self.non_cached += 1
            if ("message" not in response_json):
                self.cached_information[req] = response_json
            else:
                return response_json
        else:
            self.cached_reqs += 1
        return self.cached_information[req]

    def print_cache(self):
        print("Base: " + self.base)
        if self.cached_information:
            print("Total reqs: " + str(self.total_reqs))
            print("non cached reqs: " + str(self.non_cached))
            print("cached reqs: " + str(self.cached_reqs))
        else:
            print("No information!")

    def save(self):
        if self.save_cache:
            with open("./data/saved_cache.json", "wb") as f:
                f.write(msgpack.packb(self.cached_information))

    def read_saved_api_cache(self):
        try:
            with open('./data/saved_cache.json', "rb") as f:
                self.cached_information = msgpack.unpackb(f.read())
        except Exception as e:
            print("Could not find file saved_cache.json")
