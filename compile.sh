pyinstaller --clean --onefile \
    --workpath /tmp/KEENTUNE \
    --distpath ./bin \
    --specpath /tmp/KEENTUNE \
    --hidden-import agent.domain.sysctl \
    --hidden-import agent.domain.iperf \
    --hidden-import agent.domain.nginx \
    --hidden-import agent.domain.sysbench \
    --name target agent/agent.py