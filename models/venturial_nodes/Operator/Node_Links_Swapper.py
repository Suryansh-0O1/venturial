import bpy

def reorder_links(self,input_Socket:str):
    input_socket = self.inputs.get(input_Socket)
    if not input_socket:
        return

    # Store the desired order 
    desired_order = [item.name for item in self.link_order]
    print(f"Storing desired link order: {desired_order}")

    # Capture all the source nodes and socket
    from_links = {}
    for link in input_socket.links:
        from_node = link.from_node
        from_socket = link.from_socket
        from_links[from_node.name] = from_socket 
        print(f"Captured link from {from_node.name}")

    # Remove all existing links
    old_links = list(input_socket.links)
    for link in old_links:
        print(f"Removing link from {link.from_node.name}")
        self.id_data.links.remove(link)

    # Reconnect using desired order
    print(f"Reconnecting links : {desired_order}")
    for name in desired_order:
        if name in from_links:
            from_socket = from_links[name]
            print(f"Reconnecting link from {name}")
            self.id_data.links.new(from_socket, input_socket)
        else:
            print(f"  > Link source '{name}' not found in captured links (this shouldn't happen)")
            
def path_from_id(self):
        # Get the node tree and node name
        node_tree = self.id_data
        node_name = self.name
        
        # Find the index of this node in the node tree
        node_index = -1
        for i, node in enumerate(node_tree.nodes):
            if node == self:
                node_index = i
                break
        
        if node_index == -1:
            print(f"Error: Node {node_name} not found in node tree")
            return ""
        
        # Return the path to the node in the context
        return f"space_data.node_tree.nodes[{node_index}]"

class NODE_OT_move_link_order(bpy.types.Operator):
    bl_idname = "node.move_link_order"
    bl_label = "Move Link Order"

    node_path: bpy.props.StringProperty()
    direction: bpy.props.EnumProperty(items=[('UP', "Up", ""), ('DOWN', "Down", "")])
    index: bpy.props.IntProperty()

    def execute(self, context):
        try:
            # Get the node from the context using the path and call move link
            node = eval(f"context.{self.node_path}")
            if node:
                node.move_link(self.index, self.direction)
                return {'FINISHED'}
            else:
                print(f"Error: Could not find node at path {self.node_path}")
                return {'CANCELLED'}
        except Exception as e:
            print(f"Error moving link: {e}")
            return {'CANCELLED'} 