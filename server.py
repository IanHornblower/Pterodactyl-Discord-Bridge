class Server:
    def __init__(self, json, check_status_method):
        self.get_server_status = check_status_method

        self.name, self.server_id = self.parse_json(json) # add more data if needed
        self.current_state, self.uptime, self.cpu_usage, self.memory_usage, self.size_on_disk = self.get_server_data()

    def parse_json(self, json):
        json = json['attributes']

        name = json['name']
        server_id = json['identifier']
        
        internal_id = json['internal_id']
        uuid = json['uuid']
        is_node_under_maintenance = json['is_node_under_maintenance']

        return name, server_id

    def get_server_data(self):
        json = self.get_server_status(self.server_id)['attributes']

        current_state = json['current_state']
        is_suspended = json['is_suspended'] # add to return if needed

        json = json['resources']

        raw_memory_usage = json['memory_bytes'] # in bytes
        raw_size_on_disk = json['disk_bytes'] # in bytes
        raw_uptime = json['uptime'] # uptime in milliseconds

        cpu_usage = json['cpu_absolute'] # in precentage: ie: 9.35 = 9.35%

        uptime = convert_to_dhm(raw_uptime) # tuple of days, hours, minutes
        memory_usage = raw_memory_usage / 1e+9 # in gb
        size_on_disk = raw_size_on_disk / 1e+9 # in gb

        return current_state, uptime, cpu_usage, memory_usage, size_on_disk

    def is_online(self):
        return self.current_state.__eq__('running')

    def __str__(self): # add to this as needed
        return f"Name: {self.name}  ID: {self.server_id}  Status: {self.current_state}"
    
def convert_to_dhm(miliseconds):
    seconds = miliseconds / 1000

    SECONDS_IN_A_MINUTE = 60
    SECONDS_IN_AN_HOUR = 60 * SECONDS_IN_A_MINUTE
    SECONDS_IN_A_DAY = 24 * SECONDS_IN_AN_HOUR

    days = seconds // SECONDS_IN_A_DAY
    seconds %= SECONDS_IN_A_DAY
    hours = seconds // SECONDS_IN_AN_HOUR
    seconds %= SECONDS_IN_AN_HOUR
    minutes = seconds // SECONDS_IN_A_MINUTE

    return days, hours, minutes