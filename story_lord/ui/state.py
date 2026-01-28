class AppState:
    def __init__(self):
        self.active_screen = "LAUNCHER" # Start at Launcher
        self.status_message = "Ready."
        self.sync_issues = []
        
        # Story State
        self.is_story_loaded = False
        self.story_path = None
        
        # Explorer State
        self.exp_files = []
        self.exp_selected_idx = 0
        
        # Gen State
        self.gen_cat_idx = 0
        
    def set_status(self, msg):
        self.status_message = msg
        
    def load_story(self, path):
        self.story_path = path
        self.is_story_loaded = True

# Singleton instance
state = AppState()
