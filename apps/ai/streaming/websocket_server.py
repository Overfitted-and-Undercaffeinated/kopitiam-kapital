"""
WebSocket server for real-time collaboration
Handles team workspace connections and message broadcasting
"""
from typing import Dict, Set, List
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for team workspaces
    
    Features:
    - Multiple workspaces
    - Broadcast to all members
    - Private messages
    - Connection tracking
    """
    
    def __init__(self):
        # workspace_id -> Set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # websocket -> user_info
        self.user_mapping: Dict[WebSocket, Dict] = {}
        
        logger.info("Initialized WebSocket Connection Manager")
    
    async def connect(
        self,
        websocket: WebSocket,
        workspace_id: str,
        user_id: str,
        user_email: str
    ):
        """
        Accept new WebSocket connection to a workspace
        
        Args:
            websocket: WebSocket connection
            workspace_id: Workspace ID
            user_id: User ID
            user_email: User email
        """
        await websocket.accept()
        
        # Add to workspace connections
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = set()
        
        self.active_connections[workspace_id].add(websocket)
        
        # Track user info
        self.user_mapping[websocket] = {
            'user_id': user_id,
            'user_email': user_email,
            'workspace_id': workspace_id,
            'connected_at': datetime.now().isoformat()
        }
        
        logger.info(f"User {user_email} connected to workspace {workspace_id}")
        
        # Notify others
        await self.broadcast_to_workspace(
            workspace_id=workspace_id,
            message={
                'type': 'user_joined',
                'user_id': user_id,
                'user_email': user_email,
                'timestamp': datetime.now().isoformat()
            },
            exclude=websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection
        
        Args:
            websocket: WebSocket to disconnect
        """
        user_info = self.user_mapping.get(websocket)
        
        if user_info:
            workspace_id = user_info['workspace_id']
            user_email = user_info['user_email']
            
            # Remove from workspace
            if workspace_id in self.active_connections:
                self.active_connections[workspace_id].discard(websocket)
                
                # Clean up empty workspaces
                if not self.active_connections[workspace_id]:
                    del self.active_connections[workspace_id]
            
            # Remove from user mapping
            del self.user_mapping[websocket]
            
            logger.info(f"User {user_email} disconnected from workspace {workspace_id}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_workspace(
        self,
        workspace_id: str,
        message: Dict,
        exclude: WebSocket = None
    ):
        """
        Broadcast message to all members of a workspace
        
        Args:
            workspace_id: Target workspace
            message: Message dict to send
            exclude: Optional WebSocket to exclude from broadcast
        """
        if workspace_id not in self.active_connections:
            logger.warning(f"Workspace {workspace_id} has no active connections")
            return
        
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        disconnected = []
        
        for connection in self.active_connections[workspace_id]:
            # Skip excluded connection
            if exclude and connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to ALL connected clients (all workspaces)"""
        for workspace_id in list(self.active_connections.keys()):
            await self.broadcast_to_workspace(workspace_id, message)
    
    def get_workspace_members(self, workspace_id: str) -> List[Dict]:
        """
        Get list of connected members in a workspace
        
        Returns:
            List of user info dicts
        """
        if workspace_id not in self.active_connections:
            return []
        
        members = []
        for ws in self.active_connections[workspace_id]:
            if ws in self.user_mapping:
                members.append(self.user_mapping[ws])
        
        return members
    
    def get_connection_count(self, workspace_id: str = None) -> int:
        """
        Get connection count
        
        Args:
            workspace_id: Specific workspace (optional)
        
        Returns:
            Connection count
        """
        if workspace_id:
            return len(self.active_connections.get(workspace_id, set()))
        else:
            return sum(len(conns) for conns in self.active_connections.values())
    
    def get_workspace_count(self) -> int:
        """Get number of active workspaces"""
        return len(self.active_connections)

# Global connection manager instance
connection_manager = ConnectionManager()

