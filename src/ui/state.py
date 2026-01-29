class AppState:
    def __init__(self):
        self.active_screen = "LAUNCHER" # Start at Launcher
        self.status_message = "Ready."
        self.sync_issues = []
        
        # Story State
        self.is_story_loaded = False
        self.story_path = None
        self.active_focus_zone = "SIDEBAR" # "SIDEBAR" or "CONTENT"
        
        # Explorer State
        self.exp_mode = "CATEGORIES" # "CATEGORIES" or "FILES"
        self.exp_category = None # Current selected category
        self.exp_files = [] # Current list relative to mode
        self.exp_selected_idx = 0
        
        # Gen State
        self.gen_cat_idx = 0

        # Debug
        self.show_debug = False
        
    def set_status(self, msg):
        self.status_message = msg
        
    def load_story(self, path):
        self.story_path = path
        self.is_story_loaded = True

# Singleton instance
state = AppState()
