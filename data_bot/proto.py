from datetime import datetime
import pytz

PAK_TZ = pytz.timezone('Asia/Karachi')

# Get the current timestamp in Karachi timezone
timestamp = datetime.now(PAK_TZ)

# Format the timestamp to show only hour, minute, and second components
formatted_timestamp = timestamp.strftime("%H:%M:%S")

print(formatted_timestamp)