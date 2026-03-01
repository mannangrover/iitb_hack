import time
import uuid
from typing import Dict, Any, Optional, List


class ConversationManager:
    """Enhanced conversation context manager with full history tracking."""

    def __init__(self, ttl_seconds: int = 3600, max_history: int = 20):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.max_history = max_history

    def create_session(self) -> str:
        """Create a new conversation session"""
        sid = str(uuid.uuid4())
        self.sessions[sid] = {
            "created_at": time.time(),
            "updated_at": time.time(),
            "last_intent": None,
            "last_entities": {},
            "conversation_history": [],  # Full Q&A history for LLM context
            "extracted_context": {},     # Context from previous queries
            "pending_clarification": None,
        }
        return sid

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session and handle expiration"""
        s = self.sessions.get(session_id)
        if not s:
            return None
        # Check if session has expired
        if time.time() - s["updated_at"] > self.ttl:
            del self.sessions[session_id]
            return None
        return s

    def update_session(
        self, 
        session_id: str, 
        user_query: str,
        intent: str, 
        entities: Dict[str, Any], 
        result: Dict[str, Any],
        ai_response: str
    ):
        """Update session with new query, intent, entities, and response"""
        s = self.sessions.get(session_id)
        if not s:
            # Create if missing
            session_id = self.create_session()
            s = self.sessions[session_id]
        
        # Update last known intent and entities
        s["last_intent"] = intent
        s["last_entities"].update(entities or {})
        
        # Store full conversation turn
        s["conversation_history"].append({
            "timestamp": time.time(),
            "user_query": user_query,
            "intent": intent,
            "entities": dict(entities or {}),
            "response": ai_response,
            "data_summary": {
                "total_count": result.get("total_count"),
                "key_metrics": self._extract_key_metrics(result)
            }
        })
        
        # Keep only last N entries to manage memory
        if len(s["conversation_history"]) > self.max_history:
            s["conversation_history"] = s["conversation_history"][-self.max_history:]
        
        # Extract and update context from latest result
        s["extracted_context"].update(self._extract_context(result, entities))
        s["updated_at"] = time.time()

    def merge_entities(self, session_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Merge current query entities with session context, preserving important context"""
        s = self.get_session(session_id)
        if not s:
            return entities or {}
        
        last = s.get("last_entities", {})
        current = entities or {}
        
        # Start with previous context
        merged = dict(last)
        
        # Update with current entities (all additive except for critical grouping keys)
        merged.update(current)
        
        # Preserve important keys UNLESS explicitly overridden
        # If previous had comparison_dimension and current doesn't have it explicitly,
        # preserve it (the current query is likely just adding filters)
        if 'comparison_dimension' in last and 'comparison_dimension' not in current:
            merged['comparison_dimension'] = last['comparison_dimension']
        
        # Same for segment_by
        if 'segment_by' in last and 'segment_by' not in current:
            merged['segment_by'] = last['segment_by']
        
        return merged

    def get_conversation_context(self, session_id: str) -> str:
        """Generate context string from conversation history for LLM"""
        s = self.get_session(session_id)
        if not s or not s.get("conversation_history"):
            return ""
        
        history = s["conversation_history"]
        context_lines = []
        
        for turn in history[-5:]:  # Include last 5 turns
            context_lines.append(f"User: {turn['user_query']}")
            context_lines.append(f"Assistant: {turn['response'][:200]}...")  # Summary
            context_lines.append("")
        
        return "\n".join(context_lines) if context_lines else ""

    def get_resolved_entities(self, session_id: str) -> Dict[str, Any]:
        """Get all entities accumulated from conversation"""
        s = self.get_session(session_id)
        if not s:
            return {}
        
        resolved = {}
        # Merge last entities and context
        resolved.update(s.get("last_entities", {}))
        resolved.update(s.get("extracted_context", {}))
        return resolved

    def _extract_context(self, result: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Extract valuable context from analysis result"""
        context = {}
        
        if entities.get("category"):
            context["last_category"] = entities["category"]
        if entities.get("state"):
            context["last_state"] = entities["state"]
        if entities.get("device_type"):
            context["last_device"] = entities["device_type"]
        
        # Store data insights for context
        if result.get("statistics"):
            context["last_avg_amount"] = result["statistics"].get("average_amount")
        
        return context

    def _extract_key_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from analysis for storage"""
        metrics = {}
        
        if "statistics" in result:
            stats = result["statistics"]
            metrics["average_amount"] = stats.get("average_amount")
            metrics["total_amount"] = stats.get("total_amount")
        
        if "fraud_rate_percent" in result:
            metrics["fraud_rate"] = result["fraud_rate_percent"]
        
        return metrics

    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def set_pending_clarification(self, session_id: str, clarification: Optional[Dict[str, Any]]) -> None:
        """Set or clear pending clarification for a session"""
        s = self.sessions.get(session_id)
        if not s:
            return
        s["pending_clarification"] = clarification

    def get_pending_clarification(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get pending clarification for a session"""
        s = self.get_session(session_id)
        if not s:
            return None
        return s.get("pending_clarification")
