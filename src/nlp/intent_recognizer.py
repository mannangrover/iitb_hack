import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import get_close_matches

@dataclass
class Intent:
    type: str  # e.g., "descriptive", "comparative", "user_segmentation", "risk_analysis"
    confidence: float
    entities: Dict[str, str]

class IntentRecognizer:
    """
    Recognizes business intents from natural language queries
    Enhanced to recognize entities from actual database schema:
    - merchant_category (merchants)
    - sender_state, receiver_state
    - sender_age_group, receiver_age_group
    - transaction_type, transaction_status
    - sender_bank, receiver_bank
    - device_type, network_type
    - temporal: hour_of_day, day_of_week, is_weekend
    """
    
    def __init__(self):
        # Merchant categories from data
        self.merchant_categories = [
            "Food", "Entertainment", "Travel", "Shopping", "Utilities", 
            "Healthcare", "Education", "Bills", "Downloads", "Other", "Groceries",
            "Restaurants", "Hotels", "Airlines", "Retail", "Services"
        ]
        
        self.transaction_types = [
            "P2P", "Merchant", "Bill", "Recharge", "Investment",
            "Withdrawal", "Transfer", "Subscription"
        ]
        
        self.devices = ["iOS", "Android", "Web", "USSD"]
        
        self.networks = ["WiFi", "4G", "5G", "3G", "2G"]
        
        self.states = [
            "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana",
            "Gujarat", "Rajasthan", "Punjab", "West Bengal", "Uttar Pradesh",
            "Andhra Pradesh", "Haryana", "Madhya Pradesh", "Bihar", "Odisha",
            "Jharkhand", "Uttarakhand", "Himachal Pradesh", "Assam", "Kerala"
        ]
        
        self.age_groups = ["13-18", "18-25", "25-35", "35-45", "45-55", "55+"]
        
        self.banks = [
            "HDFC", "ICICI", "SBI", "Axis", "IDBI", "PNB", "BOB", "Union",
            "Kotak", "IndusInd", "YES", "RBL", "Federal", "Airtel",
            "Google Pay", "PhonePe", "Paytm", "Amazon Pay"
        ]
        
        self.transaction_statuses = ["Success", "Failed", "Pending", "Declined", "Timeout"]
        
    def fuzzy_match(self, user_input: str, valid_options: List[str], threshold: float = 0.8) -> Optional[str]:
        """
        Fuzzy match user input against valid list of options.
        Handles typos, partial matches, and case variations.
        
        Args:
            user_input: Text from user query (e.g., "Mahrashtra", "foo")
            valid_options: List of valid canonical values (e.g., all states, categories)
            threshold: Similarity score threshold (0-1, default 0.8 = 80%)
        
        Returns:
            Best match if found above threshold, else None
        """
        if not user_input or not valid_options:
            return None
        
        # Try exact match first (case insensitive)
        user_lower = user_input.lower()
        for option in valid_options:
            if option.lower() == user_lower:
                return option
        
        # Try fuzzy match
        matches = get_close_matches(user_input, valid_options, n=1, cutoff=threshold)
        return matches[0] if matches else None
        
    def recognize_intent(self, query: str) -> Intent:
        """
        Recognize intent from natural language query
        Returns intent type and extracted entities
        """
        query_lower = query.lower()
        
        # Determine intent type
        intent_type = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)

        # Normalize: if user asked for segmentation (e.g., 'state wise', 'by state')
        # ensure segment_by is populated from comparison_dimension when present
        if intent_type == 'user_segmentation':
            if 'comparison_dimension' in entities and 'segment_by' not in entities:
                conv = {
                    # default to sender-side fields for ambiguous segments
                    'state': 'sender_state',
                    'age_group': 'sender_age_group',
                    'age': 'sender_age_group',
                    'category': 'merchant_category',
                    'merchant_category': 'merchant_category',
                    'device': 'device_type',
                    'device_type': 'device_type',
                    'network': 'network_type',
                    'bank': 'sender_bank',
                    'sender_bank': 'sender_bank',
                    'receiver_bank': 'receiver_bank',
                    'status': 'transaction_status',
                    'type': 'transaction_type'
                }
                entities['segment_by'] = conv.get(entities['comparison_dimension'], entities['comparison_dimension'])
        
        # Calculate confidence based on entity extraction
        confidence = min(0.95, 0.7 + len(entities) * 0.05)
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            entities=entities
        )
    
    def recognize_intent_with_context(self, query: str, conversation_context: Optional[Dict[str, str]] = None) -> Intent:
        """
        Recognize intent with conversation context for follow-up questions.
        Use previous entities to fill in missing context in follow-ups.
        
        Example:
        - Q1: "What's the avg transaction in Food category?"
        - Q2: "How about Entertainment?" -> Uses 'category' context from Q1
        """
        initial_intent = self.recognize_intent(query)
        
        # If we have conversation context, fill missing entities from it
        if conversation_context:
            # Check for follow-up patterns that reference previous context
            if self._is_followup_question(query):
                # Inherit entities from context unless explicitly overridden
                for key, value in conversation_context.items():
                    if key not in initial_intent.entities and value:
                        initial_intent.entities[key] = value
        
        return initial_intent
    
    def _is_followup_question(self, query: str) -> bool:
        """
        Detect if this is a follow-up question that might need context.
        Identifies patterns like "how about", "what about", "compare with", etc.
        """
        followup_patterns = [
            "how about", "what about", "and", "compared to", "vs", "versus",
            "like", "similar", "different", "another", "other", "then what",
            "what else", "any other", "more details", "tell me more",
            "break it down", "segment", "split", "separately"
        ]
        
        query_lower = query.lower()
        for pattern in followup_patterns:
            if pattern in query_lower:
                return True
        
        return False
    
    def _classify_intent(self, query: str) -> str:
        """Classify query into intent type"""
        
        query_lower = query.lower()
        
        # Risk analysis patterns (highest priority)
        risk_keywords = [
            "fraud", "risk", "failed", "failure rate", "failure", "flagged", "suspicious",
            "anomaly", "unusual", "problem"
        ]
        
        # Comparative analysis patterns - INCLUDES "TOP X" QUERIES
        comparative_keywords = [
            "compare", "comparison", "versus", "vs", "difference", "better", "worse",
            "higher", "lower", "faster", "slower", "more than", "less than",
            "between", "across", "top", "top 3", "top 5", "top 10",
            "best", "worst", "highest", "lowest", "ranking", "ranked"
        ]
        # support explicit grouping/comparison phrases
        comparative_keywords += ["group by", "grouped by", "sum by", "total by", "amount by", "per bank", "by bank", "bank wise", "bank-wise"]
        
        # Segmentation patterns
        segmentation_keywords = [
            "age group", "state", "region", "segment", "demographic",
            "by age", "by state", "by device", "by network", "users in", "by category"
        ]
        
        # Descriptive analysis patterns
        descriptive_keywords = [
            "average", "mean", "total", "sum", "how much", "peak",
            "least", "analyze", "what are", "what is",
            "trend", "pattern", "distribution"
        ]

        # Check for risk keywords FIRST (before grouping patterns)
        # Risk analysis with grouping: "fraud rate by state", "failure rate by bank"
        has_risk_keyword = any(kw in query_lower for kw in risk_keywords)
        if has_risk_keyword:
            return "risk_analysis"

        # include bank-related comparative/segmentation triggers (only if NOT risk)
        if any(kw in query_lower for kw in ["bank wise", "bank-wise", "by bank", "per bank", "per-bank", "amount by bank", "amount per bank", "of bank", "of banks", "of the banks", "with bank", "with banks"]):
            return "comparative"

        # If user asks for grouping or aggregation (sum/total/count) prefer comparative/segmentation
        if any(kw in query_lower for kw in ["group by", "grouped by", "sum by", "total by", "count by", "amount by", "per "]):
            return "comparative"

        # Explicit grouping by dimension
        if re.search(r"\bby\s+(receiver\s+bank|sender\s+bank|bank|device|device\s+type|network|networks|state|states|age|age\s+group|category|merchant|transaction\s+type)\b", query_lower):
            return "comparative"
        
        # "total/sum/amount ... by X" patterns are comparative (e.g., "total transaction value by state")
        if any(agg in query_lower for agg in ["total", "sum", "amount", "value"]) and any(dim in query_lower for dim in ["by state", "by age", "by category", "by device", "by bank", "state wise", "age wise", "category wise"]):
            return "comparative"
        
        # Priority ordering: comparative -> segmentation -> descriptive
        for keyword in comparative_keywords:
            if keyword in query_lower:
                return "comparative"

        for keyword in segmentation_keywords:
            if keyword in query_lower:
                return "user_segmentation"

        for keyword in descriptive_keywords:
            if keyword in query_lower:
                return "descriptive"

        return "descriptive"  # Default
    
    def _extract_entities(self, query: str) -> Dict[str, str]:
        """
        Extract entities from query based on real database schema.
        Uses fuzzy matching to handle typos and spelling mistakes.
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract merchant categories (fuzzy match)
        for category in self.merchant_categories:
            if category.lower() in query_lower:
                # Exact substring found
                entities['merchant_category'] = category
                break
        if 'merchant_category' not in entities:
            # Try fuzzy match for typos
            for word in query.split():
                matched = self.fuzzy_match(word, self.merchant_categories, threshold=0.75)
                if matched:
                    entities['merchant_category'] = matched
                    break
        
        # Extract transaction types
        for tx_type in self.transaction_types:
            if tx_type.lower() in query_lower:
                entities['transaction_type'] = tx_type
                break
        
        # Extract transaction status
        for status in self.transaction_statuses:
            if status.lower() in query_lower:
                entities['transaction_status'] = status
                break
        
        # Extract devices (support multiple devices for comparisons)
        devices_found = []
        for device in self.devices:
            if device.lower() in query_lower:
                devices_found.append(device)
        # Try fuzzy match for typos
        if not devices_found:
            for word in query.split():
                matched = self.fuzzy_match(word, self.devices, threshold=0.75)
                if matched and matched not in devices_found:
                    devices_found.append(matched)
        
        if devices_found:
            if len(devices_found) > 1:
                entities['comparison_dimension'] = 'device_type'
                entities['comparison_values'] = devices_found
            else:
                entities['device_type'] = devices_found[0]
        
        # Extract networks (fuzzy match for typos)
        for network in self.networks:
            if network.lower() in query_lower:
                entities['network_type'] = network
                break
        # Try fuzzy match for typos if no exact match
        if 'network_type' not in entities:
            for word in query.split():
                matched = self.fuzzy_match(word, self.networks, threshold=0.75)
                if matched:
                    entities['network_type'] = matched
                    break
        
        # Extract sender state and age group
        for state in self.states:
            if f"sender in {state.lower()}" in query_lower or f"sender from {state.lower()}" in query_lower:
                entities['sender_state'] = state
            if f"{state.lower()} sender" in query_lower:
                entities['sender_state'] = state
        
        # If just "state" mentioned without sender context
        # First try exact match
        for state in self.states:
            if state.lower() in query_lower and 'sender_state' not in entities and 'state' not in entities:
                entities['state'] = state
                break
        # If no exact match, try fuzzy match
        if 'state' not in entities and 'sender_state' not in entities:
            for word in query.split():
                if len(word) > 3:  # Skip short words
                    matched = self.fuzzy_match(word, self.states, threshold=0.80)
                    if matched:
                        entities['state'] = matched
                        break
        
        # Extract sender age group
        for age_group in self.age_groups:
            if f"sender age {age_group}" in query_lower or f"sender {age_group}" in query_lower:
                entities['sender_age_group'] = age_group
        
        # Extract receiver age group
        for age_group in self.age_groups:
            if f"receiver age {age_group}" in query_lower or f"receiver {age_group}" in query_lower:
                entities['receiver_age_group'] = age_group
        
        # If just age mentioned without sender/receiver context
        for age_group in self.age_groups:
            if age_group in query_lower and 'sender_age_group' not in entities and 'receiver_age_group' not in entities:
                entities['age_group'] = age_group  # Generic age group
                break
        
        # Extract banks (fuzzy match for typos like "HDFL" -> "HDFC")
        # Bank mention handling: detect "to <bank>", "from <bank>", or explicit sender/receiver
        for bank in self.banks:
            bk_l = bank.lower()
            # explicit patterns
            if re.search(rf"\bto\s+{re.escape(bk_l)}\b", query_lower):
                entities['receiver_bank'] = bank
                break
            if re.search(rf"\bfrom\s+{re.escape(bk_l)}\b", query_lower):
                entities['sender_bank'] = bank
                break
            if bk_l in query_lower:
                if "sender" in query_lower:
                    entities['sender_bank'] = bank
                elif "receiver" in query_lower or "to " in query_lower:
                    entities['receiver_bank'] = bank
                else:
                    entities['bank'] = bank
                break
        
        # Fuzzy match banks if no exact match found
        if 'bank' not in entities and 'sender_bank' not in entities and 'receiver_bank' not in entities:
            for word in query.split():
                if len(word) > 2:
                    matched = self.fuzzy_match(word, self.banks, threshold=0.75)
                    if matched:
                        if "sender" in query_lower:
                            entities['sender_bank'] = matched
                        elif "receiver" in query_lower or "to " in query_lower:
                            entities['receiver_bank'] = matched
                        else:
                            entities['bank'] = matched
                        break

        # Patterns like 'per bank', 'by bank', 'bank wise', 'top banks' -> set comparison dimension
        if re.search(r"\b(bank\s*-?wise|by bank|per bank|of bank|of banks|of the banks|amount per bank|amount by bank|with bank|with banks|top\s+banks|top\s+bank)\b", query_lower):
            # prefer explicit direction if present
            if any(w in query_lower for w in ["receiver", "to ", "sent to"]):
                entities['comparison_dimension'] = 'receiver_bank'
            elif any(w in query_lower for w in ["sender", "from ", "sent from"]):
                entities['comparison_dimension'] = 'sender_bank'
            else:
                entities['comparison_dimension'] = 'sender_bank'

        # Handle explicit 'receiver bank' / 'sender bank' phrases (e.g., 'by receiver bank')
        if 'receiver bank' in query_lower or re.search(r"\bby\s+receiver\s+bank\b", query_lower):
            entities['comparison_dimension'] = 'receiver_bank'
        elif 'sender bank' in query_lower or re.search(r"\bby\s+sender\s+bank\b", query_lower):
            entities['comparison_dimension'] = 'sender_bank'

        # Detect aggregation metric (amount, sum, total, avg, count, fraud/failure rates)
        # Note: Use if/elif chain so first match wins (total before average before count)
        if re.search(r"\b(sum|total|amount|revenue|spend|spent)\b", query_lower):
            entities['metric'] = 'amount'
        elif re.search(r"\b(average|avg|mean)\b", query_lower):
            entities['metric'] = 'avg_amount'
        elif re.search(r"\b(count|how many|number of|no\. of)\b", query_lower):
            entities['metric'] = 'count'
        elif re.search(r"\b(fraud rate|fraud|flagged|fraudulent)\b", query_lower):
            entities['metric'] = 'fraud_rate'
        elif re.search(r"\b(failure rate|failed|failure)\b", query_lower):
            entities['metric'] = 'failure_rate'

        # capture top/bottom N specification
        top_match = re.search(r"top\s*(\d+|three|five|ten)", query_lower)
        if top_match:
            top_val = top_match.group(1)
            if top_val.isdigit():
                entities['top_n'] = int(top_val)
            else:
                word_to_num = {"three": 3, "five": 5, "ten": 10}
                entities['top_n'] = word_to_num.get(top_val, 3)
        bottom_match = re.search(r"bottom\s*(\d+)", query_lower)
        if bottom_match:
            entities['bottom_n'] = int(bottom_match.group(1))
        
        # Extract temporal references
        time_ref = self._extract_time_reference(query_lower)
        if time_ref:
            entities['time_reference'] = time_ref

        # Handle "from <state>" patterns for sender (model only has sender_state)
        for state in self.states:
            s_low = state.lower()
            if re.search(rf"\bfrom\s+{re.escape(s_low)}\b", query_lower) or re.search(rf"transactions from {re.escape(s_low)}", query_lower) or re.search(rf"sent from {re.escape(s_low)}", query_lower):
                entities['sender_state'] = state
        
        # Extract hour patterns
        hour_match = re.search(r'(\d{1,2})\s*(?:am|pm|:00|o\'clock|hours?)', query_lower)
        if hour_match:
            entities['hour_of_day'] = hour_match.group(1)
        
        # Extract day patterns
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in query_lower:
                entities['day_of_week'] = day
                break
        
        # Extract weekend patterns
        if any(pattern in query_lower for pattern in ["weekend", "saturday", "sunday", "weekends"]):
            entities['is_weekend'] = "true"
        
        # Extract comparison dimension for "X wise" patterns
        wise_match = re.search(r"\b(state|age|category|device|network|bank|status|type)(?:\s|-)?wise\b", query_lower)
        if wise_match:
            val = wise_match.group(1)
            conversion = {
                'age': 'age_group',
                'category': 'merchant_category',
                'device': 'device_type',
                'network': 'network_type',
                'bank': 'bank',
                'status': 'transaction_status',
                'type': 'transaction_type'
            }
            # assign generic 'bank' and let direction be resolved below if needed
            entities['comparison_dimension'] = conversion.get(val, val)

        # Detect explicit segmentation requests like "by state", "by age", etc.
        seg_keywords = ["by state", "by age", "by category", "by device", "by network", "by networks", "by bank", "by status", "by type"]
        for seg_kw in seg_keywords:
            if seg_kw in query_lower:
                if 'comparison_dimension' in entities or 'segment_by' in entities:
                    break
                dim_map = {
                    "by state": "state",
                    "by age": "age_group",
                    "by category": "merchant_category",
                    "by device": "device_type",
                    "by network": "network_type",
                    "by networks": "network_type",
                    "by bank": "bank",
                    "by status": "transaction_status",
                    "by type": "transaction_type"
                }
                # Comparative/aggregation queries need comparison_dimension (not segment_by)
                # Keywords: fraud, risk, compare, total, sum, amount, value, top, show
                if any(kw in query_lower for kw in ["fraud", "risk", "failed", "failure", "compare", "comparison", "versus", "vs", "total", "sum", "amount", "value", "top", "show"]):
                    entities['comparison_dimension'] = dim_map.get(seg_kw, seg_kw)
                else:
                    # Pure segmentation queries
                    entities['segment_by'] = dim_map.get(seg_kw, seg_kw)
                break

        # If user mentions the dimension word alone (e.g., 'state' or 'state-wise' hyphen),
        # but we haven't set segmentation/comparison, set a sensible default.
        # BUT: only if there's a grouping/aggregation keyword present
        if 'comparison_dimension' not in entities and 'segment_by' not in entities:
            has_grouping_keyword = any(kw in query_lower for kw in 
                                      ["by ", "per ", "wise", "compare", "comparison", "versus", "vs",
                                       "total", "sum", "amount", "value", "top", "show", "group",
                                       "segment", "across"])
            
            if has_grouping_keyword:
                dim_patterns = {
                    'state': r"\bstates?\b",
                    'age': r"\bage\s+groups?\b|\bage\b",
                    'category': r"\bcategories?\b|\bcategory\b",
                    'device': r"\bdevices?\b|\bdevice\s+type\b|\bdevice\b",
                    'network': r"\bnetworks?\b|\bnetwork\b",
                    'bank': r"\bbanks?\b|\bbank\b"
                }
                dim_map = {
                    'state': 'state',
                    'age': 'age_group',
                    'category': 'merchant_category',
                    'device': 'device_type',
                    'network': 'network_type',
                    'bank': 'bank'
                }
                for dim, pattern in dim_patterns.items():
                    if re.search(pattern, query_lower):
                        entities['comparison_dimension'] = dim_map.get(dim, dim)
                        break

        # If comparison_dimension is generic 'bank', refine using directional words
        if entities.get('comparison_dimension') == 'bank':
            if any(w in query_lower for w in ["receiver", "to ", "sent to", "received by"]):
                entities['comparison_dimension'] = 'receiver_bank'
            elif any(w in query_lower for w in ["sender", "from ", "sent from", "sent by"]):
                entities['comparison_dimension'] = 'sender_bank'

        # Weekend vs weekday comparisons
        if any(kw in query_lower for kw in ["weekend vs weekday", "weekday vs weekend"]):
            entities['comparison_dimension'] = 'is_weekend'
            if 'metric' not in entities and "volume" in query_lower:
                entities['metric'] = 'count'
        
        return entities
    
    def _extract_time_reference(self, query: str) -> Optional[str]:
        """Extract time reference from query"""
        time_patterns = {
            "today": "today",
            "yesterday": "yesterday",
            "this week": "week",
            "this month": "month",
            "this year": "year",
            "last week": "last_week",
            "last month": "last_month",
            "day of week": "day_of_week",
            "morning": "morning",
            "afternoon": "afternoon",
            "evening": "evening",
            "night": "night",
            "peak hours": "peak_hours",
            "peak": "peak_hours",
            "office hours": "office_hours",
            "business hours": "business_hours",
            "weekend": "weekend",
            "weekday": "weekday",
            "daytime": "daytime",
            "nighttime": "nighttime"
        }
        
        for pattern, label in time_patterns.items():
            if pattern in query:
                return label
        
        return None
