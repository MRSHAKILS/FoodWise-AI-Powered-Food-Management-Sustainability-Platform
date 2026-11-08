import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

class FoodRiskPredictor:
    """
    AI-based food expiration risk prediction system.
    Analyzes inventory, consumption patterns, and environmental factors.
    """
    
    def __init__(self, inventory_file, consumption_log_file):
        self.inventory_file = inventory_file
        self.consumption_log_file = consumption_log_file
        self.current_date = datetime.now().date()
        
        # Load data
        self.inventory = self._load_json(inventory_file)
        self.consumption_logs = self._load_json(consumption_log_file)
        
        # Category risk weights (higher = faster consumption needed)
        self.category_weights = {
            'Fish/Meat': 2.0,
            'Dairy': 1.8,
            'Dairy/Poultry': 1.7,
            'Fruit': 1.6,
            'Vegetable': 1.5,
            'Grain/Snack': 1.2,
            'Grain': 1.0,
            'Spice': 0.8,
            'Oil/Fat': 0.7,
            'Dry Good': 0.6
        }
        
        # Seasonal factors (Bangladesh context - warm season)
        self.season_factor = self._get_seasonal_factor()
    
    def _load_json(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}
    
    def _get_seasonal_factor(self):
        """Determine seasonal risk factor based on current month"""
        month = self.current_date.month
        # Bangladesh warm season: March-October (higher risk)
        if 3 <= month <= 10:
            return 1.3  # Items spoil 30% faster in warm season
        else:
            return 1.0  # Normal risk in cool season
    
    def calculate_consumption_frequency(self):
        """Calculate how frequently each item is consumed"""
        consumption_freq = defaultdict(lambda: {'count': 0, 'total_quantity': 0, 'last_consumed': None})
        
        for log in self.consumption_logs.get('consumption_logs', []):
            item_name = log['item_name']
            consumption_freq[item_name]['count'] += 1
            consumption_freq[item_name]['total_quantity'] += log['quantity']
            
            # Track last consumption date
            cons_date = datetime.strptime(log['consumption_date'], '%Y-%m-%d').date()
            if not consumption_freq[item_name]['last_consumed'] or cons_date > consumption_freq[item_name]['last_consumed']:
                consumption_freq[item_name]['last_consumed'] = cons_date
        
        return consumption_freq
    
    def calculate_days_until_expiry(self, item):
        """Calculate days remaining until expiry"""
        purchase_date = datetime.strptime(item['purchase_date'], '%Y-%m-%d').date()
        expiry_date = purchase_date + timedelta(days=item['typical_expiration_days'])
        days_until_expiry = (expiry_date - self.current_date).days
        return days_until_expiry
    
    def calculate_risk_score(self, item, consumption_freq):
        """
        Calculate risk score (0-100) for each item.
        Higher score = Higher risk of spoilage
        """
        item_name = item['item_name']
        category = item['category']
        
        # 1. Days until expiry factor (0-40 points)
        days_left = self.calculate_days_until_expiry(item)
        if days_left <= 0:
            expiry_score = 40
        elif days_left <= 1:
            expiry_score = 35
        elif days_left <= 2:
            expiry_score = 30
        elif days_left <= 3:
            expiry_score = 25
        elif days_left <= 5:
            expiry_score = 20
        elif days_left <= 7:
            expiry_score = 15
        else:
            expiry_score = max(0, 40 - (days_left * 0.5))
        
        # 2. Category risk factor (0-25 points)
        category_score = self.category_weights.get(category, 1.0) * 12.5
        
        # 3. Consumption frequency factor (0-20 points)
        # Low consumption = Higher risk
        freq_data = consumption_freq.get(item_name, {'count': 0})
        if freq_data['count'] == 0:
            frequency_score = 20  # Never consumed = high risk
        elif freq_data['count'] == 1:
            frequency_score = 15
        elif freq_data['count'] == 2:
            frequency_score = 10
        else:
            frequency_score = max(0, 20 - (freq_data['count'] * 2))
        
        # 4. Seasonal factor (0-15 points)
        seasonal_score = 0
        if category in ['Fruit', 'Vegetable', 'Fish/Meat', 'Dairy']:
            seasonal_score = (self.season_factor - 1.0) * 50  # Up to 15 points in warm season
        
        # Total risk score
        total_risk = expiry_score + category_score + frequency_score + seasonal_score
        total_risk = min(100, max(0, total_risk))  # Clamp to 0-100
        
        return {
            'total_risk': round(total_risk, 2),
            'days_until_expiry': days_left,
            'expiry_score': round(expiry_score, 2),
            'category_score': round(category_score, 2),
            'frequency_score': round(frequency_score, 2),
            'seasonal_score': round(seasonal_score, 2)
        }
    
    def get_risk_level(self, risk_score):
        """Categorize risk level"""
        if risk_score >= 70:
            return "Critical"
        elif risk_score >= 50:
            return "High"
        elif risk_score >= 30:
            return "Medium"
        else:
            return "Low"
    
    def get_risk_reason(self, item, risk_data):
        """Generate human-readable reason for the risk"""
        days_left = risk_data['days_until_expiry']
        reasons = []
        
        if days_left <= 0:
            reasons.append("Already expired!")
        elif days_left == 1:
            reasons.append("Expires tomorrow")
        elif days_left <= 2:
            reasons.append(f"Expires in {days_left} days")
        elif days_left <= 5:
            reasons.append(f"Expires in {days_left} days")
        
        if item['category'] in ['Fish/Meat', 'Dairy', 'Dairy/Poultry']:
            reasons.append("Highly perishable category")
        
        if self.season_factor > 1.0 and item['category'] in ['Fruit', 'Vegetable', 'Fish/Meat', 'Dairy']:
            reasons.append("Spoils faster in warm season")
        
        return " | ".join(reasons) if reasons else "Monitor for freshness"
    
    def generate_alerts(self, risk_items):
        """Generate in-app alerts based on risk levels"""
        alerts = []
        
        critical_items = [item for item in risk_items if item['risk_level'] == 'Critical']
        high_items = [item for item in risk_items if item['risk_level'] == 'High']
        
        if critical_items:
            alert_message = f"⚠️ URGENT: {len(critical_items)} item(s) need immediate attention!"
            alerts.append({
                'type': 'critical',
                'title': 'Critical Expiration Alert',
                'message': alert_message,
                'items': [item['item_name'] for item in critical_items[:3]],
                'action': 'Consume or discard immediately'
            })
        
        if high_items:
            alert_message = f"⚡ WARNING: {len(high_items)} item(s) expiring soon!"
            alerts.append({
                'type': 'high',
                'title': 'High Risk Alert',
                'message': alert_message,
                'items': [item['item_name'] for item in high_items[:5]],
                'action': 'Plan to use within next 1-2 days'
            })
        
        return alerts
    
    def predict_risks(self):
        """Main prediction function"""
        print("🔍 Analyzing food inventory for expiration risks...\n")
        
        # Calculate consumption patterns
        consumption_freq = self.calculate_consumption_frequency()
        
        # Analyze each inventory item
        risk_items = []
        
        for item in self.inventory.get('inventory', []):
            risk_data = self.calculate_risk_score(item, consumption_freq)
            risk_level = self.get_risk_level(risk_data['total_risk'])
            risk_reason = self.get_risk_reason(item, risk_data)
            
            risk_items.append({
                'item_id': item['item_id'],
                'item_name': item['item_name'],
                'category': item['category'],
                'quantity': item['quantity'],
                'unit': item['unit'],
                'purchase_date': item['purchase_date'],
                'days_until_expiry': risk_data['days_until_expiry'],
                'risk_score': risk_data['total_risk'],
                'risk_level': risk_level,
                'reason': risk_reason,
                'breakdown': {
                    'expiry_score': risk_data['expiry_score'],
                    'category_score': risk_data['category_score'],
                    'frequency_score': risk_data['frequency_score'],
                    'seasonal_score': risk_data['seasonal_score']
                }
            })
        
        # Sort by risk score (highest first)
        risk_items.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Generate priority list ("eat these first")
        priority_list = [item for item in risk_items if item['risk_score'] >= 30]
        
        # Generate alerts
        alerts = self.generate_alerts(risk_items)
        
        # Prepare final report
        report = {
            'analysis_date': self.current_date.strftime('%Y-%m-%d'),
            'user_id': self.inventory.get('user_id', 'unknown'),
            'user_name': self.inventory.get('user_name', 'Unknown User'),
            'total_items': len(risk_items),
            'season_factor': self.season_factor,
            'summary': {
                'critical': len([x for x in risk_items if x['risk_level'] == 'Critical']),
                'high': len([x for x in risk_items if x['risk_level'] == 'High']),
                'medium': len([x for x in risk_items if x['risk_level'] == 'Medium']),
                'low': len([x for x in risk_items if x['risk_level'] == 'Low'])
            },
            'alerts': alerts,
            'priority_list': priority_list,
            'all_items': risk_items
        }
        
        return report
    
    def save_report(self, report, output_file='risk_prediction_report.json'):
        """Save the risk prediction report to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, indent=4, ensure_ascii=False, fp=f)
            print(f"\n✅ Risk prediction report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
    
    def print_report(self, report):
        """Print formatted report to console"""
        print("=" * 80)
        print(f"🤖 AI FOOD EXPIRATION RISK PREDICTION REPORT")
        print("=" * 80)
        print(f"📅 Analysis Date: {report['analysis_date']}")
        print(f"👤 User: {report['user_name']} ({report['user_id']})")
        print(f"📦 Total Items: {report['total_items']}")
        print(f"🌡️  Season Factor: {report['season_factor']}x")
        print("\n" + "=" * 80)
        
        # Summary
        print("📊 RISK SUMMARY")
        print("-" * 80)
        print(f"  🔴 Critical: {report['summary']['critical']} items")
        print(f"  🟠 High:     {report['summary']['high']} items")
        print(f"  🟡 Medium:   {report['summary']['medium']} items")
        print(f"  🟢 Low:      {report['summary']['low']} items")
        
        # Alerts
        if report['alerts']:
            print("\n" + "=" * 80)
            print("🚨 ALERTS")
            print("-" * 80)
            for alert in report['alerts']:
                print(f"\n  {alert['title']}")
                print(f"  {alert['message']}")
                print(f"  Items: {', '.join(alert['items'])}")
                print(f"  Action: {alert['action']}")
        
        # Priority List
        if report['priority_list']:
            print("\n" + "=" * 80)
            print("⚡ PRIORITY LIST - EAT THESE FIRST!")
            print("-" * 80)
            for i, item in enumerate(report['priority_list'][:10], 1):
                emoji = "🔴" if item['risk_level'] == "Critical" else "🟠" if item['risk_level'] == "High" else "🟡"
                print(f"\n  {i}. {emoji} {item['item_name']}")
                print(f"     Risk: {item['risk_score']}/100 ({item['risk_level']})")
                print(f"     Quantity: {item['quantity']} {item['unit']}")
                print(f"     Days Left: {item['days_until_expiry']} days")
                print(f"     Reason: {item['reason']}")
        
        print("\n" + "=" * 80)


def main():
    # File paths
    inventory_file = 'user_inventory.json'
    consumption_log_file = 'consumption_log.json'
    output_file = 'risk_prediction_report.json'
    
    # Check if files exist
    if not os.path.exists(inventory_file):
        print(f"❌ Error: {inventory_file} not found!")
        return
    
    if not os.path.exists(consumption_log_file):
        print(f"❌ Error: {consumption_log_file} not found!")
        return
    
    # Create predictor and run analysis
    predictor = FoodRiskPredictor(inventory_file, consumption_log_file)
    report = predictor.predict_risks()
    
    # Print report to console
    predictor.print_report(report)
    
    # Save report to file
    predictor.save_report(report, output_file)


if __name__ == "__main__":
    main()
