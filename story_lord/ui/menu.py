from typing import Dict, List, Optional, Any, Callable
from pydantic import BaseModel, Field

class MenuNode(BaseModel):
    id: str
    label: str
    description: str = ""
    # IDs of children. If empty, it's a leaf/action node usually.
    children: List[str] = [] 
    # specific handler key (e.g., 'NAV_GEN')
    param: Optional[str] = None
    # Static props for this node
    props: Dict[str, Any] = {}

class MenuManager:
    def __init__(self, tree: Dict[str, dict]):
        # Convert raw dict tree to Models
        self.tree: Dict[str, MenuNode] = {}
        for k, v in tree.items():
            self.tree[k] = MenuNode(id=k, **v)
            
        self.history: List[str] = [] # Stack of node IDs
        self.curr_id: str = "ROOT"
        self.selected_idx: int = 0
        self.context: Dict[str, Any] = {} # Shared dynamic context

    def get_current_node(self) -> MenuNode:
        return self.tree.get(self.curr_id)

    def get_children(self) -> List[MenuNode]:
        node = self.get_current_node()
        if not node: return []
        return [self.tree[child_id] for child_id in node.children if child_id in self.tree]

    def navigate_down(self):
        children = self.get_children()
        if not children: return
        self.selected_idx = min(len(children) - 1, self.selected_idx + 1)

    def navigate_up(self):
        self.selected_idx = max(0, self.selected_idx - 1)

    def enter_child(self) -> Optional[str]:
        """
        Returns the action param string if it's an action node.
        Returns None if we just navigated deeper into the menu.
        """
        children = self.get_children()
        if not children: return None
        
        target = children[self.selected_idx]
        
        if target.children:
            # It's a directory, go inside
            self.history.append(self.curr_id)
            self.curr_id = target.id
            self.selected_idx = 0
            
            # Merge props into context
            self.context.update(target.props)
            return None
        else:
            # It's a leaf, return action param
            return target.param

    def go_back(self):
        if self.history:
            self.curr_id = self.history.pop()
            self.selected_idx = 0
            # Note: Context popping is harder with simple merge. 
            # Ideally we'd keep a context stack too if we need strict scoping.
            # For now, simplistic is fine.

    def set_root(self, root_id: str):
        self.history.clear()
        self.curr_id = root_id
        self.selected_idx = 0
