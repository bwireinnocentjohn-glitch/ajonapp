import os, glob, shutil, io

HTML = 'www/index.html'
backups = glob.glob('www/index.before*.bak.html') + glob.glob('www/index.*.bak.html')

# Pick newest backup over 700KB
best = None
best_size = 0
best_mtime = 0
for b in backups:
    try:
        sz = os.path.getsize(b)
        mt = os.path.getmtime(b)
        if sz > 700000 and mt > best_mtime:
            best = b
            best_size = sz
            best_mtime = mt
    except Exception:
        continue

if not best:
    print("ERROR: no valid backup >700KB found")
    for b in sorted(backups):
        try:
            print("  " + b + " = " + str(os.path.getsize(b)) + " bytes")
        except Exception:
            pass
    raise SystemExit(1)

print("Restoring from: " + best)
print("Size: " + str(best_size) + " bytes")
shutil.copy(best, HTML)
print("Restored. New size: " + str(os.path.getsize(HTML)) + " bytes")
