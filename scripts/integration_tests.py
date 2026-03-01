import requests

base = 'http://127.0.0.1:8000'
cases = [
    {'q':'What is the average transaction amount for Food?'},
    {'q':'State wise comparison of average transaction amount'},
    {'q':'Top 5 merchants for Shopping'},
    {'q':'Show transaction patterns by age group'},
    {'q':'What is the fraud rate for HDFC?'},
    {'q':'Give me fraud rate state wise'},
    {'q':'Give me fraud rate state wise and show groups'},
    {'q':'Give me fraud rate in Delhi'},
    {'q':'Top 3 fraud categories in Delhi'},
    {'q':'What is the fraud rate for HDFC?'},
    {'q':'Transactions to Karnataka'},
    {'q':'Transactions from Karnataka'},
]

print('Running basic queries...')
for i,c in enumerate(cases,1):
    try:
        r = requests.post(base+'/api/query', json={'query':c['q']}, timeout=30)
        out = r.json()
        print(f"\n[{i}] {c['q']} -> {r.status_code}")
        print('  intent:', out.get('intent'))
        print('  insights:', out.get('insights')[:3])
        if 'groups' in out.get('raw_data', {}):
            print('  groups:', out['raw_data']['groups'][:3])
        # print any filters applied (for debug)
        print('  raw_data keys:', list(out.get('raw_data', {}).keys()))
    except Exception as e:
        print(f"\n[{i}] FAILED: {e}")

# Session follow-up test
print('\nRunning session follow-up test...')
try:
    r = requests.post(base+'/api/conversation/start')
    sid = r.json()['session_id']
    print('  session_id:', sid)
    # First query with session
    r1 = requests.post(base+'/api/query', json={'query':'Average transaction amount for Food?','context':{'session_id':sid}}, timeout=30)
    print('  Q1 status:', r1.status_code)
    print('  Q1 intent:', r1.json().get('intent'))
    # Follow-up
    r2 = requests.post(base+'/api/query', json={'query':'How about Entertainment?','context':{'session_id':sid}}, timeout=30)
    print('  Q2 status:', r2.status_code)
    print('  Q2 intent:', r2.json().get('intent'))
    print('  Q2 insights:', r2.json().get('insights')[:3])
except Exception as e:
    print('Session test failed:', e)

print('\nRunning receiver-specific tests...')
for q in ['How many transactions were sent to HDFC?','Receiver bank HDFC fraud rate','Transactions to Delhi by receiver']:
    try:
        r = requests.post(base+'/api/query', json={'query':q}, timeout=30)
        print('\nQuery:', q, 'Status:', r.status_code)
        print('  Intent:', r.json().get('intent'))
        print('  Insights:', r.json().get('insights')[:3])
    except Exception as e:
        print('Failed:', e)

print('\nIntegration tests complete')
