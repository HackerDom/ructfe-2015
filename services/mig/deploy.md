# Mig service deploy

1. Install libgmp-dev
2. Install redis-server
3. Configure redis persistence `save 60 1` (see https://github.com/HackerDom/ructfe-2014/blob/master/services/pidometer/env.sh)
4. Install Nim (http://nim-lang.org/download.html)
5. `nim cc -d:release main.nim`
