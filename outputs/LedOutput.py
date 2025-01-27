from outputs.BaseOutput import BaseOutput

class LedOutput(BaseOutput):

    def __init__(self, service_name, config=None, debug=False):
        super().__init__(service_name, config, debug)

    def setup(self):
        pass
    
    def loop(self):
        pass
    
    def trigger_action(self, data):
        pass

    def cleanup(self):
        pass