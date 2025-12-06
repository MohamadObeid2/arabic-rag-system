pids=$(lsof -ti tcp:8000)

for p in $pids; do
    if grep -q "docker\|containerd" /proc/$p/cgroup 2>/dev/null; then
        echo "Skipping Docker-related PID $p"
        continue
    fi

    cmd=$(ps -p $p -o comm=)
    if [[ "$cmd" == *docker* ]] || [[ "$cmd" == *vpnkit* ]] || [[ "$cmd" == *containerd* ]]; then
        echo "Skipping Docker process $p ($cmd)"
        continue
    fi

    echo "Killing PID $p"
    kill $p
done

pids=$(lsof -ti tcp:9000)

for p in $pids; do
    if grep -q "docker\|containerd" /proc/$p/cgroup 2>/dev/null; then
        echo "Skipping Docker-related PID $p"
        continue
    fi

    cmd=$(ps -p $p -o comm=)
    if [[ "$cmd" == *docker* ]] || [[ "$cmd" == *vpnkit* ]] || [[ "$cmd" == *containerd* ]]; then
        echo "Skipping Docker process $p ($cmd)"
        continue
    fi

    echo "Killing PID $p"
    kill $p
done