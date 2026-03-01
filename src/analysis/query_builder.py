from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case
from src.database.models import Transaction
import statistics
from datetime import datetime, timedelta
import re

class QueryBuilder:
    """Builds and executes database queries based on intent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_query(self, intent_type: str, entities: Dict[str, str], query_text: str = "") -> Dict[str, Any]:
        """
        Execute query based on intent type and extracted entities
        Returns analysis results with statistics and insights
        
        Args:
            intent_type: Type of intent (descriptive, comparative, etc.)
            entities: Extracted entities from NLP
            query_text: Original user query for pattern detection (e.g., "top X")
        """
        if intent_type == "descriptive":
            return self._descriptive_analysis(entities)
        elif intent_type == "comparative":
            return self._comparative_analysis(entities, query_text)
        elif intent_type == "user_segmentation":
            return self._user_segmentation(entities)
        elif intent_type == "risk_analysis":
            return self._risk_analysis(entities)
        else:
            return self._descriptive_analysis(entities)
    
    def _descriptive_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Perform descriptive analysis - averages, totals, trends"""
        query = self.db.query(Transaction)
        
        # Apply filters based on entities
        if 'merchant_category' in entities:
            query = query.filter(Transaction.merchant_category == entities['merchant_category'])
        elif 'category' in entities:  # Fallback for old key
            query = query.filter(Transaction.merchant_category == entities['category'])
        
        if 'device_type' in entities:
            query = query.filter(Transaction.device_type == entities['device_type'])
        
        if 'sender_state' in entities:
            query = query.filter(Transaction.sender_state == entities['sender_state'])
        elif 'state' in entities:  # Fallback for old key
            query = query.filter(Transaction.sender_state == entities['state'])
        
        if 'sender_age_group' in entities:
            query = query.filter(Transaction.sender_age_group == entities['sender_age_group'])
        elif 'age_group' in entities:  # Fallback for old key
            query = query.filter(Transaction.sender_age_group == entities['age_group'])

        if 'receiver_age_group' in entities:
            query = query.filter(Transaction.receiver_age_group == entities['receiver_age_group'])

        if 'sender_bank' in entities:
            query = query.filter(Transaction.sender_bank == entities['sender_bank'])
        elif 'receiver_bank' in entities:
            query = query.filter(Transaction.receiver_bank == entities['receiver_bank'])

        if 'network_type' in entities:
            query = query.filter(Transaction.network_type == entities['network_type'])

        if 'transaction_type' in entities:
            query = query.filter(Transaction.transaction_type == entities['transaction_type'])

        # Time-based filters
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }

        time_ref = entities.get('time_reference')
        if time_ref == "weekend":
            query = query.filter(Transaction.is_weekend == True)
        elif time_ref == "weekday":
            query = query.filter(Transaction.is_weekend == False)
        elif time_ref == "morning":
            query = query.filter(Transaction.hour_of_day.between(5, 11))
        elif time_ref == "afternoon":
            query = query.filter(Transaction.hour_of_day.between(12, 16))
        elif time_ref == "evening":
            query = query.filter(Transaction.hour_of_day.between(17, 20))
        elif time_ref in ("night", "nighttime"):
            query = query.filter(
                (Transaction.hour_of_day.between(21, 23)) | (Transaction.hour_of_day.between(0, 4))
            )

        if 'hour_of_day' in entities:
            try:
                query = query.filter(Transaction.hour_of_day == int(entities['hour_of_day']))
            except ValueError:
                pass

        if 'day_of_week' in entities:
            day_val = day_map.get(str(entities['day_of_week']).lower())
            if day_val is not None:
                query = query.filter(Transaction.day_of_week == day_val)

        if 'is_weekend' in entities:
            query = query.filter(Transaction.is_weekend == True)
        
        # Get transactions
        transactions = query.all()
        
        if not transactions:
            return {
                "insight": "No transactions found matching the criteria",
                "total_count": 0,
                "statistics": None,
                "success_rate": 0
            }
        
        amounts = [t.amount for t in transactions]
        successful_count = len([
            t for t in transactions
            if t.transaction_status and t.transaction_status.lower() == "success"
        ])
        success_rate = (successful_count / len(transactions) * 100) if transactions else 0
        
        result = {
            "insight": f"Analyzed {len(transactions)} transactions",
            "total_count": len(transactions),
            "statistics": {
                "total_amount": sum(amounts),
                "average_amount": sum(amounts) / len(amounts),
                "median_amount": statistics.median(amounts),
                "min_amount": min(amounts),
                "max_amount": max(amounts),
                "std_dev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
                "sample_transactions": [(t.transaction_id, t.amount, t.merchant_category, t.timestamp.isoformat()) for t in transactions[:5]]
            },
            "success_rate": success_rate
        }

        # Temporal breakdowns when time-related queries are likely
        if any(k in entities for k in ['time_reference', 'hour_of_day', 'day_of_week', 'is_weekend']):
            hourly_rows = query.with_entities(
                Transaction.hour_of_day.label('hour'),
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            ).group_by(Transaction.hour_of_day).all()

            daily_rows = query.with_entities(
                Transaction.day_of_week.label('day'),
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            ).group_by(Transaction.day_of_week).all()

            weekend_rows = query.with_entities(
                Transaction.is_weekend.label('is_weekend'),
                func.count(Transaction.transaction_id).label('count')
            ).group_by(Transaction.is_weekend).all()

            hourly = [
                {
                    "hour": int(row[0]) if row[0] is not None else None,
                    "transaction_count": row[1],
                    "average_amount": float(row[2]) if row[2] else 0,
                    "total_amount": float(row[3]) if row[3] else 0
                }
                for row in hourly_rows
            ]
            hourly = sorted([h for h in hourly if h["hour"] is not None], key=lambda x: x["hour"])

            daily = [
                {
                    "day_of_week": int(row[0]) if row[0] is not None else None,
                    "transaction_count": row[1],
                    "average_amount": float(row[2]) if row[2] else 0,
                    "total_amount": float(row[3]) if row[3] else 0
                }
                for row in daily_rows
            ]

            weekend_split = [
                {
                    "is_weekend": bool(row[0]),
                    "transaction_count": row[1]
                }
                for row in weekend_rows
            ]

            peak_hours = sorted(hourly, key=lambda x: x["transaction_count"], reverse=True)[:3]

            result["temporal"] = {
                "hourly": hourly,
                "day_of_week": daily,
                "weekend_split": weekend_split,
                "peak_hours": peak_hours
            }

        return result
    
    def _comparative_analysis(self, entities: Dict[str, str], query_text: str = "") -> Dict[str, Any]:
        """
        Compare metrics across different dimensions.
        Handles "top X" queries to show top items/merchants.
        Respects comparison_dimension from NLP (e.g., "state wise comparison")
        """
        
        # Check if this is a "top X" query
        top_count = self._extract_top_count(query_text)
        
        # If asking for top items in a category, show by merchant
        # BUT: only if there's no explicit comparison_dimension (or it's merchant_category)
        merchant_category = entities.get('merchant_category') or entities.get('category')
        comparison_dim = entities.get('comparison_dimension')
        if top_count and merchant_category and (not comparison_dim or comparison_dim == 'merchant_category'):
            return self._comparative_by_merchant(entities, top_count)
        
        # Determine comparison dimension
        # Priority: explicit comparison_dimension > default logic
        if 'comparison_dimension' in entities:
            comparison_key = entities['comparison_dimension']
        else:
            # Default: Compare by device type if not specified
            comparison_key = 'device_type'
            if 'device_type' in entities:
                comparison_key = 'network_type'
            elif 'network_type' in entities:
                comparison_key = 'device_type'
        
        # Map old keys to new keys
        key_mapping = {
            'category': 'merchant_category',
            'state': 'sender_state',
            'age_group': 'sender_age_group',
            'bank': 'sender_bank'
        }
        comparison_key = key_mapping.get(comparison_key, comparison_key)
        
        # Get base filters (don't filter by the comparison dimension)
        base_filters = []
        
        merchant_category = entities.get('merchant_category') or entities.get('category')
        if merchant_category and comparison_key != 'merchant_category':
            base_filters.append(Transaction.merchant_category == merchant_category)
        
        sender_state = entities.get('sender_state') or entities.get('state')
        if sender_state and comparison_key != 'sender_state':
            base_filters.append(Transaction.sender_state == sender_state)
        
        if 'device_type' in entities and comparison_key != 'device_type':
            base_filters.append(Transaction.device_type == entities['device_type'])

        # If comparison_values provided, restrict to those values for the comparison_key
        comparison_values = entities.get('comparison_values')
        column_for_key = {
            'device_type': Transaction.device_type,
            'network_type': Transaction.network_type,
            'merchant_category': Transaction.merchant_category,
            'sender_state': Transaction.sender_state,
            'sender_bank': Transaction.sender_bank,
            'receiver_bank': Transaction.receiver_bank,
            'is_weekend': Transaction.is_weekend
        }
        if comparison_values and comparison_key in column_for_key:
            col = column_for_key[comparison_key]
            base_filters.append(col.in_(comparison_values))
        
        sender_age_group = entities.get('sender_age_group') or entities.get('age_group')
        if sender_age_group and comparison_key != 'sender_age_group':
            base_filters.append(Transaction.sender_age_group == sender_age_group)
        
        # Build query based on comparison dimension
        comparison_data = []
        
        success_expr = func.sum(
            case((func.lower(Transaction.transaction_status) == "success", 1), else_=0)
        ).label('success_count')

        if comparison_key == 'sender_state':
            groups = self.db.query(
                Transaction.sender_state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.sender_state).all()
            
        elif comparison_key == 'merchant_category':
            groups = self.db.query(
                Transaction.merchant_category,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.merchant_category).all()
            
        elif comparison_key == 'sender_age_group':
            groups = self.db.query(
                Transaction.sender_age_group,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.sender_age_group).all()
            
        elif comparison_key == 'network_type':
            groups = self.db.query(
                Transaction.network_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.network_type).all()
        
        elif comparison_key == 'transaction_type':
            groups = self.db.query(
                Transaction.transaction_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.transaction_type).all()

        elif comparison_key == 'is_weekend':
            groups = self.db.query(
                Transaction.is_weekend,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.is_weekend).all()
            
        else:  # device_type (default)
            groups = self.db.query(
                Transaction.device_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.device_type).all()

        # Handle bank comparison (sender/receiver)
        if comparison_key in ('sender_bank', 'receiver_bank'):
            # rebuild groups specifically for bank
            col = Transaction.sender_bank if comparison_key == 'sender_bank' else Transaction.receiver_bank
            groups = self.db.query(
                col,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount'),
                success_expr
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(col).all()
        
        # Build comparison data
        for group in groups:
            label = group[0]
            if comparison_key == 'is_weekend':
                label = "Weekend" if group[0] else "Weekday"
            success_count = group[4] if len(group) > 4 and group[4] else 0
            success_rate = (success_count / group[1] * 100) if group[1] else 0
            comparison_data.append({
                "category": label if label is not None else "Unknown",
                "transaction_count": group[1],
                "average_amount": float(group[2]) if group[2] else 0,
                "total_amount": float(group[3]) if group[3] else 0,
                "success_count": success_count,
                "success_rate": success_rate
            })
        
        # Determine sort key based on metric
        metric = entities.get('metric', '')
        if metric == 'count':
            sort_key = lambda x: x['transaction_count']
        elif 'avg' in metric:
            sort_key = lambda x: x['average_amount']
        elif metric in ('amount', 'total_amount', 'total'):
            sort_key = lambda x: x['total_amount']
        else:
            # default to average
            sort_key = lambda x: x['average_amount']

        comparison_data = sorted(comparison_data, key=sort_key, reverse=True)
        
        total_count = sum([d['transaction_count'] for d in comparison_data]) if comparison_data else 0

        return {
            "insight": f"Compared across {comparison_key}",
            "comparison_key": comparison_key,
            "metric": entities.get('metric'),
            "data": comparison_data[:top_count] if top_count else comparison_data,
            "best_performer": comparison_data[0]['category'] if comparison_data else None,
            "total_count": total_count
        }
    
    def _comparative_by_merchant(self, entities: Dict[str, str], top_count: int = 3) -> Dict[str, Any]:
        """Show top merchants/categories by transaction count in a category.

        Note: the current dataset only tracks merchant_category (like Shopping, Food)
        and does not include individual merchant names. When the user asks for
        "top merchants" we can't provide merchant-level detail; return a
        descriptive message instead.
        """

        merchant_category = entities.get('merchant_category') or entities.get('category', '')

        # if the model doesn't have merchant_name column, bail out with explanation
        if not hasattr(Transaction, 'merchant_name'):
            # fall back to returning a message instead of data
            return {
                "insight": "Dataset contains only merchant categories (e.g. \"Shopping\"); individual merchant names are not available.",
                "comparison_key": "merchant_category",
                "data": [],
                "best_performer": None,
                "total_count": 0
            }

        # Query top items in this category (ordered by transaction count)
        result = self.db.query(
            Transaction.merchant_category,
            func.count(Transaction.transaction_id).label('transaction_count'),
            func.avg(Transaction.amount).label('average_amount'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(Transaction.merchant_category == merchant_category)
        
        sender_state = entities.get('sender_state') or entities.get('state')
        if sender_state:
            result = result.filter(Transaction.sender_state == sender_state)
        
        result = result.group_by(
            Transaction.merchant_category
        ).order_by(desc('transaction_count')).limit(top_count).all()
        
        comparison_data = []
        for row in result:
            comparison_data.append({
                "category": row[0] if row[0] else "Unknown",
                "transaction_count": row[1],
                "average_amount": float(row[2]) if row[2] else 0,
                "total_amount": float(row[3]) if row[3] else 0
            })
        
        total_count = sum([d['transaction_count'] for d in comparison_data]) if comparison_data else 0
        
        return {
            "insight": f"Top {top_count} items in {merchant_category}",
            "comparison_key": "merchant_category",
            "data": comparison_data,
            "best_performer": comparison_data[0]['category'] if comparison_data else None,
            "total_count": total_count
        }
    
    def _extract_top_count(self, query_text: str) -> Optional[int]:
        """Extract 'top N' from query text"""
        if not query_text:
            return None
        
        # Look for patterns like "top 3", "top three", "top5"
        match = re.search(r'top\s*(\d+|three|five|ten)', query_text.lower())
        if match:
            count_str = match.group(1)
            if count_str.isdigit():
                return int(count_str)
            else:
                # Convert word to number
                word_to_num = {"three": 3, "five": 5, "ten": 10}
                return word_to_num.get(count_str, 3)
        
        return None
    
    def _user_segmentation(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze transactions by segment - age, state, category"""
        
        # Determine segmentation key: prefer explicit `segment_by` from NLP
        segment_key = entities.get('segment_by', 'sender_age_group')

        # Normalize common aliases
        if segment_key in ['state', 'states']:
            segment_key = 'sender_state'
        if segment_key in ['category', 'merchant_category']:
            segment_key = 'merchant_category'
        if segment_key in ['age_group']:
            segment_key = 'sender_age_group'
        
        segment_map = {
            'sender_age_group': Transaction.sender_age_group,
            'receiver_age_group': Transaction.receiver_age_group,
            'sender_state': Transaction.sender_state,
            'merchant_category': Transaction.merchant_category,
            'device_type': Transaction.device_type,
            'network_type': Transaction.network_type,
            'transaction_type': Transaction.transaction_type,
            'sender_bank': Transaction.sender_bank,
            'receiver_bank': Transaction.receiver_bank
        }
        segment_col = segment_map.get(segment_key, Transaction.sender_state)

        # Apply filters from entities (excluding the segmentation dimension)
        base_filters = []
        merchant_category = entities.get('merchant_category') or entities.get('category')
        if merchant_category and segment_key != 'merchant_category':
            base_filters.append(Transaction.merchant_category == merchant_category)

        sender_state = entities.get('sender_state') or entities.get('state')
        if sender_state and segment_key != 'sender_state':
            base_filters.append(Transaction.sender_state == sender_state)

        sender_age_group = entities.get('sender_age_group') or entities.get('age_group')
        if sender_age_group and segment_key != 'sender_age_group':
            base_filters.append(Transaction.sender_age_group == sender_age_group)

        receiver_age_group = entities.get('receiver_age_group')
        if receiver_age_group and segment_key != 'receiver_age_group':
            base_filters.append(Transaction.receiver_age_group == receiver_age_group)

        if 'sender_bank' in entities and segment_key != 'sender_bank':
            base_filters.append(Transaction.sender_bank == entities['sender_bank'])
        if 'receiver_bank' in entities and segment_key != 'receiver_bank':
            base_filters.append(Transaction.receiver_bank == entities['receiver_bank'])

        if 'device_type' in entities and segment_key != 'device_type':
            base_filters.append(Transaction.device_type == entities['device_type'])
        if 'network_type' in entities and segment_key != 'network_type':
            base_filters.append(Transaction.network_type == entities['network_type'])
        if 'transaction_type' in entities and segment_key != 'transaction_type':
            base_filters.append(Transaction.transaction_type == entities['transaction_type'])

        segments_q = self.db.query(
            segment_col,
            func.count(Transaction.transaction_id).label('count'),
            func.avg(Transaction.amount).label('avg_amount'),
            func.sum(Transaction.amount).label('total_amount')
        )
        for filt in base_filters:
            segments_q = segments_q.filter(filt)
        segments = segments_q.group_by(segment_col).all()
        
        segment_data = []
        for segment in segments:
            segment_data.append({
                "segment": segment[0] if segment[0] else "Unknown",
                "transaction_count": segment[1],
                "average_transaction_value": float(segment[2]) if segment[2] else 0,
                "total_amount": float(segment[3]) if segment[3] else 0
            })
        
        total_count = sum([s['transaction_count'] for s in segment_data]) if segment_data else 0

        return {
            "insight": f"Segmented transactions by {segment_key}",
            "segment_key": segment_key,
            "segments": sorted(segment_data, key=lambda x: x['transaction_count'], reverse=True),
            "top_segment": segment_data[0]['segment'] if segment_data else None,
            "total_count": total_count
        }
    
    def _risk_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze fraud flags and failed transactions"""

        base_query = self.db.query(Transaction)
        # collect filters so we can reuse them later for grouped queries
        base_filters: List = []

        merchant_category = entities.get('merchant_category') or entities.get('category')
        if merchant_category:
            base_query = base_query.filter(Transaction.merchant_category == merchant_category)
            base_filters.append(Transaction.merchant_category == merchant_category)

        # state filters (sender/generic - model only has sender_state)
        if 'sender_state' in entities:
            base_query = base_query.filter(Transaction.sender_state == entities['sender_state'])
            base_filters.append(Transaction.sender_state == entities['sender_state'])
        elif 'state' in entities:
            # generic state maps to sender_state by default
            base_query = base_query.filter(Transaction.sender_state == entities['state'])
            base_filters.append(Transaction.sender_state == entities['state'])

        # bank filters
        if 'sender_bank' in entities:
            base_query = base_query.filter(Transaction.sender_bank == entities['sender_bank'])
            base_filters.append(Transaction.sender_bank == entities['sender_bank'])
        elif 'receiver_bank' in entities:
            base_query = base_query.filter(Transaction.receiver_bank == entities['receiver_bank'])
            base_filters.append(Transaction.receiver_bank == entities['receiver_bank'])
        elif 'bank' in entities:
            # generic bank could be either side; apply to both via OR
            bank = entities['bank']
            base_query = base_query.filter(
                (Transaction.sender_bank == bank) | (Transaction.receiver_bank == bank)
            )
            base_filters.append((Transaction.sender_bank == bank) | (Transaction.receiver_bank == bank))

        if 'device_type' in entities:
            base_query = base_query.filter(Transaction.device_type == entities['device_type'])
            base_filters.append(Transaction.device_type == entities['device_type'])

        total_transactions = base_query.count()

        # Get fraud stats
        fraud_count = base_query.filter(Transaction.fraud_flag == True).count()
        failed_count = base_query.filter(func.lower(Transaction.transaction_status) == "failed").count()

        def _group_risk(col):
            grp_q = self.db.query(
                col.label('group'),
                func.count(Transaction.transaction_id).label('total'),
                func.sum(case((Transaction.fraud_flag == True, 1), else_=0)).label('fraud_count'),
                func.sum(case((func.lower(Transaction.transaction_status) == "failed", 1), else_=0)).label('failed_count')
            )
            for filt in base_filters:
                grp_q = grp_q.filter(filt)
            grp_q = grp_q.group_by(col).all()
            return [
                {
                    'group': row[0] if row[0] else 'Unknown',
                    'total': row[1],
                    'fraud_count': row[2],
                    'failed_count': row[3],
                    'fraud_rate': (row[2] / row[1] * 100) if row[1] else 0,
                    'failure_rate': (row[3] / row[1] * 100) if row[1] else 0
                }
                for row in grp_q
            ]

        # optional grouping by comparison dimension
        group_results = None
        comp = entities.get('comparison_dimension')
        if comp:
            comp_map = {
                'state': Transaction.sender_state,
                'sender_state': Transaction.sender_state,
                'sender_bank': Transaction.sender_bank,
                'receiver_bank': Transaction.receiver_bank,
                'bank': Transaction.sender_bank,  # default to sender for generic
                'merchant_category': Transaction.merchant_category,
                'device_type': Transaction.device_type,
                'network_type': Transaction.network_type,
            }
            col = comp_map.get(comp)
            if col is not None:
                group_results = _group_risk(col)

        # hot-spot breakdowns by category/state/bank (top 5 by rate)
        by_category = _group_risk(Transaction.merchant_category)
        by_state = _group_risk(Transaction.sender_state)
        by_bank = _group_risk(Transaction.sender_bank)

        fraud_hotspots_by_category = sorted(by_category, key=lambda x: x['fraud_rate'], reverse=True)[:5]
        fraud_hotspots_by_state = sorted(by_state, key=lambda x: x['fraud_rate'], reverse=True)[:5]
        fraud_hotspots_by_bank = sorted(by_bank, key=lambda x: x['fraud_rate'], reverse=True)[:5]

        failure_hotspots_by_category = sorted(by_category, key=lambda x: x['failure_rate'], reverse=True)[:5]
        failure_hotspots_by_state = sorted(by_state, key=lambda x: x['failure_rate'], reverse=True)[:5]
        failure_hotspots_by_bank = sorted(by_bank, key=lambda x: x['failure_rate'], reverse=True)[:5]

        # fraud by category should respect any filters applied above (state, bank, etc.)
        fraud_by_category = self.db.query(
            Transaction.merchant_category,
            func.count(Transaction.transaction_id).label('fraud_count')
        ).filter(Transaction.fraud_flag == True)
        for filt in base_filters:
            fraud_by_category = fraud_by_category.filter(filt)
        fraud_by_category = fraud_by_category.group_by(Transaction.merchant_category).all()
        # sort and limit if requested
        if entities.get('top_n') or entities.get('bottom_n'):
            reverse = True if entities.get('top_n') else False
            n = entities.get('top_n') or entities.get('bottom_n')
            fraud_by_category = sorted(fraud_by_category, key=lambda x: x[1], reverse=reverse)[:n]

        result = {
            "insight": "Risk analysis summary",
            "total_transactions": total_transactions,
            "total_count": total_transactions,
            "fraud_count": fraud_count,
            "fraud_rate_percent": (fraud_count / total_transactions * 100) if total_transactions > 0 else 0,
            "failed_count": failed_count,
            "failure_rate_percent": (failed_count / total_transactions * 100) if total_transactions > 0 else 0,
            "fraud_by_category": [
                {"category": f[0], "fraud_count": f[1]}
                for f in fraud_by_category
            ],
            "fraud_hotspots_by_category": fraud_hotspots_by_category,
            "fraud_hotspots_by_state": fraud_hotspots_by_state,
            "fraud_hotspots_by_bank": fraud_hotspots_by_bank,
            "failure_hotspots_by_category": failure_hotspots_by_category,
            "failure_hotspots_by_state": failure_hotspots_by_state,
            "failure_hotspots_by_bank": failure_hotspots_by_bank,
            "risk_level": "high" if (fraud_count / total_transactions * 100) > 5 else "medium" if (fraud_count / total_transactions * 100) > 2 else "low"
        }
        if group_results is not None:
            result['groups'] = group_results
        return result
