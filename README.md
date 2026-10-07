# sags-dump
ARCHIVE sags-dump.py — Package notes to a case file, including database dump.

# Target as first argument (simplest)

./sags-dump.py https://example.com 
note.txt

# With -u / --u / --url flags

./sags-dump.py -u https://example.com 
 note.txt
 
./sags-dump.py --u https://example.com  note.txt

./sags-dump.py --url https://example.com  note.txt

# With = syntax

./sags-dump.py --u=https://example.com note.txt

./sags-dump.py --url=https://example.com note.txt

# Inline note

echo "Mødenoter: alt OK" | ./sags-dump.py -u https://example.com

# From a file

./sags-dump.py -u https://example.com < noter.txt

# Multi-line heredoc

./sags-dump.py https://example.com <<'EOF'
Sag 42:
- Kunden godkendte tilbud
- Deploy på fredag
EOF

# Output of another command

tail -50 app.log | ./sags-dump.py -u https://example.com

# No note at all (prints "(ingen note)"

./sags-dump.py -u https://example.com /dev/null

# Redirect to file

./sags-dump.py -u https://example.com noter.txt > sag-2026-10-07.txt

# Timestamped archive file

./sags-dump.py -u https://example.com < noter.txt \
  > "sag-$(date -u +%Y-%m-%dT%H:%MZ).txt"

# Compressed (SQL dumps get big)
./sags-dump.py -u https://example.com < noter.txt | gzip > sag.txt.gz


  # PostgreSQL (auto-detected if pg_dump is installed)
DB_NAME=mydb DB_USER=me DB_PASSWORD=secret \
  echo "Sag afsluttet" | ./sags-dump.py -u https://example.com

# Explicit engine

DB_ENGINE=postgres DB_HOST=db.internal DB_PORT=5432 \
  DB_NAME=mydb DB_USER=me DB_PASSWORD=secret \
  echo "note" | ./sags-dump.py -u https://example.com

# MySQL

DB_ENGINE=mysql DB_HOST=localhost DB_PORT=3306 \
  DB_NAME=mydb DB_USER=root DB_PASSWORD=pw \
  echo "note" | ./sags-dump.py -u https://example.com

# .env-style file

set -a; source .env; set +a
echo "note" | ./sags-dump.py -u https://example.com

python3 sags-dump.py -u https://example.com < noter.txt

# Remember the executable bit for ./ usage

chmod +x sags-dump.py

# Daily archive at 02:00 UTC

0 2 * * * cd /opt/arkiv && \
  DB_NAME=mydb DB_USER=backup  DB_PASSWORD=xxx \
  /opt/arkiv/sags-dump.py -u https://example.com < daily-note.txt \ /var/log/arkiv/sag-(date +\%u).txt

# Archive + upload
./sags-dump.py -u https://example.com < noter.txt | curl -T - https://storage.example.com/sag.txt

# Multiple cases in one archive

for url in https://a.example https://b.example; do
  ./sags-dump.py -u "$url" < noter.txt
done > samlet-arkiv.txt


 DB_ENGINE=postgres DB_NAME=mydb DB_USER=me DB_PASSWORD=secret \
  echo "note text" | ./sags-dump.py https://example.com > sag.txt
Made In L0ve bY kArmasec 🎩
  
