import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class ResponseGenerator:
    """
    Generates context-aware natural language responses from data analysis
    Uses OpenAI LLM for conversational and explainable outputs with conversation history
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_llm = bool(self.openai_api_key)
        
        if self.use_llm:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
                # log success without unicode to avoid encoding problems
                print("OpenAI LLM integration enabled")
            except Exception as e:
                print(f"LLM integration failed: {e}")
                self.use_llm = False
        else:
            print("OPENAI_API_KEY not set - using template responses")
    
    def generate_response(
        self, 
        query: str, 
        analysis_result: Dict[str, Any], 
        intent_type: str,
        conversation_context: Optional[str] = None,
        resolved_entities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate conversational response with context awareness for follow-ups
        
        Args:
            query: Current user query
            analysis_result: Data analysis results from query builder
            intent_type: Intent classification
            conversation_context: Previous conversation history for context
            resolved_entities: Accumulated entities from conversation
        """
        
        # Extract insights from analysis
        insights = self._extract_insights(analysis_result, intent_type)
        
        # Generate explanation (LLM if available, fallback to template)
        if self.use_llm:
            explanation = self._generate_llm_response(
                query, 
                analysis_result, 
                intent_type, 
                insights,
                conversation_context,
                resolved_entities
            )
        else:
            explanation = self._generate_template_response(analysis_result, intent_type, insights, resolved_entities)

        footer = self._build_footer(analysis_result, insights)
        if footer:
            explanation = f"{explanation}\n\n{footer}"
        
        return {
            "query": query,
            "intent": intent_type,
            "explanation": explanation,
            "insights": insights,
            "raw_data": analysis_result,
            "resolved_entities": resolved_entities,
            "confidence_score": self._calculate_confidence(analysis_result)
        }
    
    def _build_footer(self, result: Dict[str, Any], insights: list) -> str:
        """Build a response footer with compute time, dataset size, and a single insight."""
        meta = result.get("_meta") or {}
        compute_ms = meta.get("compute_ms")
        dataset_size = meta.get("dataset_size")

        footer_parts = []
        if compute_ms is not None:
            footer_parts.append(f"Compute time: {compute_ms:.2f} ms")
        if dataset_size is not None:
            footer_parts.append(f"Dataset size: {int(dataset_size):,} transactions")

        insight_line = None
        if insights:
            insight_line = insights[0]

        if not footer_parts and not insight_line:
            return ""

        footer = "**Response Summary**\n"
        if footer_parts:
            footer += "- " + " | ".join(footer_parts) + "\n"
        if insight_line:
            footer += f"- Insight: {insight_line}\n"

        return footer
    
    def _generate_llm_response(
        self, 
        user_query: str, 
        analysis_result: Dict[str, Any], 
        intent_type: str, 
        insights: list,
        conversation_context: Optional[str] = None,
        resolved_entities: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response using OpenAI with context awareness"""
        try:
            prompt = self._build_context_aware_prompt(
                user_query,
                analysis_result,
                intent_type,
                insights,
                conversation_context,
                resolved_entities
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are InsightX, a financial data analyst AI assistant. 
Your role is to:
1. Answer user questions about transaction data clearly and concisely
2. Provide actionable insights based on the analysis
3. Consider the conversation context to handle follow-up questions accurately
4. Maintain consistency with previous responses in the conversation
5. Present data professionally using Indian currency (₹) without unnecessary jargon"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template_response(analysis_result, intent_type, insights)
    
    def _build_context_aware_prompt(
        self,
        user_query: str,
        analysis_result: Dict[str, Any],
        intent_type: str,
        insights: list,
        conversation_context: Optional[str],
        resolved_entities: Optional[Dict[str, Any]]
    ) -> str:
        """Build a context-aware prompt that includes conversation history"""
        
        prompt = f"""Based on the transaction data analysis, answer this question: "{user_query}"

**Analysis Results:**
- Intent Type: {intent_type}
- Key Insights: {json.dumps(insights)}
- Data Summary: {json.dumps(self._summarize_result(analysis_result), default=str)}

**Resolved Context from Conversation:**
{self._format_resolved_entities(resolved_entities)}"""
        
        # Add conversation history if available
        if conversation_context:
            prompt += f"""

**Previous Conversation:**
{conversation_context}

Note: The user may be asking a follow-up question. Use the conversation history above to maintain consistency."""
        
        prompt += """

Please provide:
1. A direct, concise answer to the question
2. Supporting data points or statistics
3. One actionable insight or recommendation (if relevant)

Keep the response focused and easy to understand. Use ₹ for currency amounts."""
        
        return prompt
    
    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a concise summary of analysis result"""
        summary = {
            "total_count": result.get("total_count"),
            "statistics": result.get("statistics"),
        }
        
        # Add intent-specific summaries
        if result.get("data"):
            summary["comparison_data"] = result["data"][:3]  # Top 3 items
        if result.get("segments"):
            summary["top_segments"] = result["segments"][:3]
        if result.get("fraud_rate_percent"):
            summary["fraud_rate"] = result["fraud_rate_percent"]

        # include grouped breakdowns (top 3)
        if result.get("groups"):
            summary["groups"] = result["groups"][:3]

        if result.get("temporal"):
            temporal = result.get("temporal") or {}
            summary["temporal"] = {
                "peak_hours": temporal.get("peak_hours", [])[:3],
                "weekend_split": temporal.get("weekend_split", [])
            }

        return summary
    
    def _format_resolved_entities(self, entities: Optional[Dict[str, Any]]) -> str:
        """Format resolved entities for prompt context"""
        if not entities:
            return "None"
        
        formatted = []
        # Prefer new schema fields (merchant_category, sender/receiver)
        if entities.get("merchant_category") or entities.get("category"):
            formatted.append(f"- Merchant Category: {entities.get('merchant_category') or entities.get('category')}")
        if entities.get("sender_state"):
            formatted.append(f"- Sender State: {entities['sender_state']}")
        if entities.get("state") and 'sender_state' not in entities:
            formatted.append(f"- State: {entities['state']}")
        if entities.get("device_type"):
            formatted.append(f"- Device: {entities['device_type']}")
        if entities.get("network_type"):
            formatted.append(f"- Network: {entities['network_type']}")
        if entities.get("sender_age_group"):
            formatted.append(f"- Sender Age Group: {entities['sender_age_group']}")
        if entities.get("receiver_age_group"):
            formatted.append(f"- Receiver Age Group: {entities['receiver_age_group']}")
        if entities.get("age_group") and 'sender_age_group' not in entities and 'receiver_age_group' not in entities:
            formatted.append(f"- Age Group: {entities['age_group']}")
        if entities.get('sender_bank'):
            formatted.append(f"- Sender Bank: {entities['sender_bank']}")
        if entities.get('receiver_bank'):
            formatted.append(f"- Receiver Bank: {entities['receiver_bank']}")
        if entities.get('transaction_type'):
            formatted.append(f"- Transaction Type: {entities['transaction_type']}")
        if entities.get('transaction_status'):
            formatted.append(f"- Transaction Status: {entities['transaction_status']}")
            
        return "\n".join(formatted) if formatted else "None"
    
    def _extract_insights(self, result: Dict[str, Any], intent_type: str) -> list:
        """Extract key insights from analysis result"""
        insights = []
        
        if intent_type == "descriptive":
            if "statistics" in result and result["statistics"]:
                insights.append(f"Analyzed {result.get('total_count', 0)} transactions")
                insights.append(f"Success rate: {result.get('success_rate', 0):.2f}%")
        
        elif intent_type == "comparative":
            if "data" in result:
                insights.append(f"Comparison across: {result.get('comparison_key', 'categories')}")
                insights.append(f"Total items compared: {len(result['data'])}")
                if result.get('best_performer'):
                    insights.append(f"Best performer: {result['best_performer']}")
        
        elif intent_type == "user_segmentation":
            if "segments" in result:
                insights.append(f"Segmented by: {result.get('segment_key', 'segment')}")
                insights.append(f"Total segments: {len(result['segments'])}")
        
        elif intent_type == "risk_analysis":
            insights.append(f"Fraud rate: {result.get('fraud_rate_percent', 0):.2f}%")
            insights.append(f"Risk level: {result.get('risk_level', 'unknown').upper()}")
            groups = result.get('groups')
            if groups:
                insights.append(f"Analyzed {len(groups)} groups")
        
        return insights
    
    def _generate_template_response(self, result: Dict[str, Any], intent_type: str, insights: list, resolved_entities: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using templates (fallback when LLM unavailable)"""
        # Prepend context if available
        context_str = self._format_resolved_entities(resolved_entities) if resolved_entities else None

        if intent_type == "descriptive":
            base = self._template_descriptive(result, insights)
        elif intent_type == "comparative":
            base = self._template_comparative(result, insights)
        elif intent_type == "user_segmentation":
            base = self._template_segmentation(result, insights)
        elif intent_type == "risk_analysis":
            base = self._template_risk(result, insights)
        else:
            base = "Analysis complete. See insights for details."

        if context_str and context_str != "None":
            return f"**Context:**\n{context_str}\n\n" + base
        return base
    
    def _template_descriptive(self, result: Dict[str, Any], insights: list) -> str:
        stats = result.get("statistics", {})
        response = "**Descriptive Summary**\n\n"

        # Key overview
        total = result.get('total_count', 0)
        response += f"- **Total transactions analyzed:** {total:,}\n"

        # Core statistics
        if "average_amount" in stats:
            response += f"- **Average transaction amount:** ₹{stats['average_amount']:,.2f}\n"
        if "median_amount" in stats:
            response += f"- **Median transaction amount:** ₹{stats['median_amount']:,.2f}\n"
        if "total_amount" in stats:
            response += f"- **Total transaction value:** ₹{stats['total_amount']:,.2f}\n"

        # Success / rates
        response += f"- **Success rate:** {result.get('success_rate', 0):.2f}%\n"

        # Range
        if stats.get('min_amount') is not None and stats.get('max_amount') is not None:
            response += f"- **Range:** ₹{stats.get('min_amount', 0):,.2f} — ₹{stats.get('max_amount', 0):,.2f}\n"

        # Temporal highlights (peak hours / day-of-week)
        temporal = result.get('temporal') or {}
        peak_hours = temporal.get('peak_hours') or []
        if peak_hours:
            top = ", ".join([f"{p.get('hour')}:00" for p in peak_hours if p.get('hour') is not None])
            if top:
                response += f"- **Peak hours:** {top}\n"

        day_breakdown = temporal.get('day_of_week') or []
        if day_breakdown:
            best_day = sorted(day_breakdown, key=lambda x: x.get('transaction_count', 0), reverse=True)[:1]
            if best_day:
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                day_idx = best_day[0].get('day_of_week')
                day_label = day_names[day_idx] if isinstance(day_idx, int) and 0 <= day_idx < 7 else str(day_idx)
                response += f"- **Busiest day:** {day_label}\n"

        return response
    
    def _template_comparative(self, result: Dict[str, Any], insights: list) -> str:
        # Build a clean, tabular-style comparative summary
        key = result.get('comparison_key', 'dimensions')
        metric = (result.get('metric') or '').lower()
        title = key.replace('_', ' ').title() + ' Comparison'
        response = f"**{title}**\n\n"
        response += f"- **Scope:** `{key}`\n"

        data = result.get('data', [])
        if data:
            for item in data:
                name = item.get('category') or item.get('segment') or item.get('name') or 'Unknown'
                avg = item.get('average_amount', 0.0)
                total = item.get('total_amount', 0.0)
                count = item.get('transaction_count', 0)
                success_rate = item.get('success_rate')
                # Default to TOTAL when metric is not specified
                if metric in ("amount", "total_amount", "total") or metric == '':
                    if success_rate is not None:
                        response += f"- **{name}:** Total = ₹{total:,.2f}; Success = {success_rate:.2f}%; Transactions = {count:,}\n"
                    else:
                        response += f"- **{name}:** Total = ₹{total:,.2f}; Transactions = {count:,}\n"
                elif metric == "count":
                    if success_rate is not None:
                        response += f"- **{name}:** Transactions = {count:,}; Success = {success_rate:.2f}%; Average = ₹{avg:,.2f}\n"
                    else:
                        response += f"- **{name}:** Transactions = {count:,}; Average = ₹{avg:,.2f}\n"
                else:
                    if success_rate is not None:
                        response += f"- **{name}:** Average = ₹{avg:,.2f}; Success = {success_rate:.2f}%; Transactions = {count:,}\n"
                    else:
                        response += f"- **{name}:** Average = ₹{avg:,.2f}; Transactions = {count:,}\n"

        # Add best performer insight if available
        if result.get('best_performer'):
            if metric in ("amount", "total_amount", "total") or metric == '':
                response += f"\n- **Insight:** {result['best_performer']} shows the highest total transaction value, indicating strong performance in this segment."
            else:
                response += f"\n- **Insight:** {result['best_performer']} shows the highest average transaction value, indicating strong performance in this segment."

        return response
    
    def _template_segmentation(self, result: Dict[str, Any], insights: list) -> str:
        key = result.get('segment_key', 'segment')
        response = f"**User Segmentation by {key.replace('_',' ').title()}**\n\n"

        # Brief summary
        if result.get('total_count') is not None:
            response += f"- **Total transactions analyzed:** {result.get('total_count',0):,}\n"

        # Detailed top segments
        segments = result.get('segments', [])
        if segments:
            response += "\n**Top segments by transaction volume:**\n"
            for seg in segments[:5]:
                seg_name = seg.get('segment') or seg.get('name') or 'Unknown'
                count = seg.get('transaction_count', 0)
                avg = seg.get('average_transaction_value') or seg.get('average_amount') or 0.0
                total = seg.get('total_amount', 0.0)
                response += f"- {seg_name}: {count:,} transactions, ₹{avg:,.2f} avg, ₹{total:,.2f} total\n"

        return response
    
    def _template_risk(self, result: Dict[str, Any], insights: list) -> str:
        response = "**Risk Analysis Summary**\n\n"

        # Core metrics
        if 'fraud_rate_percent' in result:
            response += f"- **Fraud rate:** {result.get('fraud_rate_percent',0):.2f}%\n"
        if 'failure_rate_percent' in result:
            response += f"- **Failure rate:** {result.get('failure_rate_percent',0):.2f}%\n"
        response += f"- **Risk level:** {result.get('risk_level','unknown').upper()}\n"

        # Group breakdown (state/bank etc.)
        groups = result.get('groups', [])
        if groups:
            response += "\n**Group breakdown:**\n"
            for item in groups[:5]:
                line = f"- {item.get('group','Unknown')}: "
                if 'fraud_rate' in item:
                    line += f"{item['fraud_rate']:.2f}% fraud rate"
                elif 'total' in item:
                    line += f"{item['total']:,} transactions"
                else:
                    numeric = [v for v in item.values() if isinstance(v, (int,float))]
                    line += str(numeric[0]) if numeric else ''
                response += line + "\n"

        # Fraud-by-category details
        fraud_categories = result.get('fraud_by_category', [])
        if fraud_categories:
            response += "\n**Categories with highest fraud concerns:**\n"
            for item in fraud_categories[:5]:
                response += f"- {item.get('category','Unknown')}: {item.get('fraud_count',0):,} flagged transactions\n"

        # Hot-spot breakdowns by rate
        fraud_hotspots_by_category = result.get('fraud_hotspots_by_category', [])
        fraud_hotspots_by_state = result.get('fraud_hotspots_by_state', [])
        fraud_hotspots_by_bank = result.get('fraud_hotspots_by_bank', [])
        failure_hotspots_by_category = result.get('failure_hotspots_by_category', [])
        failure_hotspots_by_state = result.get('failure_hotspots_by_state', [])
        failure_hotspots_by_bank = result.get('failure_hotspots_by_bank', [])

        if fraud_hotspots_by_category or fraud_hotspots_by_state or fraud_hotspots_by_bank:
            response += "\n**Fraud hot-spots (top 5 by rate):**\n"
            for item in fraud_hotspots_by_category[:5]:
                response += f"- Category {item.get('group','Unknown')}: {item.get('fraud_rate',0):.2f}% fraud rate\n"
            for item in fraud_hotspots_by_state[:5]:
                response += f"- State {item.get('group','Unknown')}: {item.get('fraud_rate',0):.2f}% fraud rate\n"
            for item in fraud_hotspots_by_bank[:5]:
                response += f"- Bank {item.get('group','Unknown')}: {item.get('fraud_rate',0):.2f}% fraud rate\n"

        if failure_hotspots_by_category or failure_hotspots_by_state or failure_hotspots_by_bank:
            response += "\n**Failure hot-spots (top 5 by rate):**\n"
            for item in failure_hotspots_by_category[:5]:
                response += f"- Category {item.get('group','Unknown')}: {item.get('failure_rate',0):.2f}% failure rate\n"
            for item in failure_hotspots_by_state[:5]:
                response += f"- State {item.get('group','Unknown')}: {item.get('failure_rate',0):.2f}% failure rate\n"
            for item in failure_hotspots_by_bank[:5]:
                response += f"- Bank {item.get('group','Unknown')}: {item.get('failure_rate',0):.2f}% failure rate\n"

        # Recommendations
        risk_level = (result.get('risk_level') or 'unknown').lower()
        recommendations = {
            "high": "Immediate action required — review fraud detection and implement stricter verification.",
            "medium": "Monitor transactions closely — consider enhancing security measures for high-risk categories.",
            "low": "Current fraud rates are acceptable — continue monitoring and maintain existing controls."
        }
        response += f"\n**Recommendation:** {recommendations.get(risk_level, 'Review security protocols and investigate anomalies.')}\n"

        return response
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result completeness"""
        score = 0.8  # Base score
        
        if result.get('total_count', 0) > 100:
            score += 0.1
        elif result.get('total_count', 0) < 10:
            score -= 0.2
        
        # Bonus for rich insight data
        if result.get('statistics') or result.get('data') or result.get('segments'):
            score += 0.05
        
        return min(0.98, max(0.6, score))
