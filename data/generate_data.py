import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

n_customers = 3000
plans = ['starter', 'growth', 'pro', 'enterprise']
plan_prices = {'starter': 299, 'growth': 799, 'pro': 1999, 'enterprise': 4999}

customers = []

for i in range(1, n_customers + 1):
    plan = random.choices(plans, weights=[0.4, 0.3, 0.2, 0.1])[0]
    start_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
    tenure_months = random.randint(1, 24)

    churn_prob = {'starter': 0.15, 'growth': 0.08, 
                  'pro': 0.05, 'enterprise': 0.03}[plan]
    status = 'churned' if random.random() < churn_prob else 'active'

    customers.append({
        'customer_id': f'cust_{i}',
        'company_name': f'Company_{i}',
        'plan': plan,
        'mrr': plan_prices[plan],
        'start_date': start_date.strftime('%Y-%m-%d'),
        'status': status,
        'tenure_months': tenure_months,
        'seats': random.randint(1, 50) if plan == 'enterprise' else random.randint(1, 5),
        'industry': random.choice(['SaaS', 'Ecommerce', 'Finance', 'Healthcare', 'Other']),
        'avg_dau': round(random.uniform(0.5, 10), 1),
        'login_days_30': random.randint(0, 30),
        'features_used': random.randint(1, 8),
        'support_tickets': random.randint(0, 5)
    })

df = pd.DataFrame(customers)
df.to_csv('data/subscriptions.csv', index=False)
print(f"✅ Generated {len(df)} customers")
print(df['status'].value_counts())
print(df.head(3))