import datetime

NS_TU_WIEN = 3000
NS_UNI_WIEN = 3002
NS_MU_WIEN = 3004
NS_SONSTIGE = 3006

UNI_NAMESPACES = (
	NS_TU_WIEN,
	NS_UNI_WIEN,
	NS_MU_WIEN,
	NS_SONSTIGE
)

def get_current_semester():
	today = datetime.datetime.today()
	month = today.month
	return ('WS' if month == 1 or month > 9 else 'SS') + str(today.year)[2:]
