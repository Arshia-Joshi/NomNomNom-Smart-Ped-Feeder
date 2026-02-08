from db import log_entry, log_exit
import time

log_id = log_entry("karu")
time.sleep(2)
log_exit(log_id, 42.5)

print("DB logging works!")
